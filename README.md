# Agent OS

Agent OS is a private autonomous infrastructure control plane for OpenAI-powered operations across Docker, Portainer, Tailscale, GitHub MCP workflows, and compliance-audited task execution.

## Architecture

```text
Prompt / API / GitHub MCP
  -> FastAPI Agent OS control plane
  -> OpenAI planning and tool loop
  -> Policy gate
  -> Portainer / Docker / workspace tools
  -> SQLite audit ledger
  -> scheduled job runner
```

## Capabilities

- OpenAI-powered agent planning endpoint
- Direct policy-gated tool execution endpoint
- Portainer API integration
- Docker runtime inspection
- Read-only shell execution in `/workspace`
- Scheduled autonomous jobs
- SQLite audit ledger
- Tailscale-private exposure model
- GitHub MCP-ready operating pattern

## Compliance model

Agent OS does not bypass controls. It executes inside predefined policy boundaries and records every agent run and tool call.

| Risk tier | Behavior |
|---|---|
| Read-only | Auto-execute |
| Standard diagnostics | Auto-execute |
| Scheduled reporting | Auto-execute |
| Production-impacting | Requires `change_ticket` |
| Destructive | Blocked in MVP |

## Quick start

```bash
cp .env.example .env
nano .env
make validate
make up
make health
```

Required `.env` values:

```bash
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-5.5
PORTAINER_URL=https://portainer.your-tailnet.ts.net
PORTAINER_API_KEY=ptr_...
```

## Tailscale private exposure

Install Tailscale:

```bash
./scripts/install-tailscale-ubuntu.sh
```

Expose Agent OS privately:

```bash
./scripts/expose-private-services.sh
```

Manual equivalent:

```bash
sudo tailscale serve --bg --https=8080 http://127.0.0.1:8080
```

Optional Portainer private exposure when Portainer is bound to localhost:

```bash
sudo tailscale serve --bg --https=9443 https://127.0.0.1:9443
```

Do not expose Portainer or Agent OS on a public interface.

## API usage

Health check:

```bash
curl -s http://127.0.0.1:8080/health | jq
```

Docker inspection:

```bash
curl -s http://127.0.0.1:8080/tool/run \
  -H 'Content-Type: application/json' \
  -d '{"action":"docker_ps","args":{}}' | jq
```

Read-only shell:

```bash
curl -s http://127.0.0.1:8080/tool/run \
  -H 'Content-Type: application/json' \
  -d '{"action":"shell_readonly","args":{"command":"ls -la","timeout":30}}' | jq
```

Portainer stacks:

```bash
curl -s http://127.0.0.1:8080/tool/run \
  -H 'Content-Type: application/json' \
  -d '{"action":"portainer_list_stacks","args":{}}' | jq
```

Run autonomous agent:

```bash
curl -s http://127.0.0.1:8080/agent/run \
  -H 'Content-Type: application/json' \
  -d '{
    "instruction":"Inspect Docker and visible Portainer stacks, then produce an operational status report.",
    "max_steps":6,
    "autonomous":true
  }' | jq
```

Create a one-time job:

```bash
curl -s http://127.0.0.1:8080/jobs \
  -H 'Content-Type: application/json' \
  -d '{"instruction":"Inspect Docker runtime health.","schedule":"once","max_steps":6}' | jq
```

View audit events:

```bash
curl -s http://127.0.0.1:8080/audit/events?limit=25 | jq
```

## GitHub MCP pattern

Use GitHub MCP for repository read/write work. Use Agent OS for infrastructure execution. Every infrastructure action should go through `/tool/run` so the policy gate and audit ledger remain authoritative.

## Production hardening roadmap

- Move SQLite to Postgres
- Add signed approval workflow for high-risk changes
- Add SSO/API token enforcement by default
- Add Prometheus metrics and centralized logs
- Split Docker socket access into a dedicated runner service
- Add Portainer stack deploy/update tools behind change-ticket policy
