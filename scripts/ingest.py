"""
ingest.py — Load and pair demo + onboarding transcripts.
Assigns stable account IDs. Handles missing onboarding gracefully.
"""
import re, uuid, sqlite3, datetime
from pathlib import Path
from typing import List, Dict, Optional, Any

DATASET = Path(__file__).parent.parent / "dataset"

def slugify(t: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", t.lower().strip()).strip("-")

def make_account_id(stem: str) -> str:
    base = re.sub(r"_(demo|onboarding)$", "", stem)
    slug_val: str = slugify(base)
    return f"{slug_val[:28]}-{uuid.uuid4().hex[:6]}"

def load_transcripts() -> List[Dict[str, Any]]:
    demo_dir = DATASET / "demo_calls"
    onb_dir  = DATASET / "onboarding_calls"
    if not demo_dir.exists():
        raise FileNotFoundError(f"Missing: {demo_dir}")

    accounts = []
    for demo_file in sorted(demo_dir.glob("*.txt")):
        slug = re.sub(r"_demo$", "", demo_file.stem)
        account_id = make_account_id(demo_file.stem)

        # Match onboarding by slug
        onb_file = onb_dir / f"{slug}_onboarding.txt"
        if not onb_file.exists():
            matches = list(onb_dir.glob(f"{slug}*.txt"))
            onb_file = matches[0] if matches else None

        accounts.append({
            "account_id":             account_id,
            "slug":                   slug,
            "demo_file":              str(demo_file),
            "onboarding_file":        str(onb_file) if onb_file and onb_file.exists() else None,
            "demo_transcript":        demo_file.read_text(encoding="utf-8"),
            "onboarding_transcript":  onb_file.read_text(encoding="utf-8") if onb_file and onb_file.exists() else None,
        })
        status = "✓ paired" if accounts[-1]["onboarding_transcript"] else "⚠ no onboarding"
        print(f"  Loaded: {demo_file.name} [{account_id}] {status}")
    return accounts
