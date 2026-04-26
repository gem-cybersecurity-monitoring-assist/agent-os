#!/usr/bin/env bash
set -euo pipefail

if command -v tailscale >/dev/null 2>&1; then
  echo "Tailscale already installed"
else
  curl -fsSL https://tailscale.com/install.sh | sh
fi

echo "Run: sudo tailscale up --ssh --advertise-tags=tag:agent-host"
