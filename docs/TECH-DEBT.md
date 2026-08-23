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

Status: `OPEN / THREE FROZEN SOURCE FAMILIES LOCALLY_VERIFIED + OFFICIAL DISCOVERY PATHS SELECTED + DIRECT HTTP TRANSPORT + LIVE SAMPLES`

`REPEATABLE-WEB-EXTRACTION-V1.md` records the frozen Autoevolution source-family characterization and keeps the historical V1 artifact separately reproducible. Historical strict V1 remains 8/12 configurations with 96/96 emitted fields correct and 96/142 source target fields recalled. Historical partial-evidence V1 remains 140/142 retained source target fields with 140/140 emitted fields correct. The bounded V2 artifact raises the same-family result to 10/12 strict configurations with 120/120 emitted fields correct and preserves 142/142 source targets in partial mode with zero incorrect emitted fields.

A second, structurally different source family is characterized with four frozen FuelEconomy.gov vehicle observations and a separate three-field reusable artifact. Gasoline MPG, drivetrain and fuel type are extracted with source-family-specific provenance; the PHEV `Combined MPG on Gas Only` label is handled by a declared alias. MPGe is deliberately rejected by the gasoline-MPG parser rather than being silently converted to L/100km. On this frozen second-family slice, strict extraction succeeds on 2/4 cases with 6/6 emitted fields correct and 6/12 source target fields recalled; partial-evidence extraction retains 10/12 source target fields with 10/10 emitted fields correct and leaves the two MPGe targets explicit and unresolved.

Frozen acquisition lineage is independently gated across the original two-family benchmark inventory. The manifest is derived from those benchmark case inventories and covers 16/16 retained snapshots across 13 exact HTTPS source URLs. Every snapshot is checked against a pinned repository blob identity and produces a verified SHA-256 content-addressed reference; the measured retained corpus has zero acquisition-evidence issues. Missing, empty, mutated, duplicated, unpinned/orphaned and non-HTTPS acquisition evidence fails explicitly.

`DIRECT-HTTP-ACQUISITION-V1.md` adds a separate locally verified direct-HTTP transport boundary for one explicit locator. The deterministic loopback-server suite covers protected URL/network defaults, redirect revalidation/count/limits, HTTP status, media type, content encoding, timeout, declared and streamed response-size limits, empty/malformed responses, byte-exact SHA-256 preservation, verified snapshot writing, no-clobber behavior and explicit overwrite.

`PUBLIC-WEB-ACQUISITION-CHARACTERIZATION-V1.md` adds one real public-network observation against the exact 13 retained HTTPS source URLs using that unchanged default policy. On GitHub Actions run `32653023995`, FuelEconomy.gov was 4/4 direct-HTTP PASS while all 9 unique Autoevolution URLs returned HTTP 403, for 4/13 overall acquisition success in that runner/time/sample. The live probe used no retry, browser fallback, proxy rotation or user-agent impersonation. This closes the previous complete absence of public-network evidence, but it does not convert the sample into a general success-rate estimate.

`BROWSER-ACQUISITION-CHARACTERIZATION-V1.md` measures the exact 9 Autoevolution URLs refused by direct HTTP using a normal JavaScript-capable Playwright/Chromium identity. On run `32654062805`, Playwright 1.62.0 with Chromium 151.0.7922.34 produced **0/9 acquisition PASS**: every main-document response remained HTTP 403, every title was `Just a moment...`, eight body observations exposed the configured `cloudflare` block marker, and no URL exposed retained specification relevance markers. The measurement used no stealth, proxy, custom user-agent, cookie seeding, challenge interaction or alternate identity. The browser therefore is **not selected as a permanent fallback for this observed failure mode**; Playwright remains outside runtime/package dependencies.

`COMPLIANT-ALTERNATIVE-SOURCES-V1.md` closes the narrower question of whether compliant official alternatives can be found without bypassing the refused Autoevolution path. Current primary documentation plus GitHub Actions live run `32655508584` establish two directly usable machine-readable paths: NHTSA vPIC (`ADAPT`) for U.S.-market make/model/year discovery and identity support, and EEA passenger-car CO2 monitoring data (`ADAPT`) as the strongest next third structured source-family candidate. The same run verified FuelEconomy.gov's existing menu path (`REFERENCE`) and the current Inmetro PBEV landing page. Inmetro PBEV remains `REFERENCE`: its official FAQ advertises CSV through the Brazilian Open Data portal, but the unauthenticated dataset-detail API locator tested by Podium returned HTTP 401, while the current table resource is PDF and is deliberately outside the default HTTP media-type policy.

`EEA-SOURCE-FAMILY-V1.md` implements that selected EEA path as a third bounded structured source family. The exact four-row 2025 provisional response is frozen at 1,165 bytes with SHA-256 `847fa97a46ae32d60673fe63b5ebeeb2d35575771c607b806e3bdedd1c7d2ec9` from GitHub Actions run `32656518259`, job `97235995006`. The inspected slice covers electric, petrol-hybrid, petrol/electric plug-in hybrid and petrol-monofuel observations. V1 promotes only engine power, engine capacity where applicable, and four explicitly benchmarked fuel type/mode combinations. EEA `M (kg)` is retained as **mass in running order** regulatory evidence and deliberately not mapped to `curb_weight`; WLTP CO2 and electric-energy fields are likewise preserved without inventing new normalized semantics. The frozen benchmark has 4/4 strict cases and 11/11 supported target facts correct, with zero incorrect emitted fields; partial mode also retains 11/11 with zero unresolved targets on this bounded slice.

The repository therefore has local deterministic evidence for retained-snapshot lineage, direct HTTP transport semantics, three structurally different frozen source families, bounded real-network compatibility observations, a bounded normal-browser refusal characterization for Autoevolution, and current official alternative/discovery-source selection evidence. It still does **not** establish heterogeneous-web or production precision/recall, production source distribution, source-discovery completeness, recurring robots/rate/politeness behavior, comprehensive SSRF/DNS-rebinding defense, automated current Inmetro CSV acquisition, PDF extraction correctness for PBEV, or a general MPGe semantic mapping. EEA type/variant/version evidence also does not by itself prove canonical retail identity, and V1 does not establish diesel/diesel-electric fuel mappings or production-wide European coverage.

The generic debt **"find any compliant alternative live source" is closed**, and bounded **EEA source-family V1** is now implemented. Remaining acquisition/generalization debt is concrete:

1. implement bounded **official source discovery V1** using NHTSA vPIC and the already-verified FuelEconomy.gov menu flow, preserving discovery as candidate generation rather than identity proof;
2. characterize an exact current **Inmetro PBEV machine-readable or deliberate document path** only when Brazilian coverage is the active need; do not weaken global validation just to make the PDF/401 surfaces pass;
3. define recurring-operation robots/rate/politeness and host pacing before scheduling broad live acquisition;
4. strengthen network target binding before accepting arbitrary untrusted locators;
5. broaden production source distribution/corpus coverage only through independently inspected source-family evidence and measured failure modes, including any future expansion of EEA fuel modes or canonical identity use.

Browser automation can be reconsidered only when a different independently measured source family demonstrates a genuine JavaScript requirement and successful normal-browser acquisition. Do not add a generic browser/agent layer merely because direct HTTP failed. Do not weaken strict validation or silently accept missing/semantically incompatible data.

Bounded-range semantics for `curb_weight` are no longer an open debt. MPGe semantics are not an active blocker because the current artifact rejects them explicitly; reopen that question only when electric-efficiency normalization becomes decision-critical.

## Harness debt

No known harness blocker after Agent Harness V1 beyond normal documentation gardening. Add future durable items here with status and a plan link when work starts.
