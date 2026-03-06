# RULEBOOK.md — Clara Assignment Fix Instructions
> For the Antigravity AI Agent. Execute all rules in order. Do not skip any step.
> Run `git status` after every git operation to confirm changes.

---

## MISSION

Fix 6 critical issues in the ClaraAssignment GitHub repo that are costing points
on the assignment rubric. Implement all fixes, commit each one separately with a
clear message, and push to main.

---

## RULE 1 — Remove .env from git (CRITICAL — do this first)

The `.env` file containing a real Retell API key is publicly committed to the repo.
This is a security issue and will immediately disqualify the submission.

```bash
# Remove .env from git tracking without deleting the file
git rm --cached .env

# Confirm it is no longer tracked
git status
```

Expected: `.env` should appear under "Untracked files", NOT under "Changes to be committed".

Do NOT delete the actual `.env` file — just stop tracking it.

---

## RULE 2 — Create .gitignore

There is no `.gitignore` in the repo. Create one now to prevent accidental commits
of secrets, cache files, and system files.

Create a file named `.gitignore` in the project root with this exact content:

```
# Environment secrets — never commit
.env
.env.*
!.env.example

# macOS system files
.DS_Store
.AppleDouble
.LSOverride

# Python cache
__pycache__/
*.pyc
*.pyo
*.pyd
.Python

# SQLite database (runtime artifact)
outputs/tasks.db

# Virtual environments
venv/
.venv/
env/

# IDE
.idea/
.vscode/
*.swp
```

Then stage and commit:

```bash
git add .gitignore
git rm --cached .DS_Store 2>/dev/null || true
git commit -m "fix: add .gitignore, remove .env and .DS_Store from tracking"
git push
```

---

## RULE 3 — Create requirements.txt

The README says `pip install -r requirements.txt` but the file does not exist.
This means the reviewer cannot run the project. Create it now.

Create a file named `requirements.txt` in the project root:

```
gspread>=5.0.0
google-auth>=2.0.0
requests>=2.28.0
```

Note: The core pipeline uses only Python standard library.
These three packages are only needed for optional Google Sheets integration.
The pipeline runs without them — but the file must exist.

```bash
git add requirements.txt
git commit -m "fix: add requirements.txt so reviewers can install dependencies"
git push
```

---

## RULE 4 — Remove dead code (google_sheets_logger.py)

`scripts/google_sheets_logger.py` is no longer called by anything in the pipeline.
It is dead code that makes the `scripts/` folder look messy and confusing.

Move it out of scripts into an `extras/` folder so it is preserved but not in the
main path:

```bash
mkdir -p extras
mv scripts/google_sheets_logger.py extras/google_sheets_logger.py
```

Then update any import references. Check if it is imported anywhere:

```bash
grep -r "google_sheets_logger\|log_batch" scripts/
```

If any results appear, remove those import lines from the relevant file.
If no results appear, nothing else needs to change.

```bash
git add extras/google_sheets_logger.py
git rm scripts/google_sheets_logger.py
git commit -m "refactor: move unused google_sheets_logger to extras/"
git push
```

---

## RULE 5 — Update README.md

The current README is missing several things the assignment rubric explicitly requires.
Rewrite the README with the following sections. Keep all existing content but ADD
the missing sections below.

### 5A — Add .env.example instructions

Under the Setup section, add:

```markdown
### Environment Variables

Copy `.env.example` to `.env` and fill in your values:

\```bash
cp .env.example .env
\```

| Variable | Required | Description |
|---|---|---|
| `RETELL_API_KEY` | Optional | From retell.ai → Settings → API Keys. Without it, pipeline runs in mock mode. |
| `GOOGLE_SHEET_ID` | Optional | From Google Sheet URL. Requires `credentials/google_service_account.json`. |

The pipeline runs fully without either key — Retell uses mock mode and storage
uses local JSON files + SQLite.
```

### 5B — Add output file structure

Under a section called "Outputs", add:

```markdown
## Outputs

After running the pipeline, find all outputs in `outputs/`:

\```
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
\```
```

### 5C — Add known limitations section

```markdown
## Known Limitations

- Extraction is rule-based. Unusual transcript formats may miss some fields —
  check `questions_or_unknowns` in account_memo.json for flagged gaps.
- Voice ID selection uses the first available voice in your Retell account.
  Change this in `retell_client.py` if you want a specific voice.
- Google Sheets integration requires a service account JSON key file.
  See README for setup steps.

## What I Would Improve With Production Access

- Add Whisper transcription for audio files (currently requires text transcripts)
- Use an LLM extraction layer (Claude or GPT-4o) as a fallback for ambiguous transcripts
- Add a web dashboard to view accounts, changelogs, and diffs side-by-side
- Connect to Asana API for real task tracking
- Add idempotency by hashing transcripts — skip re-processing unchanged files
- Add Slack/email notifications when a new v2 agent goes live
```

Commit after updating:

```bash
git add README.md
git commit -m "docs: add env vars table, output structure, known limitations to README"
git push
```

---

## RULE 6 — Add .env.example

There is a `.env` file but no `.env.example`. Reviewers need to know what variables
to set without seeing the real secrets. Create `.env.example`:

```
# Copy this file to .env and fill in your values
# Never commit .env to git

# Retell AI (free tier — get from retell.ai → Settings → API Keys)
RETELL_API_KEY=

# Google Sheets (optional — see README for setup steps)
GOOGLE_SHEET_ID=
```

```bash
git add .env.example
git commit -m "docs: add .env.example so reviewers know what env vars to set"
git push
```

---

## VERIFICATION CHECKLIST

After all 6 rules are complete, run these checks:

```bash
# 1. Confirm .env is NOT tracked
git ls-files | grep "\.env$"
# Expected: no output

# 2. Confirm .gitignore exists
cat .gitignore | head -5
# Expected: shows content

# 3. Confirm requirements.txt exists
cat requirements.txt
# Expected: shows 3 packages

# 4. Confirm google_sheets_logger is out of scripts/
ls scripts/ | grep sheets
# Expected: no output

# 5. Confirm .env.example exists
cat .env.example
# Expected: shows template

# 6. Confirm all changes pushed
git log --oneline -8
# Expected: shows 5-6 recent commits

# 7. Run the pipeline one final time to confirm nothing is broken
python3 scripts/run_pipeline.py
# Expected: 5 accounts processed | 0 errors
```

---

## COMMIT MESSAGE STYLE

Use this format for all commits:
- `fix:` for bug fixes and security issues
- `docs:` for README and documentation changes
- `refactor:` for code reorganization without behavior change
- `chore:` for housekeeping (gitignore, requirements)

---

## WHAT NOT TO DO

- Do NOT modify any files inside `scripts/` except to remove the google_sheets_logger import if found
- Do NOT change `docker-compose.yml` or `Dockerfile`
- Do NOT delete the actual `.env` file from disk — only remove it from git tracking
- Do NOT rewrite `run_pipeline.py` or any extraction logic
- Do NOT add new Python dependencies beyond what is in requirements.txt
- Do NOT commit `outputs/tasks.db` — it is a runtime file