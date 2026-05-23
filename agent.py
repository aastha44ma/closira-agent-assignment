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
        self.client = instructor.from_openai(
            OpenAI(
                api_key=os.getenv("Gemini_API"),
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
            )
        )
        
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

        # 2. Swap the model name parameter to a production Gemini model
        response: AgentTurnResponse = self.client.chat.completions.create(
            model="gemini-2.5-flash",  
            response_model=AgentTurnResponse,
            messages=messages,
            temperature=0.0
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