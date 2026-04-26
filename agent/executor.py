from __future__ import annotations

import uuid
from typing import Any, Optional

from audit import write_audit
from policy import evaluate
from tools import TOOL_REGISTRY


def execute_tool(
    *,
    action: str,
    args: dict[str, Any] | None = None,
    change_ticket: Optional[str] = None,
    run_id: Optional[str] = None,
) -> dict[str, Any]:
    args = args or {}
    run_id = run_id or str(uuid.uuid4())
    command = str(args.get("command", "")) if isinstance(args, dict) else ""

    decision = evaluate(action, command=command, change_ticket=change_ticket)

    if not decision.allowed:
        output = {
            "blocked": True,
            "reason": decision.reason,
            "risk_tier": decision.risk_tier,
        }
        event_id = write_audit(
            run_id=run_id,
            event_type="tool_call",
            action=action,
            risk_tier=decision.risk_tier,
            allowed=False,
            input_data={"action": action, "args": args},
            output_data=output,
            change_ticket=change_ticket,
        )
        return {
            "run_id": run_id,
            "audit_event_id": event_id,
            "allowed": False,
            "risk_tier": decision.risk_tier,
            "output": output,
        }

    if action not in TOOL_REGISTRY:
        output = {"error": f"Unknown tool: {action}"}
        event_id = write_audit(
            run_id=run_id,
            event_type="tool_call",
            action=action,
            risk_tier="unknown",
            allowed=False,
            input_data={"action": action, "args": args},
            output_data=output,
            change_ticket=change_ticket,
        )
        return {
            "run_id": run_id,
            "audit_event_id": event_id,
            "allowed": False,
            "risk_tier": "unknown",
            "output": output,
        }

    try:
        output = TOOL_REGISTRY[action](args)
    except Exception as exc:
        output = {"error": str(exc)}

    event_id = write_audit(
        run_id=run_id,
        event_type="tool_call",
        action=action,
        risk_tier=decision.risk_tier,
        allowed=True,
        input_data={"action": action, "args": args},
        output_data=output,
        change_ticket=change_ticket,
    )

    return {
        "run_id": run_id,
        "audit_event_id": event_id,
        "allowed": True,
        "risk_tier": decision.risk_tier,
        "output": output,
    }
