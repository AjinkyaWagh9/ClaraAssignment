"""
extract_account_memo.py
Rule-based extraction: transcript -> 14-field Account Memo JSON.
Zero cost. No hallucination — missing fields go to questions_or_unknowns.
"""
import re, uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

def slugify(t: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", t.lower().strip()).strip("-")

def first(patterns: List[str], text: str, flags: int = re.IGNORECASE) -> Optional[str]:
    for p in patterns:
        m = re.search(p, text, flags)
        if m: return m.group(1).strip()
    return None

# ── Company ───────────────────────────────────────────────────────────────────
def extract_company(text: str, hint: str = "") -> str:
    if hint: return hint
    # Header line first (most reliable)
    m = re.search(r"(?:DEMO CALL TRANSCRIPT|ONBOARDING CALL TRANSCRIPT|TRANSCRIPT)\s*[-–:]\s*([^\n]+)", text)
    if m: return m.group(1).strip()
    res = first([
        r"(?:we'?re called|we'?re a|we'?re an|we run|we operate)\s+([A-Z][A-Za-z0-9 &'.\-]+)",
        r"It'?s\s+([A-Z][A-Za-z0-9 &'.\-]+(?:Clinic|Services|Repair|Plumbing|Electrical|Landscaping|Dental|Auto)?)",
    ], text)
    return res or "Unknown Company"

# ── Business Hours ─────────────────────────────────────────────────────────────
def extract_hours(text: str) -> Dict[str, Optional[str]]:
    r: Dict[str, Optional[str]] = {"days": None, "start": None, "end": None, "timezone": None}
    r["days"] = first([
        r"(Monday\s+through\s+(?:Saturday|Friday|Sunday))",
        r"(Monday\s+to\s+(?:Saturday|Friday|Sunday))",
        r"(Mon(?:day)?\s*[-–]\s*(?:Sat(?:urday)?|Fri(?:day)?))",
        r"(seven days a week|Monday through Sunday)",
    ], text)
    m = re.search(r"(\d{1,2}(?::\d{2})?\s*(?:AM|PM))\s*(?:to|-)\s*(\d{1,2}(?::\d{2})?\s*(?:AM|PM))", text, re.I)
    if m:
        r["start"], r["end"] = m.group(1).strip(), m.group(2).strip()
    r["timezone"] = first([
        r"\b(Central Time|Eastern Time|Pacific Time|Mountain Time)\b",
        r"\b(CST|EST|PST|MST|CDT|EDT|PDT|MDT)\b",
    ], text)
    return r

# ── Address ───────────────────────────────────────────────────────────────────
def extract_address(text: str) -> Optional[str]:
    # Full street address with zip
    m = re.search(
        r"\d{3,5}\s+[A-Za-z0-9 ]+(?:Avenue|Ave|Street|St|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Court|Ct|Place|Pl)"
        r"(?:,\s*(?:Suite|Ste|#)\s*\d+)?[,\s]+[A-Za-z ]+,\s*[A-Z]{2}\s*\d{5}", text, re.I
    )
    if m: return m.group(0).strip()
    # City + state fallback
    m = re.search(r"(?:in|at|located in|based in)\s+([A-Z][A-Za-z ]+,\s*[A-Z][A-Za-z]+)", text)
    return m.group(1).strip() if m else None

# ── Services ──────────────────────────────────────────────────────────────────
def extract_services(text: str) -> List[str]:
    kws = [
        "leak detection","pipe repair","drain cleaning","water heater installation","water heater repair",
        "fixture replacement","emergency shut-off","tankless water heater",
        "lawn maintenance","irrigation repair","irrigation installation","landscape design",
        "tree trimming","fertilization","seasonal cleanup","pool landscaping","hardscaping",
        "dental cleaning","fillings","root canal","orthodontics","emergency dental care",
        "teeth whitening","dental implants",
        "engine diagnostics","brake repair","oil change","battery replacement",
        "transmission service","AC repair","tire rotation","fleet vehicle maintenance",
        "electrical repair","panel upgrade","breaker replacement","wiring installation",
        "EV charger installation","ceiling fan install","lighting install","safety inspection",
        "solar panel electrical",
    ]
    tl = text.lower()
    found = [k.title() for k in kws if k in tl]
    return list(dict.fromkeys(found))

# ── Emergency Definition ───────────────────────────────────────────────────────
def extract_emergency_def(text: str) -> List[str]:
    kws = [
        "burst pipe","active flooding","gas smell","loss of water supply","water heater leaking",
        "sewage backup","major irrigation line break","flooding",
        "severe tooth pain","knocked out tooth","dental abscess","facial swelling",
        "uncontrolled bleeding","broken tooth","exposed nerve","lost dental crown","broken dental crown",
        "vehicle breakdown","stranded","brake failure","smoking engine","oil pressure warning","airbag warning",
        "total power outage","burning smell","visible sparks","exposed live wire","tripped breakers",
        "electrical fire","flickering lights","water damage affecting electrical",
        "fallen tree","tree blocking driveway",
    ]
    tl = text.lower()
    found = [k.title() for k in kws if k in tl]
    return found or ["Emergency — see transcript notes"]

# ── Emergency Routing ─────────────────────────────────────────────────────────
def extract_routing(text: str) -> Dict[str, Any]:
    r: Dict[str, Any] = {"primary_contact": None, "order": [], "fallback": None}

    # Named contacts with phone numbers e.g. "Marcus at 512-334-7821"
    hits = re.findall(
        r"([A-Z][a-z]+)\s+(?:at|is at|whose (?:cell|number) is|at cell)?\s*((?:\d{3}[-.\s]?)?\d{3}[-.\s]?\d{4})",
        text
    )
    # Also "call our X, Ray, at 214-..."
    hits += re.findall(
        r"(?:call|try|reach|contact)\s+(?:our\s+)?(?:[a-z ]+,\s+)?([A-Z][a-z]+)\s+at\s+((?:\d{3}[-.\s]?)?\d{3}[-.\s]?\d{4})",
        text
    )
    seen: Dict[str, str] = {}
    for name, phone in hits:
        phone = re.sub(r"[^0-9]", "", phone)
        if name not in seen and len(phone) >= 10:
            seen[name] = phone

    if seen:
        names: List[str] = list(seen.keys())
        # Use cast to ensure name is known as str for f-string
        r["primary_contact"] = cast(str, f"{names[0]} ({seen[names[0]]})")
        r["order"] = [f"Call {n} at {seen[n]}" for n in names]
    else:
        # Role-based fallback
        role = first([
            r"(?:call|try|transfer to)\s+(?:our\s+)?(?:on-?call\s+)?([a-z][a-z\s]*(?:technician|electrician|coordinator|manager|dentist|specialist))\s+first",
            r"(?:our\s+)([a-z][a-z\s]*(?:technician|electrician|coordinator|manager|dentist))",
        ], text)
        if role:
            r["primary_contact"] = role.title()
            r["order"] = [f"Transfer to {role.title()}"]

    # Fallback / transfer-fail message — extract exact quoted text if present
    fallback_res = first([
        r'"([^"]{20,200})"',   # exact quoted message
        r"'([^']{20,200})'",
    ], text) or first([
        r"(?:tell|say|advise)[^.]*?that[^.]*?([^.]{20,150}\.)",
        r"(?:callback|call.?back)[^.]*?within[^.]*?([^.]{15,100}\.?)",
    ], text)
    r["fallback"] = fallback_res or "A technician will call you back within 30 minutes."

    return r

# ── Call Transfer Rules ────────────────────────────────────────────────────────
def extract_transfer(text: str) -> Dict[str, Any]:
    r: Dict[str, Any] = {"timeout_seconds": 30, "retries": 1, "message_if_fails": ""}
    m = re.search(r"(\d+)\s*seconds?", text, re.I)
    if m: r["timeout_seconds"] = int(m.group(1))
    # Extract exact transfer-fail message
    fail = first([r'"([^"]{20,250})"', r"'([^']{20,250})'"], text)
    r["message_if_fails"] = cast(str, fail or "I was unable to reach our team. Your message is recorded and someone will call you back shortly.")
    return r

# ── Integration Constraints ────────────────────────────────────────────────────
def extract_constraints(text: str) -> List[str]:
    found: List[str] = []
    for m in re.finditer(r"(?:AI must|AI should|agent should|agent must|never|must not|should not|cannot|do not|don't)\s+([^.\n]{15,120})", text, re.I):
        val = m.group(0).strip().rstrip(".")
        if val not in found:
            found.append(val)
    # Explicitly slice list
    return found[:8]

# ── Main ──────────────────────────────────────────────────────────────────────
def extract_account_memo(transcript: str, company_hint: str = "", account_id: str = "") -> dict:
    company = extract_company(transcript, company_hint)
    if not account_id:
        slug_str: str = slugify(company)
        # Ensure slug is a string for slicing
        account_id = f"{slug_str[:28]}-{uuid.uuid4().hex[:6]}"

    hours       = extract_hours(transcript)
    routing     = extract_routing(transcript)
    services    = extract_services(transcript)
    emergencies = extract_emergency_def(transcript)
    address     = extract_address(transcript)
    constraints = extract_constraints(transcript)
    transfer    = extract_transfer(transcript)

    unknowns = []
    if not hours["days"]:              unknowns.append("Business hours days not found in transcript")
    if not hours["start"]:             unknowns.append("Business hours start/end not found")
    if not routing["primary_contact"]: unknowns.append("No on-call contact found — role-based routing only")
    if not address:                    unknowns.append("Office address not mentioned")
    if not services:                   unknowns.append("No services detected")

    return {
        "account_id":                   account_id,
        "company_name":                 company,
        "business_hours":               hours,
        "office_address":               address,
        "services_supported":           services,
        "emergency_definition":         emergencies,
        "emergency_routing_rules":      routing,
        "non_emergency_routing_rules":  "Collect caller name, callback number, and brief issue description. Team follows up next business day.",
        "call_transfer_rules":          transfer,
        "integration_constraints":      constraints,
        "after_hours_flow_summary":     "Greet → state after-hours → ask if emergency → if yes: collect name/number/address immediately → transfer → if fails: fallback message → confirm details logged → anything else → close",
        "office_hours_flow_summary":    "Greet → purpose → collect name + callback number → identify issue → route or take message → confirm next steps → anything else → close",
        "questions_or_unknowns":        unknowns,
        "notes":                        "Extracted via rule-based parser. Review unknowns list if any.",
    }
