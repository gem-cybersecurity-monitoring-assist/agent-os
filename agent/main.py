from __future__ import annotations

import time
import uuid
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException

from audit import create_job, get_job, init_db, list_audit_events, list_jobs, write_audit
from config import settings
from executor import execute_tool
from jobs_runner import start_job_runner, stop_job_runner
from openai_agent import run_agent_task
from schemas import AgentRunRequest, JobCreateRequest, JobUpdateRequest, ToolRunRequest

app = FastAPI(title="Agent OS", version="1.0.0")


def require_api_token(authorization: Optional[str] = Header(default=None)) -> None:
    if not settings.api_token:
        return
    expected = f"Bearer {settings.api_token}"
    if authorization != expected:
        raise HTTPException(status_code=401, detail="Invalid API token")


@app.on_event("startup")
def startup() -> None:
    init_db()
    start_job_runner()


@app.on_event("shutdown")
def shutdown() -> None:
    stop_job_runner()


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": settings.agent_name,
        "mode": settings.agent_mode,
        "model": settings.openai_model,
        "time": int(time.time()),
    }


@app.post("/agent/run", dependencies=[Depends(require_api_token)])
def run_agent(req: AgentRunRequest) -> dict:
    return run_agent_task(
        instruction=req.instruction,
        change_ticket=req.change_ticket or settings.default_change_ticket or None,
        max_steps=req.max_steps,
        autonomous=req.autonomous,
    )


@app.post("/tool/run", dependencies=[Depends(require_api_token)])
def run_tool(req: ToolRunRequest) -> dict:
    return execute_tool(
        action=req.action,
        args=req.args or {},
        change_ticket=req.change_ticket or settings.default_change_ticket or None,
        run_id=req.run_id or str(uuid.uuid4()),
    )


@app.get("/audit/events", dependencies=[Depends(require_api_token)])
def audit_events(limit: int = 100) -> dict:
    return {"events": list_audit_events(limit=limit)}


@app.post("/jobs", dependencies=[Depends(require_api_token)])
def create_agent_job(req: JobCreateRequest) -> dict:
    if req.schedule not in {"once", "interval"}:
        raise HTTPException(status_code=400, detail="schedule must be 'once' or 'interval'")
    if req.schedule == "interval" and not req.interval_seconds:
        raise HTTPException(status_code=400, detail="interval_seconds is required for interval jobs")

    job = create_job(
        instruction=req.instruction,
        schedule=req.schedule,
        interval_seconds=req.interval_seconds,
        change_ticket=req.change_ticket or settings.default_change_ticket or None,
        max_steps=req.max_steps,
        enabled=req.enabled,
    )

    write_audit(
        run_id=job["id"],
        event_type="job",
        action="job_create",
        risk_tier="standard",
        allowed=True,
        input_data=req.model_dump(),
        output_data=job,
        change_ticket=req.change_ticket,
    )
    return {"job": job}


@app.get("/jobs", dependencies=[Depends(require_api_token)])
def get_jobs(limit: int = 100) -> dict:
    return {"jobs": list_jobs(limit=limit)}


@app.get("/jobs/{job_id}", dependencies=[Depends(require_api_token)])
def get_agent_job(job_id: str) -> dict:
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job": job}


@app.patch("/jobs/{job_id}", dependencies=[Depends(require_api_token)])
def update_agent_job(job_id: str, req: JobUpdateRequest) -> dict:
    if req.enabled is None:
        raise HTTPException(status_code=400, detail="Only enabled updates are supported in MVP")

    # Local import keeps startup resilient if the audit module is extended later.
    from audit import update_job_enabled

    job = update_job_enabled(job_id, req.enabled)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job": job}
