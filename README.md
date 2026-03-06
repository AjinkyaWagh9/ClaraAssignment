# Clara AI — Automation Pipeline

This is a zero-cost, rule-based automation pipeline designed to process call transcripts and generate Retell-compatible agent specifications. It handles both demo calls (Pipeline A) and onboarding calls (Pipeline B) to create and refine AI voice agent configurations.

## Features

- **Automated Ingestion**: Automatically pairs demo transcripts with onboarding transcripts from the `dataset/` directory.
- **Rule-Based Extraction**: Extracts 14+ fields (Business Hours, Services, Emergency Protocols, etc.) from raw text without expensive LLM calls.
- **Retell Integration**: Programmatically creates and updates agents via the Retell AI API (with mock support if no API key is provided).
- **Task Tracking**: Local SQLite-based tracking (`outputs/tasks.db`) to monitor the status of every account processed.
- **Changelog Generation**: Automatically detects and documents changes between V1 (demo) and V2 (onboarding) specifications.
- **Type Safety**: Fully type-hinted Python scripts for robust static analysis and maintainability.

## Project Structure

```text
.
├── dataset/                # Input transcripts (demo & onboarding)
├── scripts/                # Core pipeline logic
│   ├── run_pipeline.py     # Main entry point
│   ├── ingest.py           # Dataset loading & pairing
│   ├── extract_account_memo.py # Rule-based NLP extraction
│   ├── generate_agent_spec.py  # Retell JSON builder
│   ├── retell_client.py    # API integration
│   ├── task_tracker.py     # SQLite status tracking
│   └── diff_engine.py      # V1 -> V2 comparison & merging
├── outputs/                # Generated specs, logs, and database
└── workflows/              # n8n / automation workflow exports
```

## Setup & Usage

### 1. Prerequisites
- Python 3.10+
- (Optional) Retell AI API Key

### 2. Installation
```bash
pip install -r requirements.txt
```

### 3. Running the Pipeline
Simply run the main entry point:
```bash
python3 scripts/run_pipeline.py
```

Results will be stored in `outputs/accounts/` and a summary will be generated in `outputs/accounts_summary.csv` and `outputs/index.json`.

### Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

| Variable | Required | Description |
|---|---|---|
| `RETELL_API_KEY` | Optional | From retell.ai → Settings → API Keys. Without it, pipeline runs in mock mode. |
| `GOOGLE_SHEET_ID` | Optional | From Google Sheet URL. Requires `credentials/google_service_account.json`. |

The pipeline runs fully without either key — Retell uses mock mode and storage uses local JSON files + SQLite.

## Outputs

After running the pipeline, find all outputs in `outputs/`:

```
outputs/
├── accounts_summary.csv          ← one row per account, all versions
├── index.json                    ← machine-readable run summary
├── tasks.db                      ← SQLite task tracker (one task per account)
└── accounts/
    └── <account_id>/
        ├── v1/
        │   ├── account_memo.json ← 14-field structured extraction
        │   └── agent_spec.json   ← Retell-compatible agent config + system prompt
        └── v2/
            ├── account_memo.json ← updated after onboarding
            ├── agent_spec.json   ← updated agent config
            ├── changes.json      ← machine-readable diff
            └── changes.md        ← human-readable changelog

changelog/
└── <account_id>.md               ← copy of changes.md per account
```

## Known Limitations

- Extraction is rule-based. Unusual transcript formats may miss some fields — check `questions_or_unknowns` in account_memo.json for flagged gaps.
- Voice ID selection uses the first available voice in your Retell account. Change this in `retell_client.py` if you want a specific voice.
- Google Sheets integration requires a service account JSON key file. See README for setup steps.

## What I Would Improve With Production Access

- Add Whisper transcription for audio files (currently requires text transcripts)
- Use an LLM extraction layer (Claude or GPT-4o) as a fallback for ambiguous transcripts
- Add a web dashboard to view accounts, changelogs, and diffs side-by-side
- Connect to Asana API for real task tracking
- Add idempotency by hashing transcripts — skip re-processing unchanged files
- Add Slack/email notifications when a new v2 agent goes live

## License
Proprietary / Assignment Internal
