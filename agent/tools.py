from __future__ import annotations

from typing import Any, Callable

from docker_runner import docker_logs, docker_ps, shell_readonly, workspace_list, workspace_read_file
from portainer_client import PortainerClient


def portainer_list_stacks(_: dict[str, Any]) -> dict[str, Any]:
    return {"stacks": PortainerClient().list_stacks()}


def portainer_list_endpoints(_: dict[str, Any]) -> dict[str, Any]:
    return {"endpoints": PortainerClient().list_endpoints()}


def portainer_get_stack(args: dict[str, Any]) -> dict[str, Any]:
    return {"stack": PortainerClient().get_stack(int(args["stack_id"]))}


def _docker_ps(_: dict[str, Any]) -> dict[str, Any]:
    return docker_ps()


def _docker_logs(args: dict[str, Any]) -> dict[str, Any]:
    return docker_logs(str(args["container"]), int(args.get("lines", 100)))


def _shell_readonly(args: dict[str, Any]) -> dict[str, Any]:
    return shell_readonly(str(args["command"]), int(args.get("timeout", 60)))


def _workspace_list(args: dict[str, Any]) -> dict[str, Any]:
    return workspace_list(str(args.get("path", ".")))


def _workspace_read_file(args: dict[str, Any]) -> dict[str, Any]:
    return workspace_read_file(str(args["path"]), int(args.get("max_bytes", 12000)))


TOOL_REGISTRY: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "portainer_list_stacks": portainer_list_stacks,
    "portainer_list_endpoints": portainer_list_endpoints,
    "portainer_get_stack": portainer_get_stack,
    "docker_ps": _docker_ps,
    "docker_logs": _docker_logs,
    "shell_readonly": _shell_readonly,
    "workspace_list": _workspace_list,
    "workspace_read_file": _workspace_read_file,
}


OPENAI_TOOL_SCHEMAS: list[dict[str, Any]] = [
    {
        "type": "function",
        "name": "portainer_list_stacks",
        "description": "List Portainer stacks visible to the configured agent-bot token.",
        "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "type": "function",
        "name": "portainer_list_endpoints",
        "description": "List Portainer environments/endpoints visible to the configured agent-bot token.",
        "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "type": "function",
        "name": "portainer_get_stack",
        "description": "Get a Portainer stack by stack ID.",
        "parameters": {
            "type": "object",
            "properties": {"stack_id": {"type": "integer"}},
            "required": ["stack_id"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "docker_ps",
        "description": "List running Docker containers on the local host.",
        "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "type": "function",
        "name": "docker_logs",
        "description": "Fetch recent logs from a named Docker container.",
        "parameters": {
            "type": "object",
            "properties": {
                "container": {"type": "string"},
                "lines": {"type": "integer", "minimum": 1, "maximum": 2000},
            },
            "required": ["container"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "shell_readonly",
        "description": "Run an allowlisted read-only shell command inside the workspace.",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {"type": "string"},
                "timeout": {"type": "integer", "minimum": 1, "maximum": 300},
            },
            "required": ["command"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "workspace_list",
        "description": "List files under the mounted workspace.",
        "parameters": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "workspace_read_file",
        "description": "Read a text file under the mounted workspace.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "max_bytes": {"type": "integer", "minimum": 1, "maximum": 50000},
            },
            "required": ["path"],
            "additionalProperties": False,
        },
    },
]
