# Technical debt and external blockers

Canonical tracker for durable unresolved work that should survive beyond one prompt or active plan.

## External blocker: software license unresolved

Status: `BLOCKED_EXTERNAL`

`docs/LICENSING-STATUS.md` records software license status as `UNKNOWN`. Development and internal validation may continue, but public/package release remains blocked until the repository owner selects and records a license and `scripts/check_release_readiness.py` passes.

Do not guess or auto-select a license.

## Product debt: year-semantics challenge coverage

Status: `OPEN`

A separate challenge-oriented dataset may be useful to characterize manufacture-year versus model-year edge cases and adjacent singleton model-year records. This is not a current development blocker. Do not change resolver semantics without focused evidence and a product decision.

## Harness debt

No known harness blocker after Agent Harness V1 beyond normal documentation gardening. Add future durable items here with status and a plan link when work starts.
