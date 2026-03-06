# Clara AI — Automation Pipeline

Clara AI is a zero-cost, rule-based automation pipeline designed to process call transcripts and generate Retell-compatible agent specifications. It handles both demo calls (Pipeline A) and onboarding calls (Pipeline B) to create and refine AI voice agent configurations.

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
pip install -r requirements.txt  # If requirements.txt is provided, otherwise standard lib is mostly used
```

### 3. Running the Pipeline
Simply run the main entry point:
```bash
python3 scripts/run_pipeline.py
```

Results will be stored in `outputs/accounts/` and a summary will be generated in `outputs/accounts_summary.csv` and `outputs/index.json`.

## Technical Details

- **Path Resolution**: The scripts use a standardized project-root resolution mechanism to handle package-prefixed imports (`scripts.xxxx`).
- **Mock Mode**: If `RETELL_API_KEY` is not set in the environment, the system gracefully switches to mock mode, writing simulated responses to disk.
- **Persistence**: `task_tracker.py` ensures that re-running the pipeline updates existing records rather than duplicating them.

## License
Proprietary / Assignment Internal