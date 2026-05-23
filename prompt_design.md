# Prompt Design Documentation

## System Prompt Engineering for Closira Agent

### Overview
This document explains the prompt design strategy used to build the Closira AI agent for Bloom Aesthetics Clinic. The agent classifies customer conversations based on SOP (Standard Operating Procedure) compliance, lead qualification, and escalation requirements.

---

## 1. Classification Objectives

The agent must accomplish four key tasks:

1. **SOP Compliance Check** — Determine if the conversation adheres to clinic policies
2. **Lead Qualification** — Identify genuine prospects interested in services
3. **Escalation Detection** — Flag conversations requiring immediate human intervention
4. **Conversation Summary** — Generate concise summaries for CRM logging

---

## 2. Core Classification Categories

### ✅ IN-SCOPE
- Conversations about clinic services
- Legitimate booking/consultation inquiries
- General service information requests
- Qualified leads

**Example:** "Hi, I'd like to schedule a consultation for a hydrafacial."

### ❌ OUT-OF-SCOPE
- Medical advice requests (not aesthetic)
- Unrelated topic inquiries
- Complaints outside clinic operations
- Insurance/billing questions (redirected)

**Example:** "I have a rash on my face. What should I do?"

### 🚨 ESCALATION REQUIRED
- Allergic reactions or medical emergencies
- Equipment failures
- Client complaints or conflicts
- Serious adverse events

**Example:** "My face is getting very red and itchy all of a sudden!"

### 🎯 LEAD QUALIFIED
- Client shows genuine interest
- Willing to schedule consultation
- Within service scope
- Meets basic eligibility criteria

**Example:** "I'm interested in your anti-aging services. When can I book?"

---

## 3. SOP Rules Referenced

The agent applies the following SOP rules during classification:

| Rule ID | Category | Description |
|---------|----------|-------------|
| R1 | Service Eligibility | Only licensed professionals perform procedures |
| R2 | Client Consultation | Consultation mandatory before any procedure |
| R3 | Medical History | Clients with skin infections wait 14 days |
| R4 | Booking Policy | Cancellations require 24-hour notice |

---

## 4. Escalation Triggers

The agent immediately escalates conversations containing:
- "Medical emergency"
- "Allergic reaction"
- "Client complaint about treatment"
- "Equipment malfunction"

---

## 5. Confidence Scoring

The agent assigns a confidence score (0-1) based on:
- **Clarity of intent** — How explicit is the customer's request? (20%)
- **SOP alignment** — Does the request fit within defined scope? (40%)
- **Context completeness** — Is enough information provided? (20%)
- **Escalation certainty** — Is an escalation clearly warranted? (20%)

**Default Score:** 0.85 (high confidence for most standard inquiries)

---

## 6. Output Format

Every analysis returns:

```json
{
  "status": "in_scope|out_of_scope|escalation|lead_qualified",
  "escalation_level": "none|low|medium|critical",
  "sop_rules_applied": ["R1", "R2"],
  "summary": "Concise one-line summary",
  "action_items": ["Specific next steps"],
  "confidence_score": 0.85,
  "reasoning": "Explanation of classification"
}
```

---

## 7. Design Rationale

### Why This Prompt Design?

1. **Multi-tier Classification** — Prevents false positives by checking escalations first
2. **Keyword-based Filtering** — Fast classification without heavy language model calls
3. **SOP Integration** — External JSON file keeps rules flexible and updateable
4. **Actionable Output** — Results immediately guide next steps for staff
5. **Confidence Transparency** — Scores help prioritize manual review when needed

### Prompt Evolution

The original design could have used simple regex matching but would miss context. The current design balances:
- **Speed** (keyword triggers)
- **Accuracy** (context-aware classification)
- **Scalability** (rule-based architecture)
- **Maintainability** (external SOP configuration)

---

## 8. Testing Strategy

Test cases validate:
- ✅ Standard booking inquiries (IN-SCOPE)
- ❌ Medical advice requests (OUT-OF-SCOPE)
- 🚨 Emergency signals (ESCALATION)
- 🎯 Qualified lead indicators (LEAD_QUALIFIED)

Run tests with: `python main.py test`

---

## 9. Future Enhancements

- [ ] Integration with OpenAI GPT-4 for semantic understanding
- [ ] Named Entity Recognition (NER) to extract client info
- [ ] Sentiment analysis to detect frustrated or urgent tones
- [ ] Multi-language support
- [ ] Machine learning classifier trained on historical conversations

---

## 10. Glossary

| Term | Definition |
|------|-----------|
| SOP | Standard Operating Procedure — clinic operational rules |
| Escalation | Transfer to human staff for immediate action |
| Lead Qualification | Assessment of prospect quality/intent |
| In-Scope | Within the agent's authority and responsibility |
| Out-of-Scope | Outside agent's scope; requires redirect |
