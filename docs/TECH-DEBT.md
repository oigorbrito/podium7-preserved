# Technical debt and external blockers

Canonical tracker for durable unresolved work that should survive beyond one prompt or active plan.

## External blocker: software license unresolved

Status: `BLOCKED_EXTERNAL`

`docs/LICENSING-STATUS.md` records software license status as `UNKNOWN`. Development and internal validation may continue, but public/package release remains blocked until the repository owner selects and records a license and `scripts/check_release_readiness.py` passes.

Do not guess or auto-select a license.

## Historical candidate/research reconstruction

Status: `CLOSED / ARCHIVED`

The scientific corpus, decision-relevant benchmark measurements, primary publication identifiers, and the first selected structured source have been recovered sufficiently for current engineering decisions. `CANDIDATE-EVALUATION-LEDGER.md` records the outcome.

The exact old per-candidate execution ledger for Crawl4AI, Stagehand, Browser Use, Firecrawl, ScrapeGraphAI, Docling and Splink was not recoverable from the available durable evidence. This is archived rather than left as active debt because the current repository does not depend on those packages and repository-native implementations now cover the relevant active capabilities. Do not rerun the historical battery merely to reconstruct history. If a future work unit makes one of those candidates decision-critical again, evaluate the then-current version narrowly and record the result durably.

## Product debt: year-semantics challenge coverage

Status: `OPEN`

A separate challenge-oriented dataset may be useful to characterize manufacture-year versus model-year edge cases and adjacent singleton model-year records. This is not a current development blocker. Do not change resolver semantics without focused evidence and a product decision.

## Harness debt

No known harness blocker after Agent Harness V1 beyond normal documentation gardening. Add future durable items here with status and a plan link when work starts.
