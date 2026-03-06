"""
run_pipeline.py — Single entry point. Processes all transcripts end-to-end.

Pipeline A: demo transcript  → account_memo v1 → agent_spec v1 → Retell agent created
Pipeline B: onboarding       → account_memo v2 → agent_spec v2 → Retell agent updated → changelog

Storage: outputs/accounts/<id>/v1/ and v2/
Summary: outputs/accounts_summary.csv + Google Sheets (if configured)

Usage:
    python scripts/run_pipeline.py
"""
import json, csv, sys, time, traceback, datetime, os
from pathlib import Path
from typing import Any, Dict, List, Tuple, cast

# Standardize path: project root for package-prefixed imports
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.ingest               import load_transcripts
from scripts.normalize_transcript import normalize
from scripts.extract_account_memo import extract_account_memo
from scripts.generate_agent_spec  import generate_agent_spec
from scripts.diff_engine          import run_diff
from scripts.retell_client        import create_agent, update_agent
from scripts.task_tracker         import upsert_task, mark_v2, print_summary

# ROOT is already defined above

OUTPUTS_DIR   = ROOT / "outputs" / "accounts"
CHANGELOG_DIR = ROOT / "changelog"
SUMMARY_PATH  = ROOT / "outputs" / "accounts_summary.csv"
INDEX_PATH    = ROOT / "outputs" / "index.json"
MAX_RETRIES   = 3

def run_with_retry(fn, *args, retries=MAX_RETRIES, label=""):
    for attempt in range(1, retries + 1):
        try:
            return fn(*args)
        except Exception as e:
            if attempt == retries:
                print(f"  [ERROR] {label} failed after {retries} attempts: {e}")
                raise
            wait = 2 ** attempt
            print(f"  [RETRY] {label} attempt {attempt} failed: {e}. Retrying in {wait}s...")
            time.sleep(wait)

def save_v1(account_id, memo, spec):
    out = OUTPUTS_DIR / account_id / "v1"
    out.mkdir(parents=True, exist_ok=True)
    (out / "account_memo.json").write_text(json.dumps(memo, indent=2))
    (out / "agent_spec.json").write_text(json.dumps(spec,  indent=2))
    return out

def write_summary_csv(rows):
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    fields = ["account_id","company_name","version","city","business_hours",
              "services_count","v1_ready","v2_ready","changes_count","unknowns","processed_at"]
    with open(SUMMARY_PATH, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

def write_summary_json(rows):
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    INDEX_PATH.write_text(json.dumps(rows, indent=2))

def run():
    print("\n" + "="*62)
    print("  CLARA AI — AUTOMATION PIPELINE")
    print("="*62 + "\n")

    # ── Ingest ────────────────────────────────────────────────────
    print("▶ Step 1: Ingesting transcripts...")
    try:
        accounts = load_transcripts()
    except FileNotFoundError as e:
        print(f"\n[ERROR] {e}")
        print("→ Place .txt files in dataset/demo_calls/ and dataset/onboarding_calls/")
        sys.exit(1)

    paired = sum(1 for a in accounts if a["onboarding_transcript"])
    print(f"\n  {len(accounts)} demo call(s) loaded | {paired} paired with onboarding\n")

    summary_rows: List[Dict[str, Any]] = []
    errors       = []

    for i, account in enumerate(accounts, 1):
        account_id = account["account_id"]
        print(f"── Account {i}/{len(accounts)}: {account['slug']} ──")

        try:
            # ── Normalize ─────────────────────────────────────────
            demo_text = normalize(account["demo_transcript"])

            # ── Extract memo v1 ───────────────────────────────────
            print("  [A] Extracting account memo...")
            from typing import cast
            memo = cast(Dict[str, Any], run_with_retry(extract_account_memo, demo_text, "", account_id, label="extract_memo"))
            company = memo["company_name"]
            print(f"      Company  : {company}")
            print(f"      Services : {len(memo['services_supported'])} detected")
            print(f"      Emergency: {len(memo['emergency_definition'])} triggers")
            if memo["questions_or_unknowns"]:
                for u in memo["questions_or_unknowns"]:
                    print(f"      ⚠ {u}")

            # ── Generate agent spec v1 ────────────────────────────
            print("  [A] Generating agent spec v1...")
            spec_v1 = run_with_retry(generate_agent_spec, memo, "v1", label="gen_spec_v1")

            # ── Save v1 ───────────────────────────────────────────
            v1_dir = save_v1(account_id, memo, spec_v1)
            print(f"  [A] ✓ Saved v1 → {v1_dir.relative_to(ROOT)}")

            # ── Retell: create agent ──────────────────────────────
            print("  [A] Creating Retell agent...")
            retell_result = cast(Dict[str, Any], run_with_retry(create_agent, spec_v1, label="retell_create"))
            retell_agent_id = retell_result.get("agent_id", "")
            # Save retell agent_id into memo for v2 update
            memo["retell_agent_id"] = retell_agent_id
            (v1_dir / "account_memo.json").write_text(json.dumps(memo, indent=2))
            print(f"      Retell agent_id: {retell_agent_id}")

            # ── Task Tracker: V1 ──────────────────────────────────
            upsert_task(
                account_id=account_id,
                company_name=company,
                status="v1_complete",
                retell_agent_id=retell_agent_id,
                services_count=len(memo["services_supported"]),
                unknowns=len(memo["questions_or_unknowns"]),
                notes=memo.get("notes", "")
            )

            v2_ready  = False
            changes_n = 0

            # ── Pipeline B ────────────────────────────────────────
            if account["onboarding_transcript"]:
                print("  [B] Processing onboarding...")
                v2_dir = OUTPUTS_DIR / account_id / "v2"

                # Explicit tuple unpacking with type assertion
                result = run_with_retry(
                    run_diff, memo, account["onboarding_transcript"], v2_dir, label="diff_engine"
                )
                if result is None:
                    raise ValueError("diff_engine returned None")
                v2_memo, v2_spec, changelog = cast(Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]], result)
                changes_n = changelog["total_changes"]
                v2_ready  = True

                # Copy changelog to /changelog/
                CHANGELOG_DIR.mkdir(exist_ok=True)
                (CHANGELOG_DIR / f"{account_id}.md").write_text(
                    (v2_dir / "changes.md").read_text()
                )

                # ── Retell: update agent ──────────────────────────
                if retell_agent_id:
                    print("  [B] Updating Retell agent to v2...")
                    run_with_retry(update_agent, retell_agent_id, v2_spec, label="retell_update")

                print(f"  [B] ✓ Saved v2 → {v2_dir.relative_to(ROOT)}")
                print(f"  [B] ✓ Changelog: {changes_n} field(s) changed")

                # ── Task Tracker: V2 ──────────────────────────────
                mark_v2(account_id, changes_n)
            else:
                print("  [B] ⚠ No onboarding transcript — v2 skipped")

            # ── Summary row ───────────────────────────────────────
            bh = memo.get("business_hours", {})
            summary_rows.append({
                "account_id":    account_id,
                "company_name":  company,
                "version":       "v2" if v2_ready else "v1",
                "city":          memo.get("office_address") or "Unknown",
                "business_hours": f"{bh.get('days','')} {bh.get('start','')}–{bh.get('end','')} {bh.get('timezone','')}".strip(),
                "services_count": len(memo["services_supported"]),
                "v1_ready":      "yes",
                "v2_ready":      "yes" if v2_ready else "no",
                "changes_count": changes_n,
                "unknowns":      len(memo["questions_or_unknowns"]),
                "processed_at":  datetime.datetime.now(datetime.timezone.utc).isoformat(),
            })

        except Exception as e:
            print(f"  [FAILED] {e}")
            traceback.print_exc()
            errors.append({"account_id": account_id, "error": str(e)})

        print()

    # ── Write summary CSV & JSON ──────────────────────────────────
    write_summary_csv(summary_rows)
    write_summary_json(summary_rows)

    # ── Task Tracker: Final Summary ───────────────────────────────
    print_summary()

    # ── Final report ──────────────────────────────────────────────
    print("\n" + "="*62)
    print(f"  DONE")
    print(f"  Accounts processed : {len(accounts)}")
    print(f"  v1 created         : {len(summary_rows)}")
    print(f"  v2 created         : {sum(1 for r in summary_rows if r['v2_ready'] == 'yes')}")
    print(f"  Errors             : {len(errors)}")
    print(f"  Summary CSV        : outputs/accounts_summary.csv")
    print("="*62 + "\n")

    if errors:
        print("Errors:")
        for e in errors:
            print(f"  {e['account_id']}: {e['error']}")

if __name__ == "__main__":
    run()
