# Vercel Deployment

This repository is configured so Vercel can auto-detect and deploy the FastAPI control-plane entrypoint.

## What Vercel deploys

Vercel deploys the lightweight serverless control-plane API:

```text
api/index.py -> agent/main.py -> FastAPI app
```

This is suitable for:

- `/health`
- `/agent/run`
- `/tool/run` for lightweight/serverless-safe tools
- `/audit/events` using temporary `/tmp` SQLite storage
- API validation and control-plane tests

## What should remain self-hosted

The full Agent OS runtime should still be deployed on your Docker/Portainer/Tailscale host for:

- Docker socket access
- Portainer local/private operations
- persistent audit database
- scheduled background jobs
- Tailscale-private execution
- browser automation containers

Vercel is not a Docker host for this runtime.

## Vercel project settings

When importing from GitHub, select:

```text
Repository: gem-cybersecurity-monitoring-assist/agent-os
Framework Preset: Other
Build Command: python -m py_compile agent/*.py api/index.py
Output Directory: leave blank
Install Command: pip install -r requirements.txt
```

The repo includes `vercel.json`, so Vercel should route all requests to `api/index.py`.

## Required environment variables

Set in Vercel Project Settings -> Environment Variables:

```bash
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-5.5
AGENT_API_TOKEN=strong_bearer_token
AGENT_MODE=vercel-serverless-control-plane
AUDIT_DB=/tmp/agent_os.db
```

Optional if using remote Portainer API from Vercel:

```bash
PORTAINER_URL=https://portainer.your-tailnet.ts.net
PORTAINER_API_KEY=your_portainer_token
```

Recommended: keep Portainer operations self-hosted behind Tailscale instead of exposing Portainer to Vercel.

## Test after deployment

```bash
curl -s https://YOUR-VERCEL-APP.vercel.app/health | jq
```

If `AGENT_API_TOKEN` is set:

```bash
curl -s https://YOUR-VERCEL-APP.vercel.app/agent/run \
  -H "Authorization: Bearer YOUR_AGENT_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"instruction":"Return a control-plane health summary.","autonomous":false}' | jq
```

## Recommended production topology

```text
Vercel:
  public/serverless control-plane facade

Self-hosted Agent OS:
  Docker + Portainer + Tailscale + persistent jobs + audit + browser runners
```
