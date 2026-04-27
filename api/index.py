from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENT_DIR = ROOT / "agent"

if str(AGENT_DIR) not in sys.path:
    sys.path.insert(0, str(AGENT_DIR))

# Vercel serverless functions do not provide a persistent /data mount.
os.environ.setdefault("AUDIT_DB", "/tmp/agent_os.db")
os.environ.setdefault("AGENT_MODE", "vercel-serverless-control-plane")

from main import app  # noqa: E402
