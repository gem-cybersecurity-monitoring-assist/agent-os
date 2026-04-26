from typing import Any, Optional
from pydantic import BaseModel, Field


class AgentRunRequest(BaseModel):
    instruction: str = Field(..., min_length=1)
    change_ticket: Optional[str] = None
    max_steps: int = Field(default=6, ge=1, le=20)
    autonomous: bool = True


class ToolRunRequest(BaseModel):
    action: str = Field(..., min_length=1)
    args: dict[str, Any] = Field(default_factory=dict)
    change_ticket: Optional[str] = None
    run_id: Optional[str] = None


class JobCreateRequest(BaseModel):
    instruction: str = Field(..., min_length=1)
    schedule: str = Field(default="once", description="once or interval")
    interval_seconds: Optional[int] = Field(default=None, ge=30)
    change_ticket: Optional[str] = None
    max_steps: int = Field(default=6, ge=1, le=20)
    enabled: bool = True


class JobUpdateRequest(BaseModel):
    enabled: Optional[bool] = None
    interval_seconds: Optional[int] = Field(default=None, ge=30)
    change_ticket: Optional[str] = None
