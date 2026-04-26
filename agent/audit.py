from __future__ import annotations

import json
import os
import sqlite3
import time
import uuid
from contextlib import contextmanager
from typing import Any, Iterator, Optional

from config import settings


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    db_path = settings.audit_db
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_events (
                id TEXT PRIMARY KEY,
                ts INTEGER NOT NULL,
                run_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                action TEXT NOT NULL,
                risk_tier TEXT NOT NULL,
                allowed INTEGER NOT NULL,
                change_ticket TEXT,
                input_json TEXT,
                output_json TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                created_ts INTEGER NOT NULL,
                updated_ts INTEGER NOT NULL,
                next_run_ts INTEGER,
                status TEXT NOT NULL,
                enabled INTEGER NOT NULL,
                schedule TEXT NOT NULL,
                interval_seconds INTEGER,
                instruction TEXT NOT NULL,
                change_ticket TEXT,
                max_steps INTEGER NOT NULL,
                last_result_json TEXT
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_run_id ON audit_events(run_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status_next ON jobs(status, next_run_ts)")


def write_audit(
    *,
    run_id: str,
    event_type: str,
    action: str,
    risk_tier: str,
    allowed: bool,
    input_data: Any,
    output_data: Any,
    change_ticket: Optional[str] = None,
) -> str:
    init_db()
    event_id = str(uuid.uuid4())
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO audit_events (
                id, ts, run_id, event_type, action, risk_tier, allowed,
                change_ticket, input_json, output_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event_id,
                int(time.time()),
                run_id,
                event_type,
                action,
                risk_tier,
                1 if allowed else 0,
                change_ticket,
                json.dumps(input_data, default=str),
                json.dumps(output_data, default=str),
            ),
        )
    return event_id


def list_audit_events(limit: int = 100) -> list[dict[str, Any]]:
    init_db()
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM audit_events ORDER BY ts DESC LIMIT ?",
            (max(1, min(limit, 1000)),),
        ).fetchall()
    return [dict(row) for row in rows]


def create_job(*, instruction: str, schedule: str, interval_seconds: Optional[int], change_ticket: Optional[str], max_steps: int, enabled: bool) -> dict[str, Any]:
    init_db()
    now = int(time.time())
    job_id = str(uuid.uuid4())
    next_run_ts = now if enabled else None
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO jobs (
                id, created_ts, updated_ts, next_run_ts, status, enabled, schedule,
                interval_seconds, instruction, change_ticket, max_steps, last_result_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                job_id,
                now,
                now,
                next_run_ts,
                "queued" if enabled else "disabled",
                1 if enabled else 0,
                schedule,
                interval_seconds,
                instruction,
                change_ticket,
                max_steps,
                None,
            ),
        )
    return get_job(job_id) or {"id": job_id}


def list_jobs(limit: int = 100) -> list[dict[str, Any]]:
    init_db()
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM jobs ORDER BY created_ts DESC LIMIT ?",
            (max(1, min(limit, 1000)),),
        ).fetchall()
    return [dict(row) for row in rows]


def get_job(job_id: str) -> Optional[dict[str, Any]]:
    init_db()
    with connect() as conn:
        row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    return dict(row) if row else None


def claim_due_job() -> Optional[dict[str, Any]]:
    init_db()
    now = int(time.time())
    with connect() as conn:
        row = conn.execute(
            """
            SELECT * FROM jobs
            WHERE enabled = 1 AND next_run_ts IS NOT NULL AND next_run_ts <= ?
              AND status IN ('queued', 'scheduled')
            ORDER BY next_run_ts ASC
            LIMIT 1
            """,
            (now,),
        ).fetchone()
        if not row:
            return None
        job = dict(row)
        conn.execute(
            "UPDATE jobs SET status = ?, updated_ts = ? WHERE id = ?",
            ("running", now, job["id"]),
        )
    return job


def complete_job(job_id: str, result: Any, schedule: str, interval_seconds: Optional[int]) -> None:
    init_db()
    now = int(time.time())
    if schedule == "interval" and interval_seconds:
        next_run_ts = now + interval_seconds
        status = "scheduled"
    else:
        next_run_ts = None
        status = "completed"

    with connect() as conn:
        conn.execute(
            """
            UPDATE jobs
            SET status = ?, updated_ts = ?, next_run_ts = ?, last_result_json = ?
            WHERE id = ?
            """,
            (status, now, next_run_ts, json.dumps(result, default=str), job_id),
        )


def fail_job(job_id: str, result: Any) -> None:
    init_db()
    now = int(time.time())
    with connect() as conn:
        conn.execute(
            """
            UPDATE jobs
            SET status = ?, updated_ts = ?, next_run_ts = NULL, last_result_json = ?
            WHERE id = ?
            """,
            ("failed", now, json.dumps(result, default=str), job_id),
        )


def update_job_enabled(job_id: str, enabled: bool) -> Optional[dict[str, Any]]:
    init_db()
    now = int(time.time())
    with connect() as conn:
        conn.execute(
            """
            UPDATE jobs
            SET enabled = ?, status = ?, updated_ts = ?, next_run_ts = ?
            WHERE id = ?
            """,
            (1 if enabled else 0, "queued" if enabled else "disabled", now, now if enabled else None, job_id),
        )
    return get_job(job_id)
