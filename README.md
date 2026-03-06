
I have a Python automation pipeline project in this folder called Clara AI.
It processes voice call transcripts and generates Retell AI agent configurations.

Please do the following in order:

1. Read README.md to understand the full project structure.

2. Check that Python 3 is installed on this machine by running:
   python3 --version
   If not installed, install it.

3. Install the required Python packages:
   pip3 install gspread google-auth requests

4. Copy .env.example to .env:
   cp .env.example .env

5. Run the pipeline locally to verify it works:
   python3 scripts/run_pipeline.py
   
   Expected output: "5 accounts processed | 0 errors"
   If there are errors, read them carefully and fix them.

6. Start Docker (make sure Docker Desktop is running first), then build
   and start the n8n container:
   docker-compose up -d --build
   
   This takes 2-3 minutes on first run — wait for it to complete.

7. Verify the container is running:
   docker ps | grep clara-n8n
   
   Then verify Python3 is available inside the container:
   docker exec clara-n8n python3 --version

8. Open http://localhost:5678 in the browser.
   Login: admin / clara2026
   Import the workflow file: workflows/clara_pipeline.json
   Activate the workflow.

9. Trigger the workflow manually once and confirm it runs without errors.

10. Show me the outputs/accounts_summary.csv file contents.

Report back after each step with what happened.
```

---

## Project Overview (for the agent's context)

**What this does:**
Reads sales demo call transcripts and onboarding call transcripts,
extracts structured data (company info, hours, services, emergency
routing), generates a Retell AI voice agent configuration for each
company, and tracks changes between v1 (demo) and v2 (onboarding).

**Stack:**
- Python 3 — core pipeline (no external AI API needed)
- Docker + n8n — automation and scheduling
- Retell AI — voice agent platform (free tier)
- Google Sheets — output storage (optional)

**Key files the agent should know about:**

| File | Purpose |
|---|---|
| `scripts/run_pipeline.py` | Main entry point — run this |
| `scripts/extract_account_memo.py` | Extracts 14 fields from transcripts |
| `scripts/generate_agent_spec.py` | Builds Retell voice agent config |
| `scripts/diff_engine.py` | Compares v1 and v2, writes changelog |
| `scripts/retell_client.py` | Calls Retell API (needs API key) |
| `scripts/google_sheets_logger.py` | Logs to Google Sheets (needs key) |
| `docker-compose.yml` | Starts n8n with Python3 baked in |
| `Dockerfile` | Custom n8n image with Python3 installed |
| `workflows/clara_pipeline.json` | Import this into n8n |
| `.env.example` | Copy to `.env`, add optional keys |

---

## What the Agent Should NOT Do

- Do not modify any files inside `scripts/` unless explicitly asked
- Do not delete anything inside `outputs/` or `changelog/`
- Do not commit `.env` to git — it contains API keys
- Do not add the `credentials/` folder to git
- Do not change `docker-compose.yml` port from 5678 — n8n uses it

---

## Expected Outputs After a Successful Run

```
outputs/
└── accounts/
    ├── rapidfix-plumbing-xxxxx/
    │   ├── v1/
    │   │   ├── account_memo.json     ← extracted from demo call
    │   │   └── agent_spec.json       ← Retell agent config
    │   └── v2/
    │       ├── account_memo.json     ← updated after onboarding
    │       ├── agent_spec.json       ← updated agent config
    │       ├── changes.json          ← machine-readable diff
    │       └── changes.md            ← human-readable changelog
    ├── greenleaf-landscaping-xxxxx/
    ├── brightsmile-dental-xxxxx/
    ├── elite-auto-repair-xxxxx/
    └── safehome-electrical-xxxxx/

changelog/
├── rapidfix-plumbing-xxxxx.md
└── ... (one per account)

outputs/accounts_summary.csv          ← summary of all 5 accounts
```

---

## Troubleshooting Prompts for the Agent

If something breaks, paste the relevant prompt below into the agent:

**Docker container won't start:**
```
The docker-compose up -d --build command failed.
Read the error output carefully.
Check that Docker Desktop is running.
Check that port 5678 is not already in use by running: lsof -i :5678
Fix the issue and try again.
```

**n8n Execute Command nodes show as "?" after import:**
```
The n8n workflow has broken nodes after import.
This means N8N_ALLOW_EXEC is not set correctly.
Check docker-compose.yml has these environment variables:
  - N8N_ALLOW_EXEC=true
  - NODE_FUNCTION_ALLOW_BUILTIN=*
  - NODE_FUNCTION_ALLOW_EXTERNAL=*
  - EXECUTIONS_PROCESS=main
Restart Docker with: docker-compose down && docker-compose up -d --build
Then delete the old workflow in n8n and re-import clara_pipeline.json
```

**Python not found inside Docker container:**
```
docker exec clara-n8n python3 --version returned an error.
This means the Dockerfile did not build correctly.
Run: docker-compose down
Then run: docker-compose up -d --build --no-cache
Wait for it to fully complete, then check again.
```

**Pipeline outputs "Unknown Company" for some accounts:**
```
Read the transcript file that is failing.
The company name extractor looks for a header line like:
"DEMO CALL TRANSCRIPT - Company Name"
Check that the transcript file starts with that format.
If not, tell me what the first line looks like and I will fix the extractor.
```

**Google Sheets not receiving data:**
```
Check that credentials/google_service_account.json exists.
Check that GOOGLE_SHEET_ID is set in .env
Check that the Google Sheet is shared with the service account email
  (found inside google_service_account.json as "client_email")
Run: python3 scripts/google_sheets_logger.py to test the connection.
```

---

## Optional: Connect Retell AI

Once the pipeline runs successfully, add your Retell API key:

1. Go to retell.ai → Settings → API Keys → Copy key
2. Open `.env` and set: `RETELL_API_KEY=key_xxxxxxxx`
3. Run the pipeline again: `python3 scripts/run_pipeline.py`

The agent will now automatically create real Retell agents via API
and print the `agent_id` for each one.

---

## Optional: Connect Google Sheets

1. Go to console.cloud.google.com
2. Create a project → Enable Google Sheets API + Google Drive API
3. IAM → Service Accounts → Create → Download JSON key
4. Save as: `credentials/google_service_account.json`
5. Create a Google Sheet → Share with the service account's `client_email`
6. Copy the Sheet ID from the URL and add to `.env`:
   `GOOGLE_SHEET_ID=your_sheet_id_here`

---

## Voice Settings Reference (AiVanta Labs Guide)

The agent uses these defaults from the AiVanta Labs voice guide:

| Voice | ID | Language |
|---|---|---|
| Riya Rao (default) | `wlmwDR77ptH6bKHZui0l` | English |
| Saavi Hindi | `LWFgMHXb8m0uANBUpzlq` | Hindi / Hinglish |
| Raju | `pzxut4zZz4GImZNlqQ3H` | English Male |
| Ranga | `pzT3Axu7WJzqmpRAWYc5` | Hindi Male |

Start at **Stability 30% / Similarity 30%**.
Increase stability by 10% increments if the voice hallucinates.
Never change speed by more than ±10% — switch voices instead.
Always use a Hindi voice for Hinglish scripts.