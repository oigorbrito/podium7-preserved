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

## Product debt: year-semantics resolver rule

Status: `CHARACTERIZED / PRODUCT_DECISION_REQUIRED`

The source-backed challenge slice in `benchmarks/catalog_identity_year_semantics_challenge_v1.json` now characterizes manufacture-year versus model-year behavior. Primary evidence establishes that Senatran stores manufacture year and model year separately, FIPE keys vehicle year to model year, and Toyota publishes the same named configuration across adjacent year/model notations.

Current resolver behavior is measured at 4/6 exact challenge labels with two ambiguous overcommits: manufacture-year-only non-overlap forces `NO_MATCH`, while missing model year can force `MATCH` even when the same named configuration exists in adjacent model years. `CATALOG-YEAR-SEMANTICS-CHALLENGE-V1.md` records the evidence and narrow policy options.

Do not change resolver semantics until the product owner chooses the intended rule. Once selected, update the resolver and convert the relevant characterization cases into regression expectations. This does not block unrelated development.

## Harness debt

No known harness blocker after Agent Harness V1 beyond normal documentation gardening. Add future durable items here with status and a plan link when work starts.
