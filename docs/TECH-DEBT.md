# Technical debt and external blockers

Canonical tracker for durable unresolved work that should survive beyond one prompt or active plan.

## Release policy: private/proprietary

Status: `INTENTIONAL_PRIVATE_BLOCK`

`docs/LICENSING-STATUS.md` records software status as `PRIVATE_PROPRIETARY`. The repository is private and no public software license is granted. Development, testing and private operation may continue, while package/public release remains intentionally blocked by `scripts/check_release_readiness.py`.

A future MIT, Apache-2.0 or other distribution/open-source choice is deferred until the product is operational and requires a new explicit owner decision. Do not infer or generate a public license before then.

## Historical candidate/research reconstruction

Status: `CLOSED / ARCHIVED`

The scientific corpus, decision-relevant benchmark measurements, primary publication identifiers, and the first selected structured source have been recovered sufficiently for current engineering decisions. `CANDIDATE-EVALUATION-LEDGER.md` records the outcome.

The exact old per-candidate execution ledger for Crawl4AI, Stagehand, Browser Use, Firecrawl, ScrapeGraphAI, Docling and Splink was not recoverable from the available durable evidence. This is archived rather than left as active debt because the current repository does not depend on those packages and repository-native implementations now cover the relevant active capabilities. Do not rerun the historical battery merely to reconstruct history. If a future work unit makes one of those candidates decision-critical again, evaluate the then-current version narrowly and record the result durably.

## Product debt: year-semantics resolver rule

Status: `CLOSED / SELECTED_POLICY`

The owner selected the Senatran-aligned rule on 2026-08-23. Manufacture year and model year remain separate identity dimensions; explicit non-overlap in either dimension is a deterministic `NO_MATCH`; missing manufacture-year evidence alone is not a contradiction; and model year present on only one side routes an otherwise structural auto-match to `REVIEW` unless stronger identity evidence establishes the match.

`benchmarks/catalog_identity_year_semantics_challenge_v1.json` version `year-semantics-1.1` is the focused regression gate, and `CATALOG-YEAR-SEMANTICS-CHALLENGE-V1.md` records the evidence and decision. Reopen this debt only if new evidence or product requirements justify changing the selected rule.

## Web extraction source-family coverage/generalization

Status: `OPEN / LOCALLY_VERIFIED`

`REPEATABLE-WEB-EXTRACTION-V1.md` records a frozen 12-configuration Autoevolution source-family characterization. Strict extraction still succeeds on 8/12 configurations, emits 96/96 correct fields and recalls 96/142 source target fields; strict unsupported structures continue to fail explicitly.

The gap is partially remediated without redefining strict success. An additive facts+issues report path preserves independently valid evidence from structurally partial pages. On the same frozen corpus it retains 140/142 source target fields, all 140 emitted fields are correct, and all four problematic configurations retain usable facts alongside explicit issues. The observed `Combined (EPA)` variation is handled only through a declared validated alias, with the exact source label preserved for provenance.

Two source target fields remain unresolved: the observed non-scalar `curb_weight` ranges. They are preserved as raw issue evidence and are not collapsed to arbitrary scalar weights. Fields truly absent from a source also remain explicit `MISSING_FIELD` issues rather than invented values.

The remaining debt is therefore narrower but still real: select evidence-backed semantics if non-scalar automotive ranges become decision-critical, and characterize reusable extraction beyond this one source family before making heterogeneous-web or production claims. Do not weaken strict validation or convert partial evidence into a false complete-page PASS merely to increase coverage.

## Harness debt

No known harness blocker after Agent Harness V1 beyond normal documentation gardening. Add future durable items here with status and a plan link when work starts.
