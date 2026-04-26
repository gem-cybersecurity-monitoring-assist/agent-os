from __future__ import annotations

import json
import uuid
from typing import Any, Optional

from openai import OpenAI

from audit import write_audit
from config import settings
from executor import execute_tool
from tools import OPENAI_TOOL_SCHEMAS


SYSTEM_PROMPT = """
You are Agent OS, an autonomous infrastructure operations agent.

Operating model:
- Discover before changing.
- Use read-only tools first.
- Never claim a tool ran unless the tool result confirms it.
- Execute only inside the available tool boundary.
- Production-impacting or destructive changes require a change_ticket.
- Always return an executive summary, actions taken, compliance summary, and next recommended action.
""".strip()


def _client() -> OpenAI:
    return OpenAI(api_key=settings.openai_api_key)


def _missing_openai_key() -> bool:
    return not settings.openai_api_key or settings.openai_api_key == "replace_me"


def _safe_json_loads(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if not value:
        return {}
    try:
        return json.loads(value)
    except Exception:
        return {}


def _function_calls(response: Any) -> list[Any]:
    calls: list[Any] = []
    for item in getattr(response, "output", []) or []:
        item_type = getattr(item, "type", None)
        if item_type == "function_call":
            calls.append(item)
    return calls


def _output_text(response: Any) -> str:
    text = getattr(response, "output_text", None)
    if text:
        return text
    parts: list[str] = []
    for item in getattr(response, "output", []) or []:
        content = getattr(item, "content", None)
        if not content:
            continue
        for part in content:
            maybe_text = getattr(part, "text", None)
            if maybe_text:
                parts.append(maybe_text)
    return "\n".join(parts).strip()


def offline_plan(instruction: str) -> str:
    return f"""
Agent OS is configured, but OPENAI_API_KEY is not set.

Requested instruction:
{instruction}

Recommended next steps:
1. Populate .env with OPENAI_API_KEY, OPENAI_MODEL, PORTAINER_URL, and PORTAINER_API_KEY.
2. Run make up and make health.
3. Validate direct tools with make ps and make test-tool.
4. Re-run /agent/run for autonomous execution.
""".strip()


def run_agent_task(
    *,
    instruction: str,
    change_ticket: Optional[str] = None,
    max_steps: int = 6,
    autonomous: bool = True,
    run_id: Optional[str] = None,
) -> dict[str, Any]:
    run_id = run_id or str(uuid.uuid4())

    if _missing_openai_key():
        result = {
            "run_id": run_id,
            "mode": "offline-plan",
            "result": offline_plan(instruction),
            "tool_results": [],
            "compliance_summary": "No external model call was made because OPENAI_API_KEY is not configured.",
        }
        event_id = write_audit(
            run_id=run_id,
            event_type="agent_run",
            action="agent_plan",
            risk_tier="standard",
            allowed=True,
            input_data={"instruction": instruction, "max_steps": max_steps, "autonomous": autonomous},
            output_data=result,
            change_ticket=change_ticket,
        )
        result["audit_event_id"] = event_id
        return result

    client = _client()
    tool_results: list[dict[str, Any]] = []

    user_content = f"""
Instruction:
{instruction}

Change ticket:
{change_ticket or "none"}

Autonomous mode:
{autonomous}

Available tools are policy-gated. Use tool calls only for allowed operational actions.
""".strip()

    response = client.responses.create(
        model=settings.openai_model,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        tools=OPENAI_TOOL_SCHEMAS,
    )

    steps = 0
    final_text = _output_text(response)

    while autonomous and steps < max_steps:
        calls = _function_calls(response)
        if not calls:
            final_text = _output_text(response)
            break

        function_outputs: list[dict[str, Any]] = []
        for call in calls:
            action = getattr(call, "name", "")
            args = _safe_json_loads(getattr(call, "arguments", "{}"))
            call_id = getattr(call, "call_id", None)

            execution = execute_tool(
                action=action,
                args=args,
                change_ticket=change_ticket,
                run_id=run_id,
            )
            tool_results.append({"call_id": call_id, "action": action, "args": args, "execution": execution})
            function_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": json.dumps(execution, default=str),
                }
            )

        response = client.responses.create(
            model=settings.openai_model,
            previous_response_id=response.id,
            input=function_outputs,
            tools=OPENAI_TOOL_SCHEMAS,
        )
        steps += 1
        final_text = _output_text(response)

    result = {
        "run_id": run_id,
        "mode": "autonomous" if autonomous else "planner",
        "result": final_text,
        "tool_results": tool_results,
        "compliance_summary": "All executed tools passed through policy evaluation and audit logging.",
    }

    event_id = write_audit(
        run_id=run_id,
        event_type="agent_run",
        action="agent_run",
        risk_tier="standard",
        allowed=True,
        input_data={
            "instruction": instruction,
            "change_ticket": change_ticket,
            "max_steps": max_steps,
            "autonomous": autonomous,
        },
        output_data=result,
        change_ticket=change_ticket,
    )
    result["audit_event_id"] = event_id
    return result
