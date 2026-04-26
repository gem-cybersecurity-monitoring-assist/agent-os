import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-5.5")
    agent_name: str = os.getenv("AGENT_NAME", "Agent OS")
    agent_mode: str = os.getenv("AGENT_MODE", "policy-autonomous")
    agent_base_url: str = os.getenv("AGENT_BASE_URL", "http://127.0.0.1:8080")
    workspace_dir: str = os.getenv("WORKSPACE_DIR", "/workspace")
    audit_db: str = os.getenv("AUDIT_DB", "/data/agent_os.db")
    job_poll_seconds: int = int(os.getenv("JOB_POLL_SECONDS", "5"))
    max_agent_steps: int = int(os.getenv("MAX_AGENT_STEPS", "8"))
    portainer_url: str = os.getenv("PORTAINER_URL", "").rstrip("/")
    portainer_api_key: str = os.getenv("PORTAINER_API_KEY", "")
    portainer_timeout_seconds: int = int(os.getenv("PORTAINER_TIMEOUT_SECONDS", "30"))
    default_change_ticket: str = os.getenv("DEFAULT_CHANGE_TICKET", "")
    api_token: str = os.getenv("AGENT_API_TOKEN", "")


settings = Settings()
