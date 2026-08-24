# Technical debt and external blockers

Canonical tracker for durable unresolved work that should survive beyond one prompt or active plan. Completed implementation evidence belongs in the specialized design records and `exec-plans/completed/`; this file keeps only the durable decision state needed to choose future work.

## Release policy: private/proprietary

Status: `INTENTIONAL_PRIVATE_BLOCK`

`docs/LICENSING-STATUS.md` records software status as `PRIVATE_PROPRIETARY`. The repository is private and no public software license is granted. Development, testing and private operation may continue, while package/public release remains intentionally blocked by `scripts/check_release_readiness.py`.

A future MIT, Apache-2.0 or other distribution/open-source choice is deferred until the product is operational and requires a new explicit owner decision. Do not infer or generate a public license before then.

## Historical candidate/research reconstruction

Status: `CLOSED / ARCHIVED`

The scientific corpus, decision-relevant benchmark measurements, primary publication identifiers, and the first selected structured source have been recovered sufficiently for current engineering decisions. `CANDIDATE-EVALUATION-LEDGER.md` records the outcome.

The exact old per-candidate execution ledger for Crawl4AI, Stagehand, Browser Use, Firecrawl, ScrapeGraphAI, Docling and Splink was not recoverable from durable evidence. This remains archived because current Podium 7 code does not depend on those packages. Do not rerun that historical battery merely to reconstruct history; reevaluate only a future decision-critical candidate, narrowly and at its then-current version.

## Product debt: year-semantics resolver rule

Status: `CLOSED / SELECTED_POLICY`

The owner selected the Senatran-aligned rule on 2026-08-23. Manufacture year and model year remain separate identity dimensions; explicit non-overlap in either dimension is a deterministic `NO_MATCH`; missing manufacture-year evidence alone is not a contradiction; and model year present on only one side routes an otherwise structural auto-match to `REVIEW` unless stronger identity evidence establishes the match.

`benchmarks/catalog_identity_year_semantics_challenge_v1.json` version `year-semantics-1.1` is the focused regression gate, and `CATALOG-YEAR-SEMANTICS-CHALLENGE-V1.md` records the evidence and decision. Reopen only if new evidence or product requirements justify changing the selected rule.

## Acquisition and source-family generalization

Status: `CLOSED / CURRENT BOUNDED PROCESS COMPLETE`

Completed bounded capabilities are recorded in their dedicated design records:

- `REPEATABLE-WEB-EXTRACTION-V1.md` — retained Autoevolution extraction benchmark and measured strict/partial behavior;
- `DIRECT-HTTP-ACQUISITION-V1.md` — fail-closed direct HTTP transport semantics and snapshot contract;
- `NETWORK-TARGET-BINDING-V1.md` — DNS-rebinding-resistant acquisition path for arbitrary untrusted locators; each hop resolves, validates, and connects to the same validated IP set while preserving hostname TLS verification;
- `INMETRO-PBEV-DOCUMENT-PATH-V1.md` — deliberate source-specific current Inmetro PBEV PDF acquisition and ruled-table extraction path; `pdfplumber` is an optional `pbev` extra and the global HTTP media policy remains unchanged;
- `PRODUCTION-SOURCE-DISTRIBUTION-V1.md` — bounded regression gate for independently inspected source-family and regional diversity across US/EU/BR without a production-completeness claim;
- `PUBLIC-WEB-ACQUISITION-CHARACTERIZATION-V1.md` — bounded real-network compatibility observation;
- `BROWSER-ACQUISITION-CHARACTERIZATION-V1.md` — normal Chromium did not overcome the measured Autoevolution HTTP 403 path, so generic browser fallback was not selected;
- `COMPLIANT-ALTERNATIVE-SOURCES-V1.md` — official alternative-source selection: NHTSA vPIC `ADAPT`, EEA `ADAPT`, FuelEconomy.gov `REFERENCE`, and the historical Inmetro resource boundary that motivated the now-implemented document path;
- `EEA-SOURCE-FAMILY-V1.md` — third bounded structured source family with explicit regulatory semantics and nonclaims;
- `EEA-SEMANTIC-EXPANSION-V2.md` — official-classification-backed diesel/diesel-electric semantics plus the explicit decision that EEA type/variant/version are regulatory evidence, not canonical retail identity proof;
- `OFFICIAL-SOURCE-DISCOVERY-V1.md` — bounded NHTSA vPIC + FuelEconomy.gov candidate discovery with source-native identifiers/locators and an explicit `identity_proof=False` contract;
- `RECURRING-SOURCE-POLICY-V1.md` — fail-closed recurring-operation robots interpretation and per-host pacing gate using stdlib robots semantics plus the existing Podium rate limiter.

The bounded acquisition/source-family process has no remaining active block. Future production-scale corpus growth, precision/recall measurement, new regions, new semantic fields or new source families are product-operation work and must be reopened only from measured need with new evidence and, where applicable, ADR-0001 evaluation.

Browser automation can be reconsidered only if a different independently measured source family demonstrates both a genuine JavaScript requirement and successful normal-browser acquisition. This is not an active blocker.

MPGe semantics can be reopened when electric-efficiency normalization becomes decision-critical; the current FuelEconomy extraction artifact rejects MPGe explicitly rather than silently converting it. This is not an active blocker.

## Product operation replay cycle

Status: `CLOSED / EVIDENCE ENRICHMENT V3 COMPLETE`

`PRODUCTION-QUALITY-GATE-V2.md` established the pre-enrichment baseline: 60 source-backed records with 19 `CREATED`, 19 `MATCHED`, 22 `REVIEW`, and zero ingestion failures. Review causes were 13 `MISSING_IDENTITY_EVIDENCE` and 9 `LABEL_AMBIGUITY`.

`PRODUCTION-EVIDENCE-ENRICHMENT-V1.md` and `PRODUCTION-QUALITY-GATE-V3.md` reduced that replay to 19 `CREATED`, 20 `MATCHED`, 21 `REVIEW`, and zero failures using explicit Toyota Corolla body-style evidence. Remaining causes were 12 `MISSING_IDENTITY_EVIDENCE` and 9 `LABEL_AMBIGUITY`.

`PRODUCTION-EVIDENCE-ENRICHMENT-V2.md` closed the next measured evidence cycle. Replay diagnostics showed that a deliberately sparse Chevrolet Onix Premier MY26 observation created an earlier canonical candidate that correctly kept later MY26 observations in review. Strengthening that sparse observation with official, case-bound generation and MY26 mechanical evidence, plus enriching the later incomplete observation from the official MY26 price list, reduced the bounded replay to 19 `CREATED`, 22 `MATCHED`, 19 `REVIEW`, and zero failures. Remaining causes were 10 `MISSING_IDENTITY_EVIDENCE` and 9 `LABEL_AMBIGUITY`.

`PRODUCTION-EVIDENCE-ENRICHMENT-V3.md` closes the next measured evidence cycle. The current Volkswagen T-Cross evidence identifies Highline 250 TSI and the case-bound MY26 owner manual explicitly maps the 1.4 Total Flex 110 kW / 250 Nm TSI engine family to the AQ250 six-speed automatic transmission. Adding only that missing transmission field reduces the replay to 19 `CREATED`, 23 `MATCHED`, 18 `REVIEW`, and zero failures. Remaining causes are 9 `MISSING_IDENTITY_EVIDENCE` and 9 `LABEL_AMBIGUITY`. The separate T-Cross one-sided-model-year case remains `REVIEW`; no model year is inferred onto the yearless observation.

The companion source-backed identity quality corpus remains at auto-match precision 1.0 and recall 1.0 with zero false merges and zero ambiguous overcommit. Resolver-policy changes remain zero. Enrichment sources remain bound to each curated case and overlapping field mutations fail closed.

Future review-load reduction must be reopened only when new source-backed evidence can close a measured ambiguity. Do not weaken resolver policy to reduce the nominal review rate, and do not treat this bounded replay as a production-completeness or market-coverage claim.

## Harness debt

No known harness blocker after Agent Harness V1 beyond normal documentation gardening. Add future durable items here with status and a plan link when work starts.
