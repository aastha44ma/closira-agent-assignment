# Closira Agent Assignment - Bloom Aesthetics Clinic
**Project Type:** AI Agent for Customer Classification  
**Client:** Bloom Aesthetics Clinic  

---

## 📋 Project Overview

The **Closira Agent** is an intelligent classification system that analyzes customer conversations for a beauty clinic. It determines if inquiries are:
- **In-Scope** (booking/consultation)
- **Out-of-Scope** (medical advice)
- **Escalation-Required** (emergencies)
- **Lead-Qualified** (genuine prospects)

This helps clinic staff prioritize and route customer interactions efficiently while ensuring compliance with Standard Operating Procedures (SOPs).

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install openai pydantic instructor python-dotenv
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root:

```
Gemini_API
"To ensure optimal budget flexibility during the initial testing phase, I leveraged the OpenAI SDK's backwards compatibility to map our structured extraction engine directly to Google's Gemini Flash infrastructure via AI Studio. This shows how our agent framework can change underlying foundation model layers instantly with minimal disruption to the code base."
```

### 3. Run the Agent

**Interactive Mode** (chat with the agent):
```bash
python main.py
```

**Test Mode** (run predefined test cases):
```bash
python main.py test
```

---

## 📂 Project Structure

```
closira-agent-assignment/
├── data/
│   └── sop.json                    # SOP rules and escalation triggers
├── test_transcripts/
│   ├── 1_in_sop.md                # Test: In-scope booking
│   ├── 2_out_of_scope.md          # Test: Out-of-scope inquiry
│   ├── 3_escalation_trigger.md    # Test: Emergency scenario
│   ├── 4_lead_qualification.md    # Test: Qualified lead
│   └── 5_conversation_summary.md  # Test: Multi-topic conversation
├── agent.py                        # Core classification logic
├── main.py                         # Executable script
├── prompt_design.md               # System prompt documentation
├── .env                           # API key (DO NOT COMMIT)
├── .gitignore                     # Git exclusions
└── README.md                      # This file
```

---

## 🔧 How It Works

### 1. **Conversation Input**
User enters a customer message or transcript.

### 2. **SOP Engine Analysis**
- Loads rules from `data/sop.json`
- Checks for escalation triggers
- Evaluates conversation context

### 3. **Classification**
The agent assigns one of four statuses with reasoning and action items.

### 4. **Output**
Results include:
- Classification status
- Escalation level
- Applied SOP rules
- Confidence score
- Recommended next steps

---

## 📊 Classification Examples

### ✅ In-Scope Example
```
Input: "Hi, I'd like to schedule a consultation for a hydrafacial treatment."
Output: IN_SCOPE | Confidence: 95% | Action: Confirm appointment
```

### ❌ Out-of-Scope Example
```
Input: "I have a rash on my face. What should I do?"
Output: OUT_OF_SCOPE | Action: Direct to medical professional
```

### 🚨 Escalation Example
```
Input: "My face is getting very red and itchy!"
Output: ESCALATION | Level: CRITICAL | Action: Alert medical staff
```

### 🎯 Qualified Lead Example
```
Input: "I'm interested in your anti-aging services. When can I book?"
Output: LEAD_QUALIFIED | Action: Schedule consultation
```

---

## 🎓 Key SOP Rules

| ID | Rule | Impact |
|----|------|--------|
| R1 | Licensed professionals only | Eligibility checking |
| R2 | Mandatory consultation first | Booking validation |
| R3 | 14-day wait for active infections | Safety compliance |
| R4 | 24-hour cancellation notice | Scheduling enforcement |

---

## 🧪 Testing

### Run All Tests
```bash
python main.py test
```

This executes 5 predefined scenarios covering:
1. Standard booking inquiry
2. Out-of-scope medical question
3. Emergency/escalation trigger
4. Qualified lead detection
5. Multi-message conversation summary

### Manual Testing
```bash
python main.py
```

Interactively send messages and observe classifications. Type `exit` to quit.

---

## 📝 Prompt Design

See [prompt_design.md](prompt_design.md) for detailed explanation of:
- Classification logic
- SOP integration
- Confidence scoring
- Output format
- Future enhancements

---

## 🛠️ Configuration

### Modify SOP Rules
Edit `data/sop.json`:
```json
{
  "rules": [
    {"id": "R5", "category": "New Category", "description": "..."}
  ],
  "escalation_triggers": ["new trigger"]
}
```

### Change Keyword Detection
Edit keyword lists in `agent.py`:
```python
medical_keywords = ["rash", "dermatologist", "...]
lead_indicators = ["consultation", "book", "...]
```

---


---

## 📦 Dependencies

- **pydantic** — Data validation with Python type hints
- **instructor** — Structured outputs (future enhancement)
- **python-dotenv** — Environment variable management

---
Happy To contribute!!
