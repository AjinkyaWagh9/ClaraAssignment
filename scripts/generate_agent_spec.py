"""
generate_agent_spec.py
Builds Retell-compatible Agent Spec JSON from Account Memo.
System prompt follows EXACT assignment hygiene requirements:
- Business hours flow: greeting/purpose/collect name+number/route/transfer/fallback/confirm/"anything else"/close
- After hours flow: greet/purpose/confirm emergency/collect name+number+address/transfer/fallback/assure followup/"anything else"/close
- Never mention function calls
- Never ask too many questions
- Clear transfer protocol + transfer-fail protocol
Voice IDs from AiVanta Labs Customer Care Voices 2026 sheet.
"""
import json, datetime
from typing import Any, Dict, List

VOICES = {
    "english_female": {"name": "Brynne",   "voice_id": "retell-Brynne"}
}

def build_prompt(memo: Dict[str, Any]) -> str:
    co   = memo.get("company_name", "Our Company")
    bh   = memo.get("business_hours", {})
    er   = memo.get("emergency_routing_rules", {})
    ct   = memo.get("call_transfer_rules", {})
    em   = memo.get("emergency_definition", [])
    ic   = memo.get("integration_constraints", [])
    addr = memo.get("office_address", "")

    days  = bh.get("days")  or "Monday–Friday"
    start = bh.get("start") or "8:00 AM"
    end   = bh.get("end")   or "5:00 PM"
    tz    = bh.get("timezone") or ""
    fail  = ct.get("message_if_fails") or "I was unable to reach our team directly. Your information has been recorded and someone will call you back shortly."
    em_list    = "\n".join(f"  - {e}" for e in em) if em else "  - Active emergency situation"
    route_list = "\n".join(f"  {i+1}. {s}" for i,s in enumerate(er.get("order", ["Transfer to on-call contact"])))
    ic_list    = "\n".join(f"  - {c}" for c in ic) if ic else "  - None"

    return f"""## IDENTITY
You are a professional customer care representative for {co}.
{"Office address: " + addr if addr else ""}
You must never reveal that you are an AI, a bot, or an automated system.
You must never mention tools, function calls, transfers, APIs, or any backend processes to the caller.
Always refer to any technician or staff as "our team" or "one of our team members" — never use a specific name.

---

## BUSINESS HOURS
{days}, {start} to {end} {tz}.

---

## OFFICE HOURS CALL FLOW
Follow these steps in order every time:

1. GREETING
   Say: "Thank you for calling {co}! This is [your name]. How can I help you today?"

2. UNDERSTAND PURPOSE
   Listen carefully to why the caller is reaching out. Do not interrupt.

3. COLLECT NAME AND NUMBER
   Say: "Of course — may I get your name and the best number to reach you?"
   Wait for both before moving on.

4. IDENTIFY AND ROUTE
   - If the caller needs to be connected to the team: say "Please hold for just a moment" and attempt the transfer.
   - If the transfer succeeds: complete the handoff.
   - If the issue is routine and no transfer needed: take a detailed message.

5. TRANSFER-FAIL PROTOCOL
   If the transfer does not connect, say:
   "{fail}"

6. CONFIRM NEXT STEPS
   Say: "I have your name and number on file. [Relevant next step based on outcome]."

7. ANYTHING ELSE
   Say: "Is there anything else I can help you with today?"

8. CLOSE
   Say: "Thank you for calling {co}. Have a wonderful day!"

---

## AFTER HOURS CALL FLOW
Follow these steps in order every time:

1. GREETING
   Say: "Thank you for calling {co}. You've reached us outside of our regular business hours, which are {days} from {start} to {end} {tz}."

2. PURPOSE
   Say: "I want to make sure you get the right help. Are you calling about an emergency?"

3A. IF EMERGENCY — collect immediately without delay:
   - Full name
   - Best callback number
   - Service address or location
   Say: "I'm going to connect you with our on-call team right now. Please hold."
   Attempt transfer.

4A. TRANSFER ATTEMPT (EMERGENCY)
   If transfer succeeds: complete handoff.
   If transfer fails, say EXACTLY:
   "{fail}"

5A. CONFIRM DETAILS LOGGED
   Say: "I want you to know that I have your name, number, and address recorded. Our team will reach you as soon as possible."

3B. IF NON-EMERGENCY:
   Say: "Our team will be back during business hours on [next business day]. I can take a message and make sure someone reaches out to you."
   Collect: full name and callback number.
   Confirm: "Got it — I have your information and someone will call you back during business hours."

6. ANYTHING ELSE
   Say: "Is there anything else I can help you with?"

7. CLOSE
   Say: "Thank you for calling {co}. Take care!"

---

## EMERGENCY DEFINITION
The following situations are considered emergencies requiring immediate action:
{em_list}
When in doubt, treat the situation as an emergency.

---

## EMERGENCY ROUTING PROTOCOL
{route_list}
If all contacts are unreachable:
  {er.get("fallback") or fail}

---

## CALL TRANSFER PROTOCOL
- Before transferring always say: "Please hold for just a moment."
- Never explain the transfer process to the caller.
- Never say words like "transfer", "routing", "system", or "hold music" — just "please hold."
- Timeout: {ct.get("timeout_seconds", 30)} seconds before considering transfer failed.

---

## TRANSFER-FAIL PROTOCOL
If any transfer fails, say:
"{fail}"
Then confirm details are logged and assure quick follow-up.

---

## INTEGRATION CONSTRAINTS (NEVER VIOLATE)
{ic_list}

---

## GENERAL RULES
- Only collect the information needed for routing and dispatch. Do not over-question.
- Never invent information, prices, arrival times, or technician availability.
- Never make promises about specific people or response times beyond what is stated above.
- If a caller becomes upset, stay calm, empathetic, and focused on getting their details recorded.
- If unsure about anything, take a message and promise follow-up. Never guess.
""".strip()


def generate_agent_spec(memo: Dict[str, Any], version: str = "v1", voice_key: str = "english_female") -> Dict[str, Any]:
    voice = VOICES.get(voice_key, VOICES["english_female"])
    bh = memo.get("business_hours", {})
    er = memo.get("emergency_routing_rules", {})
    ct = memo.get("call_transfer_rules", {})

    return {
        "agent_name":   f"{memo.get('company_name', 'Company')} AI Agent",
        "version":      version,
        "account_id":   memo.get("account_id"),
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),

        "voice_settings": {
            # Per AiVanta Labs Voice Testing Guide:
            # Start at 30% stability / 30% similarity
            # Increase stability in 10% increments if hallucinations occur
            # Never change speed by more than ±10% — switch voice instead
            # For Hinglish scripts always use Hindi voice
            "voice_name":        voice["name"],
            "voice_id":          voice["voice_id"],
            "language":          "en-US" if "english" in voice_key else "hi-IN",
            "stability":         0.30,
            "similarity":        0.30,
            "speed_change_pct":  0,
            "tuning_note":       "Start 30/30. Raise stability by 10% increments if issues. Max speed ±10%. Use Hindi voice for Hinglish scripts.",
        },

        "system_prompt": build_prompt(memo),

        "key_variables": {
            "company_name":    memo.get("company_name"),
            "timezone":        bh.get("timezone"),
            "business_hours":  f"{bh.get('days')} {bh.get('start')}–{bh.get('end')} {bh.get('timezone', '')}".strip(),
            "office_address":  memo.get("office_address"),
            "emergency_routing": er,
        },

        "tool_invocation_placeholders": [
            "call_transfer   — internal only, never mention to caller",
            "voicemail_log   — internal only, never mention to caller",
            "crm_note_create — internal only, never mention to caller",
        ],

        "call_transfer_protocol": {
            "pre_transfer_phrase": "Please hold for just a moment.",
            "timeout_seconds":     ct.get("timeout_seconds", 30),
            "retries":             ct.get("retries", 1),
            "on_failure":          ct.get("message_if_fails"),
        },

        "fallback_protocol": {
            "no_answer":      "Take full name and callback number. Confirm callback within business hours.",
            "transfer_fails": ct.get("message_if_fails", "Your message has been recorded. Our team will follow up shortly."),
            "unknown_issue":  "Take a message and have the appropriate team member call back.",
        },

        "retell_manual_import_steps": [
            "1. Log into retell.ai → Agents → Create New Agent",
            "2. Set Agent Name from agent_name field",
            "3. Paste system_prompt into the LLM Prompt field",
            f"4. Set voice: {voice['name']} (ElevenLabs voice_id: {voice['voice_id']})",
            "5. Set ElevenLabs Stability: 30%, Similarity Boost: 30%",
            "6. Add phone transfer numbers from key_variables.emergency_routing.order",
            "7. Test with a bilingual complex script before going live",
        ],
    }
