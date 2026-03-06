
import json, re, datetime, sys, os
from pathlib import Path
from typing import Any, Dict, List

# Standardize path: project root for package-prefixed imports
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Local imports
from scripts.normalize_transcript import normalize
from scripts.extract_account_memo import (
    extract_hours, extract_services, extract_emergency_def,
    extract_routing, extract_constraints, extract_address, extract_transfer
)
from scripts.generate_agent_spec import generate_agent_spec

def deep_merge(base: dict, updates: dict) -> dict:
    result = base.copy()
    for k, v in updates.items():
        if isinstance(v, dict) and isinstance(result.get(k), dict):
            result[k] = deep_merge(result[k], v)
        elif isinstance(v, list) and v:
            result[k] = v
        else:
            result[k] = v
    return result

def extract_onboarding_updates(transcript: str, v1_memo: dict) -> dict:
    """Extract only changed/added fields from onboarding transcript."""
    text = normalize(transcript)
    updates: Dict[str, Any] = {}

    # Hours
    new_hours = extract_hours(text)
    old_hours = v1_memo.get("business_hours", {})
    if new_hours["days"] and new_hours["days"] != old_hours.get("days"):
        updates["business_hours"] = {**old_hours, **{k: v for k, v in new_hours.items() if v}}

    # Services — add new ones, never remove
    new_svcs = extract_services(text)
    old_svcs = v1_memo.get("services_supported", [])
    added = [s for s in new_svcs if s not in old_svcs]
    if added:
        updates["services_supported"] = old_svcs + added

    # Emergency definitions — add new, never remove
    new_em = extract_emergency_def(text)
    old_em = v1_memo.get("emergency_definition", [])
    added_em = [e for e in new_em if e not in old_em]
    if added_em:
        updates["emergency_definition"] = old_em + added_em

    # Routing — update if contact changed
    new_routing = extract_routing(text)
    old_routing = v1_memo.get("emergency_routing_rules", {})
    if new_routing["primary_contact"] and new_routing["primary_contact"] != old_routing.get("primary_contact"):
        updates["emergency_routing_rules"] = {**old_routing, **{k: v for k, v in new_routing.items() if v}}
    elif new_routing.get("order") and new_routing["order"] != old_routing.get("order"):
        updates["emergency_routing_rules"] = {**old_routing, "order": new_routing["order"]}

    # Constraints — add new, never remove
    new_ic = extract_constraints(text)
    old_ic = v1_memo.get("integration_constraints", [])
    added_ic = [c for c in new_ic if c not in old_ic]
    if added_ic:
        updates["integration_constraints"] = old_ic + added_ic

    # Transfer-fail message
    new_transfer = extract_transfer(text)
    if new_transfer.get("message_if_fails") and new_transfer["message_if_fails"] != v1_memo.get("call_transfer_rules", {}).get("message_if_fails"):
        updates["call_transfer_rules"] = {**v1_memo.get("call_transfer_rules", {}), "message_if_fails": new_transfer["message_if_fails"]}

    updates["notes"] = f"Updated via onboarding call — {datetime.date.today().isoformat()}."
    return updates

def compute_diff(v1: dict, v2: dict) -> list:
    changes = []
    for key in sorted(set(list(v1.keys()) + list(v2.keys()))):
        old, new = v1.get(key), v2.get(key)
        if json.dumps(old, sort_keys=True, default=str) != json.dumps(new, sort_keys=True, default=str):
            changes.append({"field": key, "from": old, "to": new, "reason": "Updated via onboarding call"})
    return changes

def write_changelog_json(account_id, changes, path: Path) -> dict:
    doc = {
        "account_id":    account_id,
        "version":       "v1_to_v2",
        "generated_at":  datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "total_changes": len(changes),
        "changes":       changes,
    }
    path.write_text(json.dumps(doc, indent=2))
    return doc

def write_changelog_md(account_id, company, changes, path: Path):
    lines = [
        f"# Changelog — {company}",
        f"**Account ID:** `{account_id}`",
        f"**Version:** v1 → v2",
        f"**Date:** {datetime.date.today().isoformat()}",
        f"**Total Changes:** {len(changes)}",
        "", "---", "", "## Changed Fields", "",
    ]
    for ch in changes:
        lines += [
            f"### `{ch['field']}`",
            "| | Value |",
            "|---|---|",
            f"| **Before (v1)** | `{json.dumps(ch['from'], default=str)}` |",
            f"| **After  (v2)** | `{json.dumps(ch['to'],   default=str)}` |",
            f"| **Reason**      | {ch['reason']} |",
            "",
        ]
    path.write_text("\n".join(lines))

def run_diff(v1_memo, onboarding_transcript, v2_out_dir: Path):

    updates  = extract_onboarding_updates(onboarding_transcript, v1_memo)
    v2_memo  = deep_merge(v1_memo, updates)
    v2_memo["version"] = "v2"
    v2_spec  = generate_agent_spec(v2_memo, version="v2")
    changes  = compute_diff(v1_memo, v2_memo)

    v2_out_dir.mkdir(parents=True, exist_ok=True)
    (v2_out_dir / "account_memo.json").write_text(json.dumps(v2_memo, indent=2))
    (v2_out_dir / "agent_spec.json").write_text(json.dumps(v2_spec, indent=2))
    changelog = write_changelog_json(v1_memo["account_id"], changes, v2_out_dir / "changes.json")
    write_changelog_md(v1_memo["account_id"], v1_memo["company_name"], changes, v2_out_dir / "changes.md")

    return v2_memo, v2_spec, changelog
