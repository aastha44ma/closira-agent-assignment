import json
import os
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from anthropic import Anthropic
import instructor
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# 1. STRUCTURAL DATA SCHEMAS (Pydantic)
# ==========================================

class AgentTurnResponse(BaseModel):
    reply: str = Field(..., description="The natural language response spoken back to the customer.")
    updated_stage: str = Field(..., description="The next appropriate stage: 'FAQ', 'QUALIFICATION', or 'ESCALATED'.")
    escalate: bool = Field(..., description="Set to True ONLY if an escalation rule or an unanswerable question is triggered.")
    escalation_reason: Optional[str] = Field(None, description="Clear technical reason for human agent handoff.")
    extracted_lead_data: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Key-value details extracted from user answers (e.g., target_area, past_treatment, preferred_time)."
    )

class FinalSessionSummary(BaseModel):
    customer_intent: str = Field(..., description="Primary objective or intent of the customer.")
    key_details_collected: Dict[str, Any] = Field(..., description="Consolidated lead qualification metrics.")
    sop_gaps_identified: List[str] = Field(..., description="List of user questions/topics that were missing from the clinic SOP.")
    recommended_next_action: str = Field(..., description="Explicit hand-off instruction for the human operations team.")

# ==========================================
# 2. CORE WORKFLOW ENGINE
# ==========================================

class ClosiraAgentEngine:
    def __init__(self, sop_path: str):
        # 1. Direct the OpenAI client to redirect traffic directly to Google Gemini
        # If a GEMINI key is present (accept several common env names), use a local deterministic analyzer
        # so the app can run without external Anthropic credits or network calls.
        possible_gemini_keys = [
            "GEMINI_API_KEY",
            "GEMINI_API",
            "Gemini_API_KEY",
            "Gemini_API",
            "Gemini_APi",
            "Gemini_APi_key",
        ]
        self.gemini_key = None
        for kname in possible_gemini_keys:
            val = os.getenv(kname)
            if val:
                self.gemini_key = val
                break
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")

        if self.gemini_key:
            self.client = None
            self.use_local_analyzer = True
        else:
            # Patch the Anthropic client with instructor for deterministic JSON outputs.
            if not self.anthropic_key:
                raise ValueError("Missing ANTHROPIC_API_KEY in environment variables.")
            self.client = instructor.from_anthropic(Anthropic(api_key=self.anthropic_key))
            self.use_local_analyzer = False
        
        with open(sop_path, 'r') as f:
            self.sop = json.load(f)
            
        self.conversation_history = []
        self.current_stage = "FAQ"
        self.compiled_lead_data = {}
        self.last_reply = ""

    def process_message(self, user_input: str) -> AgentTurnResponse:
        self.conversation_history.append({"role": "user", "content": user_input})
        
        system_prompt = f"""
        You are an elite, highly precise AI Assistant for {self.sop['business_name']}.

        CLINIC KNOWLEDGEBASE (SOP):
        - Operating Hours: {self.sop['hours']}
        - Services & Rates: {json.dumps(self.sop['services'])}
        - Booking Policy: {self.sop['booking_policy']}
        - Qualification Checkpoints to ask/verify: {json.dumps(self.sop['qualification_questions'])}
        - Hard Escalation Rules: {json.dumps(self.sop['escalation_rules'])}

        STATE CONTROLLER CONTEXT:
        - Current Active Stage: {self.current_stage}
        - Current Gathered Lead Metrics: {json.dumps(self.compiled_lead_data)}

        STRICT SAFETY MANDATES:
        1. Rely ONLY on the provided Clinic Knowledgebase. If a user asks about a service, price, or policy NOT explicitly listed in the SOP, you MUST set 'escalate' to true and note the gap. Do not hallucinate.
        2. Sentiment Check: If the user displays frustration, anger, or opens a complaint, escalate immediately.
        3. PROGRESSION MANDATE: Once you have answered the user's initial questions, you MUST transition 'updated_stage' to 'QUALIFICATION' in your response and immediately ask the first checkpoint question: "What specific treatment or area are you looking to target?"
        4. VARIATION RULE: Do not repeat your previous replies. Tailor your response dynamically to the user's latest statement.
        """

        messages = [{"role": "system", "content": system_prompt}] + self.conversation_history

        # If using local analyzer (e.g., user provided GEMINI_API_KEY), bypass external API
        if self.use_local_analyzer:
            response = self._local_process(user_input)
        else:
            # Execute structured LLM extraction call via Anthropic
            response = self.client.messages.create(
                model="claude-3-5-haiku-latest",
                response_model=AgentTurnResponse,
                system=system_prompt,
                messages=self.conversation_history,
                max_tokens=700,
                temperature=0.0 # Absolute determinism
            )

        # 3. Synchronize internal engine tracking updates
        self.conversation_history.append({"role": "assistant", "content": response.reply})
        self.current_stage = response.updated_stage
        if response.extracted_lead_data:
            self.compiled_lead_data.update(response.extracted_lead_data)
            
        if response.escalate:
            self.current_stage = "ESCALATED"

        return response

    def compile_end_of_session(self) -> FinalSessionSummary:
        """
        Stage 4: Post-session evaluations.
        """
        summary_prompt = f"""
        Analyze the conversation history and extract an administrative summary report.
        Current Compiled Data State: {json.dumps(self.compiled_lead_data)}
        """
        
        summary: FinalSessionSummary = self.client.messages.create(
            model="claude-3-5-haiku-latest",
            response_model=FinalSessionSummary,
            system=summary_prompt,
            messages=[
                {"role": "user", "content": str(self.conversation_history)}
            ],
            max_tokens=700,
            temperature=0.0
        )
        return summary

    def _local_process(self, user_input: str) -> AgentTurnResponse:
        """Deterministic, rule-based fallback processor used when Gemini key present.

        This mirrors the previous simple classifier logic so the app remains usable
        without external API calls.
        """
        text = user_input.lower().strip()

        # Simple empty input handling
        if not text:
            reply = "Please tell me how I can help or which treatment you're asking about."
            if reply == self.last_reply:
                reply = "Could you share a treatment or question so I can assist?"
            self.last_reply = reply
            return AgentTurnResponse(reply=reply, updated_stage="FAQ", escalate=False, escalation_reason=None, extracted_lead_data={})

        # Escalation triggers from SOP (if any)
        escalation_rules = [r.lower() for r in self.sop.get("escalation_rules", [])]
        if any(rule in text for rule in escalation_rules):
            self.last_reply = "This looks urgent or outside our automated scope — I'm escalating to a human now."
            return AgentTurnResponse(
                reply=self.last_reply,
                updated_stage="ESCALATED",
                escalate=True,
                escalation_reason="SOP escalation rule matched",
                extracted_lead_data={}
            )

        # Sentiment check: escalate on complaints, anger, or frustration
        sentiment_indicators = ["angry", "frustrated", "upset", "not happy", "complaint", "complain", "mad", "furious"]
        if any(si in text for si in sentiment_indicators):
            self.last_reply = "I can see you're upset. I'm escalating this to a human operator for immediate assistance."
            return AgentTurnResponse(
                reply=self.last_reply,
                updated_stage="ESCALATED",
                escalate=True,
                escalation_reason="Sentiment escalation detected",
                extracted_lead_data={}
            )

        # Medical/symptom detection
        medical_keywords = ["rash", "itchy", "dermatologist", "diagnosed", "infection", "swelling", "pain"]
        if any(k in text for k in medical_keywords) and not any(b in text for b in ["consultation", "book", "schedule", "appointment"]):
            return AgentTurnResponse(
                reply="I'm not able to provide medical advice. Please consult a medical professional.",
                updated_stage="FAQ",
                escalate=False,
                escalation_reason=None,
                extracted_lead_data={}
            )

        # Opening hours / availability queries
        hours_indicators = ["opening hours", "opening hour", "hours", "open", "when are you open", "time are you open", "availability"]
        if any(h in text for h in hours_indicators):
            hours_text = self.sop.get("hours", "Monday to Saturday, 9:00 AM - 7:00 PM. Closed on Sundays.")
            reply = f"Our opening hours are {hours_text}\n\nWhat specific treatment or area are you looking to target?"
            if reply == self.last_reply:
                reply = f"We're open {hours_text}\n\nCould you share the treatment area you're interested in?"
            self.last_reply = reply
            return AgentTurnResponse(
                reply=reply,
                updated_stage="QUALIFICATION",
                escalate=False,
                escalation_reason=None,
                extracted_lead_data={}
            )

        # Pricing/service intent
        pricing_indicators = ["price", "prices", "pricing", "cost", "how much", "fee"]
        service_indicators = [s.lower() for s in self.sop.get("services", {}).keys()]
        if any(p in text for p in pricing_indicators):
            # If SOP contains service pricing, return it.
            # Find specific service mentioned
            for svc in service_indicators:
                if svc in text:
                    price = self.sop.get("services", {}).get(svc.title())
                    if price:
                        normalized_price = price.replace("Â£", "GBP ").replace("£", "GBP ").replace("Â", "")
                        reply = f"{svc.title()} — {normalized_price}. I can help you book a consultation for exact details.\n\nWhat specific treatment or area are you looking to target?"
                        if reply == self.last_reply:
                            reply = f"{svc.title()} — {normalized_price}. I can help you book a consultation for exact details.\n\nCould you tell me which area you'd like treated?"
                        self.last_reply = reply
                        return AgentTurnResponse(reply=reply, updated_stage="QUALIFICATION", escalate=False, escalation_reason=None, extracted_lead_data={"service_interest": svc})
            # Generic pricing reply
            reply = "Pricing depends on treatment details. I can help you book a consultation for an exact quote.\n\nWhat specific treatment or area are you looking to target?"
            if reply == self.last_reply:
                reply = "Pricing depends on treatment details. I can help you book a consultation for an exact quote.\n\nCould you share the area or treatment you're interested in?"
            self.last_reply = reply
            return AgentTurnResponse(reply=reply, updated_stage="QUALIFICATION", escalate=False, escalation_reason=None, extracted_lead_data={})

        # If a user asks about a service that isn't in the SOP, escalate per mandate #1
        if any(token in text for token in ["service", "treatment", "procedure", "price", "pricing", "cost", "fee"]) and not any(svc in text for svc in service_indicators):
            self.last_reply = "I'm sorry — that service or pricing information isn't listed in our clinic knowledgebase. I'm escalating this to a human for an exact answer."
            return AgentTurnResponse(
                reply=self.last_reply,
                updated_stage="ESCALATED",
                escalate=True,
                escalation_reason="Service/pricing not in SOP",
                extracted_lead_data={}
            )

        # Stage-aware follow-up handling so the conversation can continue after the first answer.
        if self.current_stage == "QUALIFICATION":
            followup_time_indicators = [
                "today",
                "tomorrow",
                "this week",
                "next week",
                "morning",
                "afternoon",
                "evening",
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
            ]
            if any(item in text for item in followup_time_indicators):
                reply = (
                    f"Great, I've noted {text}. "
                    "Have you ever had clinical aesthetic treatments before?"
                )
                if reply == self.last_reply:
                    reply = "Got it. Have you ever had clinical aesthetic treatments before?"
                self.last_reply = reply
                self.compiled_lead_data["preferred_time"] = text
                return AgentTurnResponse(
                    reply=reply,
                    updated_stage="QUALIFICATION",
                    escalate=False,
                    escalation_reason=None,
                    extracted_lead_data={"preferred_time": text}
                )

        # Lead qualification
        lead_indicators = ["consultation", "interested", "book", "schedule", "appointment", "available"]
        if any(li in text for li in lead_indicators) or any(svc in text for svc in service_indicators):
            reply = "Great — I can help you with booking and consultation options. When would you like to come in?\n\nWhat specific treatment or area are you looking to target?"
            if reply == self.last_reply:
                reply = "Great — I can help you with booking and consultation options.\n\nCould you share the treatment area you're interested in?"
            self.last_reply = reply
            return AgentTurnResponse(reply=reply, updated_stage="QUALIFICATION", escalate=False, escalation_reason=None, extracted_lead_data={"service_interest": next((svc for svc in service_indicators if svc in text), None)})

        # Default
        reply = "Happy to help. Tell me which treatment or concern you want to discuss."
        if reply == self.last_reply:
            reply = "Could you please tell me which treatment or concern you want to discuss?"
        self.last_reply = reply
        return AgentTurnResponse(reply=reply, updated_stage="FAQ", escalate=False, escalation_reason=None, extracted_lead_data={})