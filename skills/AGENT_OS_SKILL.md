---
name: agent-os-operations
description: Operate Docker, Portainer, Tailscale-private services, GitHub MCP, and audit-controlled infrastructure tasks.
---

Use this skill when a task involves infrastructure operations, Docker diagnostics, Portainer visibility, private Tailscale access, scheduled autonomous jobs, audit evidence, or policy-gated execution.

Operating principles:
1. Discover before changing.
2. Prefer read-only tools first.
3. Record every action.
4. Use change tickets for production-impacting work.
5. Keep Portainer and Agent OS private behind Tailscale.
6. Use least-privilege tokens.
7. Never bypass compliance controls; execute within pre-authorized controls.
8. Never claim execution unless a tool result confirms execution.

Default report format:
- Executive summary
- Systems inspected
- Actions taken
- Tool outputs reviewed
- Risk/compliance status
- Next recommended action
