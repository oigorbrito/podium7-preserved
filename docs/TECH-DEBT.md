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

Status: `OPEN / CORE BOUNDED CAPABILITIES LOCALLY_VERIFIED`

Completed bounded capabilities are recorded in their dedicated design records:

- `REPEATABLE-WEB-EXTRACTION-V1.md` — retained Autoevolution extraction benchmark and measured strict/partial behavior;
- `DIRECT-HTTP-ACQUISITION-V1.md` — fail-closed direct HTTP transport semantics and snapshot contract;
- `PUBLIC-WEB-ACQUISITION-CHARACTERIZATION-V1.md` — bounded real-network compatibility observation;
- `BROWSER-ACQUISITION-CHARACTERIZATION-V1.md` — normal Chromium did not overcome the measured Autoevolution HTTP 403 path, so generic browser fallback was not selected;
- `COMPLIANT-ALTERNATIVE-SOURCES-V1.md` — official alternative-source selection: NHTSA vPIC `ADAPT`, EEA `ADAPT`, FuelEconomy.gov `REFERENCE`, Inmetro PBEV `REFERENCE` under the current resource/transport boundary;
- `EEA-SOURCE-FAMILY-V1.md` — third bounded structured source family with explicit regulatory semantics and nonclaims;
- `OFFICIAL-SOURCE-DISCOVERY-V1.md` — bounded NHTSA vPIC + FuelEconomy.gov candidate discovery with source-native identifiers/locators and an explicit `identity_proof=False` contract;
- `RECURRING-SOURCE-POLICY-V1.md` — fail-closed recurring-operation robots interpretation and per-host pacing gate using stdlib robots semantics plus the existing Podium rate limiter.

The generic debts “find any compliant alternative live source”, “implement EEA source-family V1”, “implement bounded official source discovery V1”, and “define recurring-operation source policy” are closed.

Remaining acquisition/generalization debt is concrete:

1. **Network target binding.** Strengthen protection against SSRF/DNS rebinding before accepting arbitrary untrusted locators. The current direct-HTTP boundary remains intentionally narrower than that future capability.
2. **Inmetro PBEV path, when needed.** Characterize an exact current unauthenticated machine-readable resource or a deliberate source-specific PDF/document acquisition-and-extraction path only when Brazilian coverage is an active product need. Do not weaken the default global HTTP media-type or validation policy merely to make the current PDF/401 surfaces pass.
3. **Production source distribution and corpus breadth.** Broaden coverage only through independently inspected source-family evidence and measured failure modes. Current bounded results do not establish heterogeneous-web or production precision/recall, discovery completeness, or production-wide European/U.S./Brazilian coverage.
4. **EEA semantic expansion.** V1 does not establish diesel/diesel-electric mappings, production-wide European coverage, or canonical retail identity from EEA type/variant/version evidence. Expand only when those semantics become decision-critical and independently benchmarked.

Browser automation can be reconsidered only if a different independently measured source family demonstrates both a genuine JavaScript requirement and successful normal-browser acquisition. Do not add a generic browser/agent layer merely because direct HTTP failed.

MPGe semantics are not an active blocker because the current FuelEconomy extraction artifact rejects MPGe explicitly rather than silently converting it. Reopen only when electric-efficiency normalization becomes decision-critical.

## Harness debt

No known harness blocker after Agent Harness V1 beyond normal documentation gardening. Add future durable items here with status and a plan link when work starts.
