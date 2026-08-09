# GEM Organization Repository Migration Runbook

## Purpose

Move authoritative GEM company repositories from the personal `support371` namespace into the `gem-cybersecurity-monitoring-assist` GitHub organization without losing history, weakening security boundaries, enabling live financial execution, or introducing unexpected paid infrastructure.

This runbook is the organization-side control document for the migration. It is intentionally fail-closed: ownership transfer, production deployment, credential rotation, provider activation, database migration, and live financial capability are separate gates.

## Non-negotiable controls

1. No secrets, private keys, seed phrases, KYC/KYB documents, production database credentials, provider credentials, or signing material may be committed to Git.
2. No repository migration step may enable mainnet trading, exchange writes, withdrawals, deposits, fund movement, social publishing, provider mutation, or production deployment.
3. No paid GitHub, cloud, CI, model, runner, database, or provider capacity may be enabled implicitly. Any paid capability requires a separate owner decision.
4. Preserve Git history, tags, releases, issues, pull requests, and audit evidence when transferring canonical repositories.
5. Repositories with an organization-side name collision must be reconciled before transfer; do not overwrite or delete an existing repository blindly.
6. Deprecated forks, upstream mirrors, starter templates, and vendor documentation repositories are not migrated unless GEM-specific proprietary changes are verified.
7. All production-impacting work remains review-gated. Destructive migration operations are not authorized by this document.

## Current organization state

At audit time the organization installation exposes only:

- `gem-cybersecurity-monitoring-assist/agent-os`
- `gem-cybersecurity-monitoring-assist/My-client-portal-`

Both are currently visible as public repositories. `agent-os` describes itself as a private autonomous infrastructure control plane, so repository visibility and exposure must be reviewed before production credentials or operational authority are introduced.

## Canonical repository tiers

### P0 — migrate first

These repositories carry the highest combination of production authority, financial/security sensitivity, active development, or company-control-plane value.

| Source | Target disposition | Notes |
|---|---|---|
| `support371/gem-enterprise` | Transfer to organization; private target preferred | Canonical GEM production platform and Command Center. Highest priority. |
| `support371/crypto-signal-bot` | Transfer to organization; private target preferred | Financial-security system. Preserve paper/testnet/mainnet locks and draft release gates. |
| `support371/fintech-microservices-core` | Transfer to organization; private target preferred | Compliance/fintech infrastructure. Audit chain and governance evidence must remain intact. |
| `support371/GlobalGateway` | Transfer to organization; private target preferred | Shared gateway/infrastructure component with recent activity. |
| `support371/GEM-Assist_AI_Autonomous_Agent` | Transfer to organization; private target preferred | Company autonomous-agent IP. |
| `support371/gem-sentinel-trust` | Transfer to organization; private target preferred | Trust/security subsystem. |
| `support371/gem-fortress-shield` | Transfer to organization; private target preferred | Defensive-security subsystem. |
| `support371/asset-compass` | Transfer; retain private | Existing private asset subsystem. |
| `support371/global-foundation-forge` | Transfer; retain private | Internal/auth/foundation work. |
| `support371/My-client-portal-` | Reconcile first, then migrate canonical state | Organization already contains a repository with the same name. |

### P1 — migrate after P0 verification

- `support371/Gem-Assist`
- `support371/MymainEnterprisewebsite`
- `support371/GemAssistLive`
- `support371/It-cybersecurity-legal-assist`
- `support371/azure_devops_app`
- `support371/mcptoolkit`
- `support371/Agent-Extend`
- `support371/foundry-agent-webapp`
- `support371/foundry-whisperer`

Each P1 repository must first be checked for current ownership, active deployment references, proprietary changes, secrets/history risk, and duplication with `gem-enterprise`.

### P2 — quarantine/review before migration

- `support371/GEM-BTC-Recovery-Dashboard-`
- `support371/nexus-financial-platform`
- `support371/investment-portfolio-platform`
- `support371/Asset-Packet`
- `support371/shipping-and-mailing`
- `support371/ESIM_Managemen`

Do not represent a P2 repository as production-authoritative until its role is proven.

## Repositories not migrated by default

Do not automatically move large upstream forks, vendor source mirrors, generic starters, sample applications, or documentation mirrors such as AutoGPT, OpenAI Agents SDK mirrors, Cloudflare documentation mirrors, iTwin, Twilio SDK mirrors, generic Next.js/Astro starters, Terraform examples, or similar repositories.

Exception: migrate only after confirming material GEM-owned proprietary changes that are not preserved elsewhere.

## Special reconciliation: My-client-portal-

The organization already contains `gem-cybersecurity-monitoring-assist/My-client-portal-` while the personal `support371/My-client-portal-` has newer development history.

Required sequence:

1. Freeze destructive changes on both copies during comparison.
2. Record default-branch heads, tags, open PRs, and deployment references for both repositories.
3. Compare histories and determine which commits exist only in each copy.
4. Preserve the organization copy under a legacy name or archive strategy before any canonical-name transfer.
5. Transfer or reconstruct the newer canonical repository only after the unique history is retained.
6. Validate build, auth, client/admin routes, environment references, and deployment links after reconciliation.
7. Do not delete the legacy copy until the canonical repository has passed validation and rollback evidence exists.

## Pre-transfer security gate for every P0 repository

Before ownership transfer:

- Record repository ID, visibility, default branch, latest commit SHA, open PRs, tags/releases, and active deployment references.
- Inspect `.github/workflows`, deployment configuration, dependency manifests, secret/config examples, and infrastructure-as-code files.
- Search current tree and reachable history for committed credentials or sensitive identifiers.
- Treat previously exposed credentials as compromised and rotate/revoke them outside Git; deletion alone is insufficient.
- Confirm `.gitignore` excludes runtime secrets and local state.
- Confirm no workflow writes to production merely because ownership changes.
- Confirm external integrations are least-privileged and scoped to the intended repository/environment.
- Confirm financial repositories remain paper/testnet/fail-closed unless a separately reviewed release authorizes otherwise.
- Record rollback: original owner, repository ID, source head SHA, deployment mapping, and integration inventory.

## Transfer wave

Recommended order:

1. `gem-enterprise`
2. `crypto-signal-bot`
3. `fintech-microservices-core`
4. `GlobalGateway`
5. `GEM-Assist_AI_Autonomous_Agent`
6. `gem-sentinel-trust`
7. `gem-fortress-shield`
8. `asset-compass`
9. `global-foundation-forge`
10. `My-client-portal-` after reconciliation

Transfer one repository at a time. Complete post-transfer verification before starting the next critical repository.

## Post-transfer verification

For each transferred repository:

1. Verify repository ID continuity where GitHub transfer semantics preserve it.
2. Verify default branch and exact head SHA.
3. Verify all expected branches/tags/releases are present.
4. Verify open pull requests and issues are intact.
5. Verify GitHub App access works from the organization installation.
6. Recheck Actions/workflow permissions and any organization policy changes caused by the move.
7. Verify deployment integrations still resolve the intended repository and branch.
8. Re-authorize or rotate external integration credentials only where required, using least privilege.
9. Run non-destructive build/test/security checks.
10. Perform read-only or fail-closed application smoke tests.
11. Record evidence in a migration issue or PR before marking the repository complete.

## Organization security baseline

Apply where supported by the current GitHub plan without enabling paid features unexpectedly:

- Require strong 2FA for organization members.
- Use teams for access instead of broad individual admin grants.
- Reserve Admin for repository/organization owners who need sensitive settings authority.
- Protect the canonical branch with PR review, no force-push, no deletion, and required checks where available.
- Require CODEOWNERS review for security-sensitive paths when plan support allows.
- Enable Dependabot/security update visibility and secret scanning/push protection where available without an unapproved plan change.
- Prefer short-lived/OIDC workload identity over long-lived cloud credentials where the deployment provider supports it.
- Keep production secrets in provider secret stores or dedicated secret managers, not repository variables committed in source.
- Keep public repositories free of internal architecture, credentials, customer data, operational endpoints, or reusable attack material that does not need to be public.

## Production and financial locks

Migration does not authorize any of the following:

- merge of draft release PRs solely because ownership changed;
- production promotion;
- Cloudflare Worker production deployment;
- production D1/R2/KV mutation;
- Supabase production migration;
- mainnet exchange connectivity;
- real-order submission;
- deposits, withdrawals, transfers, or custody;
- provider account mutation;
- autonomous publishing;
- new billable agents/runners/services.

All existing fail-closed controls remain authoritative after migration.

## Evidence ledger

For each migrated repository record:

- source repository
- target repository
- repository ID
- pre-transfer head SHA
- post-transfer head SHA
- visibility before/after
- transfer date/time
- migration operator
- open PR count before/after
- tags/releases verification
- integration/deployment verification
- secret-history audit result
- credential rotations required/completed
- build/test/security result
- rollback reference
- final status: `BLOCKED`, `TRANSFERRED_UNVERIFIED`, `VERIFIED`, or `LEGACY_ARCHIVED`

## Completion definition

The repository migration programme is complete only when:

- every P0 repository is organization-owned or has an explicitly documented exception;
- all P0 organization copies pass post-transfer validation;
- the `My-client-portal-` collision is reconciled without losing unique history;
- legacy/duplicate repositories are clearly classified;
- secrets and production identities are organizationally controlled and least-privileged;
- deployment references point to the intended organization repositories;
- no migration step has silently enabled paid capacity or live financial/external-write capability;
- rollback/evidence is preserved for every critical repository.
