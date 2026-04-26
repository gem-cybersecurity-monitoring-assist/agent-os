from __future__ import annotations

import threading
import time
import traceback
from typing import Optional

from audit import claim_due_job, complete_job, fail_job, write_audit
from config import settings
from openai_agent import run_agent_task


_stop_event = threading.Event()
_worker_thread: Optional[threading.Thread] = None


def _loop() -> None:
    while not _stop_event.is_set():
        try:
            job = claim_due_job()
            if not job:
                _stop_event.wait(settings.job_poll_seconds)
                continue

            result = run_agent_task(
                instruction=job["instruction"],
                change_ticket=job.get("change_ticket"),
                max_steps=int(job.get("max_steps") or settings.max_agent_steps),
                autonomous=True,
                run_id=f"job-{job['id']}",
            )
            complete_job(
                job_id=job["id"],
                result=result,
                schedule=job["schedule"],
                interval_seconds=job.get("interval_seconds"),
            )
        except Exception as exc:
            try:
                job_id = job["id"] if "job" in locals() and job else "unknown"
                if job_id != "unknown":
                    fail_job(job_id, {"error": str(exc), "traceback": traceback.format_exc()})
                write_audit(
                    run_id=f"job-{job_id}",
                    event_type="system",
                    action="job_runner_error",
                    risk_tier="standard",
                    allowed=True,
                    input_data={},
                    output_data={"error": str(exc), "traceback": traceback.format_exc()},
                )
            except Exception:
                pass
            _stop_event.wait(settings.job_poll_seconds)


def start_job_runner() -> None:
    global _worker_thread
    if _worker_thread and _worker_thread.is_alive():
        return
    _stop_event.clear()
    _worker_thread = threading.Thread(target=_loop, name="agent-os-job-runner", daemon=True)
    _worker_thread.start()


def stop_job_runner() -> None:
    _stop_event.set()
    if _worker_thread and _worker_thread.is_alive():
        _worker_thread.join(timeout=5)
