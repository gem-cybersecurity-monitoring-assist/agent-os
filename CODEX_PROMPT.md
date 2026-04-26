# Codex / Claude Deployment Prompt

Paste this into Codex CLI or Claude Code from inside this repository.

```text
You are my autonomous platform engineer.

Mission:
Deploy and validate Agent OS from this repository.

Repository:
gem-cybersecurity-monitoring-assist/agent-os

Steps:
1. Inspect the repository structure.
2. Create `.env` from `.env.example` if missing.
3. Do not invent secrets. Leave placeholders where credentials are unavailable.
4. Run:
   - python3 -m py_compile agent/*.py
   - docker compose config
   - docker compose build
5. Start the runtime:
   - docker compose up -d
6. Validate:
   - curl -s http://127.0.0.1:8080/health | jq
   - curl -s http://127.0.0.1:8080/tool/run -H 'Content-Type: application/json' -d '{"action":"docker_ps","args":{}}' | jq
   - curl -s http://127.0.0.1:8080/audit/events?limit=10 | jq
7. Configure Tailscale private exposure only:
   - sudo tailscale serve --bg --https=8080 http://127.0.0.1:8080
8. Do not expose Portainer or Agent OS publicly.
9. Do not disable policy gates or audit logging.
10. Report deployment status, missing secrets, and exact next commands.
```
