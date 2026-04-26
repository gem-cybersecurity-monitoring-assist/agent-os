from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


READ_ONLY_ACTIONS = {
    "portainer_list_stacks",
    "portainer_list_endpoints",
    "portainer_get_stack",
    "docker_ps",
    "docker_logs",
    "shell_readonly",
    "workspace_list",
    "workspace_read_file",
}

STANDARD_ACTIONS = {
    "agent_plan",
    "agent_run",
    "generate_report",
    "run_tests",
    "create_job",
    "list_jobs",
    "list_audit_events",
}

PRODUCTION_KEYWORDS = [
    "prod",
    "production",
    "live environment",
    "customer environment",
]

DESTRUCTIVE_KEYWORDS = [
    "rm -rf",
    "docker rm",
    "docker stop",
    "docker kill",
    "docker compose down",
    "kubectl delete",
    "terraform destroy",
    "drop database",
    "truncate",
    "delete volume",
    "delete stack",
    "rotate secret",
    "rotate credential",
    "wipe",
]

RESTRICTED_KEYWORDS = [
    "deploy",
    "restart production",
    "scale production",
    "modify production",
    "external scan",
    "internet scan",
    "credential",
    "secret",
]


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    risk_tier: str
    reason: str


def _has_any(text: str, keywords: list[str]) -> bool:
    text_l = (text or "").lower()
    return any(keyword in text_l for keyword in keywords)


def classify(action: str, command: Optional[str] = None) -> str:
    command_l = (command or "").lower()
    action_l = action.lower()

    if _has_any(command_l, DESTRUCTIVE_KEYWORDS):
        return "destructive"

    if _has_any(command_l, PRODUCTION_KEYWORDS):
        return "production"

    if _has_any(command_l, RESTRICTED_KEYWORDS):
        return "restricted"

    if action_l in READ_ONLY_ACTIONS:
        return "read_only"

    if action_l in STANDARD_ACTIONS:
        return "standard"

    if "prod" in action_l or "production" in action_l:
        return "production"

    return "standard"


def evaluate(action: str, command: Optional[str] = None, change_ticket: Optional[str] = None) -> PolicyDecision:
    tier = classify(action, command)

    if tier in {"read_only", "standard"}:
        return PolicyDecision(True, tier, "Action is inside autonomous policy boundary.")

    if tier == "destructive":
        return PolicyDecision(False, tier, "Destructive action is blocked in the MVP runtime.")

    if tier in {"production", "restricted"} and change_ticket:
        return PolicyDecision(True, tier, "Restricted action allowed because a change_ticket was supplied.")

    return PolicyDecision(False, tier, "Action requires a change_ticket or is outside autonomous policy.")


def is_destructive_command(command: str) -> bool:
    return _has_any(command or "", DESTRUCTIVE_KEYWORDS)
