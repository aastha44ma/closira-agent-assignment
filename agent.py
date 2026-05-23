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
        # If a GEMINI_API_KEY is present, use a local deterministic analyzer
        # so the app can run without external Anthropic credits or network calls.
        self.gemini_key = os.getenv("GEMINI_API_KEY")
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

    def process_message(self, user_input: str) -> AgentTurnResponse:
        self.conversation_history.append({"role": "user", "content": user_input})
        
        system_prompt = f"""
        You are an elite, highly precise AI Assistant for {self.sop['business_name']}.
        ... [Keep your exact system prompt text from the previous step here] ...
        """

        messages = [{"role": "system", "content": system_prompt}] + self.conversation_history

        # If using local analyzer (e.g., user provided GEMINI_API_KEY), bypass external API
        if self.use_local_analyzer:
            return self._local_process(user_input)

        # Execute structured LLM extraction call via Anthropic
        response: AgentTurnResponse = self.client.messages.create(
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
            return AgentTurnResponse(
                reply="Please tell me how I can help or which treatment you're asking about.",
                updated_stage="FAQ",
                escalate=False,
                escalation_reason=None,
                extracted_lead_data={}
            )

        # Escalation triggers from SOP (if any)
        escalation_rules = [r.lower() for r in self.sop.get("escalation_rules", [])]
        if any(rule in text for rule in escalation_rules):
            return AgentTurnResponse(
                reply="This looks urgent or outside our automated scope — I'm escalating to a human now.",
                updated_stage="ESCALATED",
                escalate=True,
                escalation_reason="SOP escalation rule matched",
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
                        return AgentTurnResponse(
                            reply=f"{svc.title()} — {price}. I can help you book a consultation for exact details.",
                            updated_stage="QUALIFICATION",
                            escalate=False,
                            escalation_reason=None,
                            extracted_lead_data={"service_interest": svc}
                        )
            # Generic pricing reply
            return AgentTurnResponse(
                reply="Pricing depends on treatment details. I can help you book a consultation for an exact quote.",
                updated_stage="QUALIFICATION",
                escalate=False,
                escalation_reason=None,
                extracted_lead_data={}
            )

        # Lead qualification
        lead_indicators = ["consultation", "interested", "book", "schedule", "appointment", "available"]
        if any(li in text for li in lead_indicators) or any(svc in text for svc in service_indicators):
            return AgentTurnResponse(
                reply="Great — I can help you with booking and consultation options. When would you like to come in?",
                updated_stage="QUALIFICATION",
                escalate=False,
                escalation_reason=None,
                extracted_lead_data={"service_interest": next((svc for svc in service_indicators if svc in text), None)}
            )

        # Default
        return AgentTurnResponse(
            reply="Happy to help. Tell me which treatment or concern you want to discuss.",
            updated_stage="FAQ",
            escalate=False,
            escalation_reason=None,
            extracted_lead_data={}
        )
        return summary