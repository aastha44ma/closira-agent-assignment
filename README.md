# Closira Agent Assignment - Bloom Aesthetics Clinic

**Status:** ✅ Ready to Test  
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
OPENAI_API_KEY=your_api_key_here
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

## 🎬 Video Walkthrough Checklist

For your 2-5 minute presentation:

- [ ] Show the project structure in VS Code Explorer
- [ ] Display `sop.json` to show SOP rules
- [ ] Open and read a test transcript
- [ ] Run `python main.py test` to show all 5 test cases
- [ ] Demonstrate interactive mode with a custom message
- [ ] Show the Markdown Preview of `prompt_design.md`
- [ ] Explain classification logic and decision-making
- [ ] Mention the Pydantic schema benefits

---

## 📦 Dependencies

- **openai** — OpenAI API client (future enhancement)
- **pydantic** — Data validation with Python type hints
- **instructor** — Structured outputs (future enhancement)
- **python-dotenv** — Environment variable management

---

## 🔐 Security Notes

⚠️ **NEVER commit `.env` file to GitHub!**

The `.gitignore` is configured to exclude:
- `.env` (API keys)
- `__pycache__/` (compiled files)
- `.venv/` (virtual environment)

---

## 📞 Support & Next Steps

1. **Verify Setup:** Run `python main.py test` to confirm everything works
2. **Test Edge Cases:** Use interactive mode to test scenarios
3. **Review Docs:** Check `prompt_design.md` for system design explanation
4. **Record Demo:** Capture your 2-5 minute walkthrough showing all features

---

## ✨ Features Highlight

✅ Pydantic schema for type-safe outputs  
✅ Rule-based classification system  
✅ Escalation detection with severity levels  
✅ Lead qualification scoring  
✅ Conversation summarization  
✅ Confidence-based filtering  
✅ Extensible SOP configuration  
✅ Interactive testing mode  

---

**Ready to test?** Run: `python main.py test`

Good luck with your assignment! 🎉
