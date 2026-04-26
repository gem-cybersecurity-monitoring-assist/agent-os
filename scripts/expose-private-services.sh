#!/usr/bin/env bash
set -euo pipefail

if ! command -v tailscale >/dev/null 2>&1; then
  echo "tailscale is not installed" >&2
  exit 1
fi

echo "Exposing Agent OS privately on HTTPS 8080 through Tailscale Serve"
sudo tailscale serve --bg --https=8080 http://127.0.0.1:8080

cat <<'MSG'
Agent OS private exposure configured.

Optional Portainer private exposure, only if Portainer is bound to localhost:
  sudo tailscale serve --bg --https=9443 https://127.0.0.1:9443
MSG
