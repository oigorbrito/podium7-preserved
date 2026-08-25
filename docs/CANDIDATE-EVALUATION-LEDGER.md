# Candidate evaluation ledger

This document is the durable record for external software and data-source evaluation in Podium 7. Its purpose is to preserve prior work, make uncertainty explicit, and prevent broad retesting when usable evidence already exists.

## Evidence policy

- Reconstruct before retesting. Search repository history, PRs, CI artifacts, prior handoffs/logs, and recorded commands/results before running a candidate again.
- Do not repeat a test merely because its conversational summary is missing.
- Retest only the smallest missing slice when no recoverable result exists, a result cannot be tied to an identifiable version/SHA, the original test was incomplete for the current decision, or an architecture/environment change specifically invalidates the result.
- Preserve the distinction between `candidate considered` and `candidate validated`. A name in this ledger is not approval.
- Prefer primary/official documentation and reproducible evidence. For research claims, prefer peer-reviewed publications or established laboratory/benchmark work. Community/social discussion is not primary decision evidence.
- New evaluations must record enough context to avoid another reconstruction: candidate/source, version or timestamp, license/terms status, capability, hypothesis, parameters, environment, result, interpretation, reuse decision, and evidence location.

## Status vocabulary

- `RECOVERED_SUFFICIENT` — evidence is adequate for the decision; do not repeat without a new reason.
- `RECOVERED_INCOMPLETE` — candidate/intent is known, but one or more decision-critical fields are missing.
- `RESULT_ENV_UNCERTAIN` — a result is known, but exact version/environment/parameters are not recovered.
- `NO_EVIDENCE` — no usable prior evidence was recovered after searching durable/project artifacts.
- `OBSOLETE_BY_ARCHITECTURE` — a historical test no longer answers a current product question; do not rerun automatically.
- `ARCHIVED_UNRECOVERABLE` — exact historical execution detail was not recovered and no current decision depends on reconstructing it. If the capability becomes active again, evaluate the then-current candidate/version rather than replaying an old battery.

## Confirmed historical research corpus — `RECOVERED_SUFFICIENT`

The project owner confirmed the following earlier research/benchmark corpus. Primary publication details and decision-relevant measurements are recorded in `SCIENTIFIC-FOUNDATION.md`; those published numbers are not Podium local benchmark results.

| Work / benchmark / standard | Recovered role |
|---|---|
| SODIUM / SODIUM-Bench | agentic data integration / benchmark evidence |
| WebLists / BardeenAgent | repeatable web extraction / agent-to-program evidence |
| WideSearch | broad web collection / agent benchmark evidence |
| WANDR | web retrieval / precision-recall-completeness evidence |
| WebDS | web data-science task benchmark evidence |
| MaDI-Bench | end-to-end data integration benchmark evidence |
| Automatic End-to-End Data Integration using LLMs | LLM-configured deterministic integration evidence |
| KnowledgeNet | knowledge-base population benchmark evidence |
| ComEM | entity matching benchmark evidence |
| ALER | active-learning entity-resolution evidence |
| PARSE | structured extraction / schema optimization evidence |
| DTBench | document-to-table extraction benchmark evidence |
| W3C PROV / PROV-O | provenance model / normative standard |

All rows above are `RECOVERED_SUFFICIENT` for the current decision framework.

## Historical software candidates — current decision closed

Exact historical commands/versions for these packages were not recovered. The missing history is not an active blocker because current repository-native components cover the active capabilities and no runtime dependency currently depends on these packages.

| Candidate | Historical area | Current status | Current action |
|---|---|---|---|
| Crawl4AI | web acquisition/extraction | `OBSOLETE_BY_ARCHITECTURE` | re-evaluate only if a new crawler capability becomes decision-critical |
| Stagehand | web/browser automation | `OBSOLETE_BY_ARCHITECTURE` | re-evaluate only for a newly demonstrated browser requirement |
| Browser Use | browser automation | `OBSOLETE_BY_ARCHITECTURE` | do not infer Podium acceptance from navigation benchmarks |
| Firecrawl | web acquisition/extraction | `OBSOLETE_BY_ARCHITECTURE` | re-evaluate only for a new active capability |
| ScrapeGraphAI | web extraction | `OBSOLETE_BY_ARCHITECTURE` | current repeatable extractor is repository-native |
| Docling | document extraction | `OBSOLETE_BY_ARCHITECTURE` | current document path is repository-native |
| Splink | entity resolution | `OBSOLETE_BY_ARCHITECTURE` | current Catalog Identity resolver is repository-native and benchmarked separately |

The unrecovered original per-candidate results remain `ARCHIVED_UNRECOVERABLE`; do not reverse-engineer them into invented PASS/FAIL or ADOPT/REJECT decisions.

## Automotive data/source candidates

| Candidate/source family | Status | Evidence / disposition |
|---|---|---|
| `vehicle-makes-models` | `RECOVERED_SUFFICIENT` | selected for first real structured ingestion; upstream `gor3a/vehicle-makes-models`, `data/json/artega.json`, source blob `560e795a8a0a9e97d20b7b201b3537962c7d6824`, acquired 2026-08-19; upstream ODbL v1.0; pinned snapshot/attribution in `data/raw/vehicle-makes-models/` |
| `car-data-specifications` | `ARCHIVED_UNRECOVERABLE` | historical details not recovered; no active selection depends on it |
| `automobile-models-and-specs` | `ARCHIVED_UNRECOVERABLE` | historical details not recovered; no active selection depends on it |
| `open-vehicle-db` | `ARCHIVED_UNRECOVERABLE` | historical details not recovered; no active selection depends on it |
| `vehiclesdb` | `ARCHIVED_UNRECOVERABLE` | historical details not recovered; no active selection depends on it |
| FIPE data | `ARCHIVED_UNRECOVERABLE` for historical source comparison | Catalog Identity treats FIPE identifiers separately; old source-evaluation commands are not required for the current resolver |
| EVDB | `ARCHIVED_UNRECOVERABLE` | evaluate current source/terms only if it becomes decision-critical |
| vehicle-specification APIs | `ARCHIVED_UNRECOVERABLE` | original providers/versions not recovered; future use needs a fresh provider/terms decision |
| NHTSA/vPIC-derived data | historical row superseded by current evaluation below | current source-specific evidence now exists; do not reuse unrecovered historical conclusions |

## Current source-family evaluation — FuelEconomy.gov

| Field | Recorded value |
|---|---|
| Capability | second-family repeatable web extraction characterization |
| Candidate | FuelEconomy.gov Find-a-Car vehicle pages and official web-service documentation (`https://www.fueleconomy.gov/feg/ws/index.shtml`) |
| Version | observations acquired 2026-08-23; vehicle IDs `48897`, `42793`, `45011`, `38187`; dataset `fueleconomy-find-a-car-source-family-1.0` |
| License/terms | official U.S. government source; retained benchmark contains only minimal factual target observations; no broad redistribution conclusion is made |
| Hypothesis | repository-native deterministic extraction can be reused on a structurally different source family without semantic overcommit |
| Parameters | combined gasoline MPG, drivetrain, fuel type; declared gas-only alias; anchored `MPG` parser rejects `MPGe`; strict and facts+issues evaluation |
| Environment | Python 3.13.15, GitHub Actions Ubuntu 24.04; validation run `32648780263`, job `97217035510` |
| Result | strict 2/4 pages, 6/6 emitted fields correct, precision 1.000, recall 6/12; partial 10/10 emitted correct, 10/12 target recall, two explicit unresolved MPGe targets; repository suite 343/343 PASS in that validation run |
| Interpretation | extraction/provenance reuse across a second family is locally verified; MPGe remains unsupported; arbitrary-web and production-wide performance are unclaimed |
| Decision | `REFERENCE` |
| Evidence | `benchmarks/web_extraction_fueleconomy_source_family_v1.json`, `data/raw/web/fueleconomy-v1/`, tests/docs, PR #53 |

## Current alternative-source evaluation — NHTSA vPIC

| Field | Recorded value |
|---|---|
| Capability | official source discovery and identity-support candidate |
| Candidate | NHTSA Product Information Catalog and Vehicle Listing (vPIC), `https://vpic.nhtsa.dot.gov/api/` |
| Version | current API documentation checked 2026-08-23; API page showed v4.06/June 2026 release lineage and downloads surface showed v4.07 updated 2026-07-18; exact live response is pinned by URL/hash below |
| License/terms | official NHTSA developer/research API; automated traffic rate control is explicitly documented; no separate broad vPIC redistribution license was established in this evaluation |
| Hypothesis | vPIC can provide normal-access make/model/year candidate discovery and stable source identifiers without introducing a crawler/browser layer |
| Parameters | default Podium `DirectHttpPolicy`; `GetModelsForMakeYear/make/Toyota/modelyear/2025?format=json`; no retry/proxy/browser/bypass |
| Environment | GitHub Actions run `32655508584`, job `97233453958`, Ubuntu 24.04.4 / Python 3.13.15 |
| Result | PASS: HTTP 200 `application/json`, 1,826 bytes, SHA-256 `63741973a12e5efcdc6ae452cce19dd022a91fffba18d330c8c3b05d32e2e915`; parsed 22 model rows with `Make_ID`, `Make_Name`, `Model_ID`, `Model_Name` |
| Interpretation | usable as an official discovery/identity-support path for its documented scope. NHTSA states vPIC data represent vehicles intended for sale/import into the U.S.; this is not universal trim/spec coverage |
| Decision | `ADAPT` |
| Evidence | `COMPLIANT-ALTERNATIVE-SOURCES-V1.md`, PR #63, live artifact `9497328553` |

## Current alternative-source evaluation — EEA passenger-car CO2 data

| Field | Recorded value |
|---|---|
| Capability | third structured automotive source-family candidate |
| Candidate | European Environment Agency passenger-car CO2 monitoring dataset and Discodata SQL REST endpoint |
| Version | 2025 provisional dataset published 2026-06-25; current table `[CO2Emission].[latest].[co2cars_2025Pv31]` |
| License/terms | EEA legal notice generally places EEA-owned materials under CC-BY with acknowledgement; EEA data policy says datasets are open where possible and, unless otherwise indicated, ODC-By or similar; dataset-specific/third-party notices remain authoritative |
| Hypothesis | an official EU registration/type-approval dataset can supply a structurally different machine-readable family with useful automotive factual evidence without semantic overcommit |
| Parameters | default Podium `DirectHttpPolicy`; bounded `SELECT TOP 5 *` Discodata query; no retry/proxy/browser/bypass |
| Environment | GitHub Actions run `32655508584`, job `97233453958`, Ubuntu 24.04.4 / Python 3.13.15 |
| Result | PASS: HTTP 200 `application/json`, 3,478 bytes, SHA-256 `aee9d6cf0529950232d5e20e676c2c9d0f3bb9cdd9b015df3132cfceb49324b2`; parsed five records with make/commercial name/manufacturer, type-approval/type/variant/version, mass, fuel, engine capacity/power, registration year and electric/CO2 fields among the available columns |
| Interpretation | strongest next bounded third-family implementation candidate. Rows carry EU registration/type-approval semantics and must not be silently treated as globally unique retail configurations |
| Decision | `ADAPT` |
| Evidence | `COMPLIANT-ALTERNATIVE-SOURCES-V1.md`, PR #63, live artifact `9497328553` |

## Current alternative-source evaluation — Inmetro PBE Veicular

| Field | Recorded value |
|---|---|
| Capability | official Brazilian model/version, efficiency, consumption and emissions reference candidate |
| Candidate | Inmetro PBE Veicular current table page plus the Brazilian Open Data path advertised by Inmetro |
| Version | 2026 18th cycle; Inmetro news on 2026-08-14 reported 43 brands and 959 models/versions; table page observed updated 2026-08-19 |
| License/terms | evaluated gov.br pages state Creative Commons Attribution-NoDerivatives 3.0 Unported; this evaluation does not assume that page-level terms replace resource-specific open-data metadata |
| Hypothesis | PBEV is a high-value official Brazilian source but should be selected only if its current resource path fits Podium's explicit transport/extraction boundaries |
| Parameters | default Podium `DirectHttpPolicy`; current gov.br landing page, advertised Open Data dataset-detail locator, and current 2026 PDF resource discovery; no retry/proxy/browser/bypass |
| Environment | GitHub Actions run `32655508584`, job `97233453958`, Ubuntu 24.04.4 / Python 3.13.15 |
| Result | partial: landing page PASS HTTP 200 `text/html`, 152,033 bytes, SHA-256 `54bb3bffe06a3f6a30d7939108c9b55440b57b73aacaa46b13d0668fdcf9b8de`, containing the 2026/PBEV table surface. The advertised Open Data dataset-detail API locator returned HTTP 401. The discovered PDF returned HTTP 200 but was deliberately rejected as `UNSUPPORTED_CONTENT_TYPE` because `application/pdf` is outside the default transport policy |
| Interpretation | source quality/relevance is strong, but current automated machine-readable acquisition is not established. The PDF failure is a Podium policy boundary, not site refusal. Verify an exact unauthenticated CSV resource or justify a separate document path before implementation |
| Decision | `REFERENCE` |
| Evidence | `COMPLIANT-ALTERNATIVE-SOURCES-V1.md`, PR #63, live artifact `9497328553` |

## Post-MVP targeted qualification — Brazil identity evidence

### SENATRAN WSDenatran / RENAVAM

| Field | Recorded value |
|---|---|
| Capability | row-level Brazilian vehicle identity/configuration evidence candidate |
| Candidate | SENATRAN WSDenatran / RENAVAM official API, `https://www.gov.br/conecta/catalogo/apis/wsdenatran` |
| Version | primary catalog and technical response documentation checked 2026-08-25 |
| License/terms | official catalog requires SENATRAN authorization and contracting of the online consultation service with SERPRO; no anonymous public production access is assumed |
| Hypothesis | official RENAVAM data can supply the distinct manufacturing-year/model-year and sparse configuration attributes measured as Podium evidence gaps |
| Parameters | documentation-only qualification; no credentialed live request attempted |
| Environment | primary official web documentation; no Podium runtime probe required because the decision-critical boundary is documented authorization/contract access |
| Result | documentation confirms separate `anoModelo` and `anoFabricacao` plus brand/model, body, power, displacement, fuel, engine number and gearbox number fields in the vehicle response model |
| Interpretation | strongest identified Brazil row-level semantic fit; cannot be treated as an available recurring adapter until legitimate access and applicable use terms exist |
| Decision | `UNDECIDED` |
| Evidence | `SOURCE-QUALIFICATION-V1.md`; official Conecta catalog and technical documentation checked 2026-08-25 |

### SENATRAN public fleet datasets

| Field | Recorded value |
|---|---|
| Capability | official Brazilian aggregate/reference evidence |
| Candidate | SENATRAN 2026 fleet publications, `https://www.gov.br/transportes/pt-br/assuntos/transito/conteudo-Senatran/frota-de-veiculos-2026` |
| Version | current 2026 monthly publication surface checked 2026-08-25 |
| License/terms | official public government publication; resource-specific terms remain authoritative for any redistribution decision |
| Hypothesis | public fleet data can corroborate official terminology/aggregate dimensions without being misused as row-level identity proof |
| Parameters | documentation-only qualification |
| Environment | primary official web publication |
| Result | publication exposes aggregated views by `Ano de Fabricação Modelo`, brand/model, fuel, power and vehicle type/species |
| Interpretation | useful semantic and aggregate plausibility reference; insufficient granularity for individual catalog identity resolution |
| Decision | `REFERENCE` |
| Evidence | `SOURCE-QUALIFICATION-V1.md`; official SENATRAN 2026 fleet publication checked 2026-08-25 |

### SENATRAN CAT / SISCAT

| Field | Recorded value |
|---|---|
| Capability | official Brazilian homologation identity semantics |
| Candidate | SENATRAN CAT/SISCAT service documentation |
| Version | service page last modified 2025-12-15; official service material checked 2026-08-25 |
| License/terms | official service/homologation documentation; no public anonymous machine-readable CAT catalog was established in this qualification |
| Hypothesis | CAT establishes the regulatory meaning of RENAVAM brand/model/version identity and may anchor future source contracts |
| Parameters | documentation-only qualification |
| Environment | primary official gov.br service documentation |
| Result | CAT is documented as the homologation instrument granting a specific RENAVAM `marca/modelo/versão` code |
| Interpretation | authoritative semantic reference, but not a currently established automated data-acquisition surface |
| Decision | `REFERENCE` |
| Evidence | `SOURCE-QUALIFICATION-V1.md`; official SISCAT/CAT service documentation checked 2026-08-25 |

## Post-MVP targeted qualification — retained structured sources

The 2026-08-25 documentation review strengthens but does not replace the existing decisions for NHTSA vPIC and EEA:

- **NHTSA vPIC — `ADAPT`:** official documentation states the dataset is populated from manufacturer submissions and provides VIN decoding plus a vehicle-variable catalog. Use returned VIN-backed variables only when present and within documented U.S. scope; missing variables are absence of evidence, not negative proof.
- **EEA passenger-car monitoring — `ADAPT`:** current 2025 provisional data officially expose manufacturer, type-approval number, type, variant, version, make, commercial name, fuel, engine capacity/power, mass, registration year and electric/emissions fields. Preserve regulatory/type-approval semantics; do not convert type/variant/version into retail trim identity or registration year into manufacturing year.
- **Primary manufacturer artifacts — `REFERENCE` evidence class:** official manufacturer-published specifications/homologation/ordering material may be used case-by-case for generation, retail trim or mechanical distinctions, but no generic manufacturer source family is approved by this row. Each concrete source requires its own qualification and provenance contract.

No new broad live probe was executed. Existing NHTSA/EEA operational evidence remains recoverable and sufficient; WSDenatran's limiting condition is documented authorization/contract access, not unknown public endpoint behavior.

## FuelEconomy.gov discovery extension

The same live run `32655508584` verified the existing official model-menu endpoint for Toyota 2025: HTTP 200 JSON, 3,427 bytes, SHA-256 `be18d61bb6c505ff8f75ed9fb4c165321407e5956d041e5f9b6be36e0e27e6f6`, with 63 parsed model/options entries. This remains `REFERENCE`: it strengthens the evidence for a future deterministic discovery flow but does not create a third independent source family.

## Recovered partial results and current disposition

- **Autoevolution:** frozen benchmark evidence remains valid. Current live direct HTTP and normal Chromium both returned HTTP 403 on the retained 9-URL sample. Do not add stealth/proxy/challenge-bypass machinery merely to preserve this live source; official alternatives are now selected for further work.
- **Ford Mustang Dark Horse:** the recovered artifact was TXT, not PDF. The current document-extraction boundary preserves the factual snapshot; no PDF-specific historical claim is required.

## Required evaluation record for future candidates

Every new/repeated candidate evaluation must record:

| Field | Required content |
|---|---|
| Capability | product capability under evaluation |
| Candidate | source/service/repository and URL or durable identifier |
| Version | SHA/tag/API version/dataset release/snapshot timestamp |
| License/terms | relevant use/reuse/access status |
| Hypothesis | what the evaluation is intended to establish |
| Parameters | commands, inputs, flags, thresholds and relevant configuration |
| Environment | runtime/OS/dependencies needed to interpret the result |
| Result | PASS/FAIL/SKIP/partial plus measured output |
| Interpretation | what the result does and does not prove |
| Decision | `ADOPT`, `ADAPT`, `REFERENCE`, `REJECT`, or `UNDECIDED` |
| Evidence | Git path, commit, PR, CI artifact, benchmark, or durable external source |

## Reconstruction outcome

`SCIENTIFIC_CORPUS = RECOVERED_SUFFICIENT`

`PRIMARY_BENCHMARK_DETAILS = RECOVERED_SUFFICIENT`

`FIRST_SELECTED_STRUCTURED_SOURCE = RECOVERED_SUFFICIENT`

`HISTORICAL_SOFTWARE_TEST_LEDGER = ARCHIVED_UNRECOVERABLE / NOT CURRENTLY_DECISION_CRITICAL`

`WHOLESALE_HISTORICAL_RETEST_REQUIRED = NO`

There is no remaining research-reconstruction blocker for current Podium 7 development. Current alternative-source decisions are now recorded separately from unrecoverable historical source tests and must be revisited only when new evidence or a new product scope makes a source decision-critical.
