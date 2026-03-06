
import sqlite3, datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "outputs" / "tasks.db"

def _conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(str(DB_PATH), timeout=10)
    c.execute("""CREATE TABLE IF NOT EXISTS tasks (
        account_id      TEXT PRIMARY KEY,
        task_id         TEXT,
        company_name    TEXT,
        status          TEXT DEFAULT 'pending',
        v1_created_at   TEXT,
        v2_created_at   TEXT,
        retell_agent_id TEXT,
        changes_count   INTEGER DEFAULT 0,
        services_count  INTEGER DEFAULT 0,
        unknowns        INTEGER DEFAULT 0,
        notes           TEXT,
        updated_at      TEXT
    )""")
    c.commit()
    return c

def upsert_task(account_id, company_name, status,
                retell_agent_id="", changes_count=0,
                services_count=0, unknowns=0, notes=""):
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    task_id = f"CLARA-{account_id[:12].upper()}"
    c = _conn()
    try:
        c.execute("""
            INSERT INTO tasks
              (account_id, task_id, company_name, status, v1_created_at,
               retell_agent_id, services_count, unknowns, notes, updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(account_id) DO UPDATE SET
              status=excluded.status,
              retell_agent_id=excluded.retell_agent_id,
              services_count=excluded.services_count,
              unknowns=excluded.unknowns,
              notes=excluded.notes,
              updated_at=excluded.updated_at
        """, (account_id, task_id, company_name, status, now,
              retell_agent_id, services_count, unknowns, notes, now))
        c.commit()
        print(f"  [Tasks] ✓ {task_id} — {company_name} [{status}]")
    finally:
        c.close()

def mark_v2(account_id, changes_count):
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    c = _conn()
    try:
        c.execute("""
            UPDATE tasks SET status='v2_complete', v2_created_at=?,
            changes_count=?, updated_at=? WHERE account_id=?
        """, (now, changes_count, now, account_id))
        c.commit()
    finally:
        c.close()

def print_summary():
    c = _conn()
    try:
        rows = c.execute("""
            SELECT task_id, company_name, status, services_count,
                   changes_count, retell_agent_id
            FROM tasks ORDER BY company_name
        """).fetchall()
    finally:
        c.close()
    print("\n  ┌─ TASK TRACKER ──────────────────────────────────────────────")
    for r in rows:
        agent = (r[5] or "none")[:30]
        print(f"  │ {r[0]:<26} {r[1]:<32} {r[2]:<14} svc={r[3]} Δ={r[4]}")
    print(f"  └─ {len(rows)} task(s) — outputs/tasks.db\n")
    return rows
