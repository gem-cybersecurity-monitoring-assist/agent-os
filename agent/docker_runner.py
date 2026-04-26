from __future__ import annotations

import os
import subprocess
from typing import Any

from config import settings
from policy import is_destructive_command


READONLY_PREFIXES = [
    "ls",
    "cat",
    "head",
    "tail",
    "grep",
    "find",
    "pwd",
    "whoami",
    "date",
    "git status",
    "git log",
    "pytest",
    "python -m pytest",
]


def _run(args: list[str], timeout: int = 60, cwd: str | None = None) -> dict[str, Any]:
    try:
        result = subprocess.run(args, text=True, capture_output=True, timeout=timeout, cwd=cwd)
        return {
            "returncode": result.returncode,
            "stdout": result.stdout[-20000:],
            "stderr": result.stderr[-20000:],
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "returncode": 124,
            "stdout": exc.stdout[-20000:] if isinstance(exc.stdout, str) else "",
            "stderr": f"Command timed out after {timeout} seconds",
        }
    except Exception as exc:
        return {"returncode": 1, "stdout": "", "stderr": str(exc)}


def docker_ps() -> dict[str, Any]:
    return _run(["docker", "ps", "--format", "{{json .}}"], timeout=30)


def docker_logs(container: str, lines: int = 100) -> dict[str, Any]:
    safe_lines = max(1, min(int(lines), 2000))
    return _run(["docker", "logs", "--tail", str(safe_lines), container], timeout=60)


def shell_readonly(command: str, timeout: int = 60) -> dict[str, Any]:
    command = command.strip()
    if not command:
        return {"returncode": 2, "stdout": "", "stderr": "Empty command blocked"}

    if is_destructive_command(command):
        return {"returncode": 126, "stdout": "", "stderr": "Destructive command blocked"}

    if not any(command == prefix or command.startswith(prefix + " ") for prefix in READONLY_PREFIXES):
        return {"returncode": 126, "stdout": "", "stderr": "Command blocked by readonly shell policy"}

    safe_timeout = max(1, min(int(timeout), 300))
    return _run(["sh", "-lc", command], timeout=safe_timeout, cwd=settings.workspace_dir)


def workspace_list(path: str = ".") -> dict[str, Any]:
    base = os.path.abspath(settings.workspace_dir)
    target = os.path.abspath(os.path.join(base, path))
    if not target.startswith(base):
        return {"error": "Path escapes workspace"}
    try:
        return {"path": target, "items": sorted(os.listdir(target))}
    except Exception as exc:
        return {"error": str(exc)}


def workspace_read_file(path: str, max_bytes: int = 12000) -> dict[str, Any]:
    base = os.path.abspath(settings.workspace_dir)
    target = os.path.abspath(os.path.join(base, path))
    if not target.startswith(base):
        return {"error": "Path escapes workspace"}
    try:
        with open(target, "rb") as handle:
            raw = handle.read(max(1, min(int(max_bytes), 50000)))
        return {"path": path, "content": raw.decode("utf-8", errors="replace")}
    except Exception as exc:
        return {"error": str(exc)}
