# Compliant Alternative Automotive Sources V1

Status: research selection complete; implementation of selected adapters is separate work.

## Decision question

After the retained Autoevolution URLs returned HTTP 403 to both the Podium direct-HTTP client and a normal Chromium identity, which current automotive sources can be used without bypass behavior and still satisfy Podium's evidence, provenance, minimality and semantic-conservatism rules?

This record uses current primary documentation plus a bounded GitHub-hosted live probe. It does not rank sources by convenience, nominal field count or search-engine popularity.

## Selection rules

A source is useful only when all relevant claims can be tied to independently inspectable evidence. The evaluation therefore required:

- an identifiable primary owner and current documentation/dataset release;
- useful automotive semantics that can be mapped without silently changing meaning;
- normal access without stealth, proxy rotation, CAPTCHA/challenge interaction or alternate identities;
- explicit rate/access constraints where documented;
- a provenance path that can preserve the exact source locator and acquired bytes/hash;
- a narrow disposition (`ADOPT`, `ADAPT`, `REFERENCE`, `REJECT`, or `UNDECIDED`) rather than a universal-source claim.

HTTP 200 alone is not a PASS. JSON responses were parsed and checked for source-relevant records/keys. The Inmetro landing page was checked for the current 2026 cycle/table surface.

## Primary-source evidence

### NHTSA vPIC

Primary documentation: <https://vpic.nhtsa.dot.gov/api/> and <https://vpic.nhtsa.dot.gov/>.

Current API documentation identifies vPIC as NHTSA's vehicle/manufacturer data API, populated from manufacturer information submitted through NHTSA processes. It provides JSON/CSV/XML outputs, VIN decoding and make/model/year methods including `GetModelsForMakeYear`. The API documents automated traffic rate control. NHTSA also states that vPIC data represent vehicles intended for sale or importation into the United States; vehicles outside that scope may yield limited results.

Current release evidence observed during this evaluation: API page version 4.06 with June 2026 release notes; the vPIC downloads surface reported version 4.07 updated July 18, 2026. The exact API endpoint used by Podium is therefore recorded by locator and acquisition hash rather than relying on a single broad version label.

Reuse/terms boundary: this work establishes official intended developer/research access and rate-control constraints. It does not claim a separate broad redistribution license for all vPIC content because no source-specific license statement was established in the evaluated API documentation.

### European Environment Agency passenger-car CO2 monitoring data

Primary dataset page: <https://www.eea.europa.eu/en/datahub/datahubitem-view/fa8b1229-3db6-495d-b18e-9c9b3267c02b>.

Primary Discodata API documentation: <https://discodata.eea.europa.eu/Help.html>.

The EEA 2025 provisional passenger-car dataset was published June 25, 2026 under Regulation (EU) 2019/631. The published current SQL table is `[CO2Emission].[latest].[co2cars_2025Pv31]`. EEA documents Discodata as a public SQL Server REST endpoint returning query results as JSON.

The current table exposes fields relevant to Podium including make/commercial name, manufacturer, type-approval/type/variant/version identifiers, mass, fuel, engine capacity, engine power, electric energy consumption/range, registration year and emissions-related fields. These are registration/type-approval monitoring semantics; they must not be silently reinterpreted as globally unique retail trims.

Reuse evidence: EEA's legal notice states that EEA-owned materials are generally published under CC-BY and may be reused with acknowledgement, while dataset-specific/third-party notices still control where present. The EEA data policy further states that datasets are made openly available where possible and, unless otherwise indicated, are distributed under ODC-By or a similar open standard license. Podium must preserve attribution and any dataset-specific conditions.

### Inmetro PBE Veicular

Primary current table page: <https://www.gov.br/inmetro/pt-br/assuntos/regulamentacao/avaliacao-da-conformidade/programa-brasileiro-de-etiquetagem/tabelas-de-eficiencia-energetica/veiculos-automotivos-pbe-veicular/>.

Primary open-data availability notice: <https://www.gov.br/inmetro/pt-br/acesso-a-informacao/perguntas-frequentes/avaliacao-da-conformidade/etiquetagem-para-veiculos-leves/tabela-pbev-indisponivel-no-site>.

Inmetro's August 14, 2026 publication states that the 2026 PBE Veicular table covered 43 brands and 959 models/versions and provides consumption, emissions and efficiency information across combustion, hybrid, plug-in hybrid and electric vehicles. The current PBEV page identified the 2026 18th cycle and was updated August 19, 2026 during this evaluation.

The official FAQ says the PBE table is also available in CSV through the Brazilian Open Data portal. The gov.br pages evaluated here state Creative Commons Attribution-NoDerivatives 3.0 Unported for site content. This record does not infer that the same page-level license automatically resolves every dataset/resource reuse question; exact resource metadata remains authoritative.

### FuelEconomy.gov discovery baseline

Primary web-service documentation: <https://www.fueleconomy.gov/feg/ws/index.shtml>.

FuelEconomy.gov was already retained as Podium's second characterized web source family. Its documented menu flow (`year -> make -> model -> options/vehicle ID`) is included here only as an existing official discovery baseline, not counted as a newly discovered source family.

## Live characterization

Observed GitHub Actions run `32655508584`, job `97233453958`, Ubuntu 24.04.4 / Python 3.13.15. The existing `DirectHttpPolicy` defaults were used: HTTPS, no proxy, no browser, no retry, no stealth or alternate identity. Artifact: `9497328553`; uploaded ZIP SHA-256 `cac6e7bb31c9dfd1b98bfd0d9bc74932081114517b2845e6eae4756e9ec96a23`.

| Candidate/probe | Observed result | Content relevance check |
|---|---|---|
| NHTSA vPIC `GetModelsForMakeYear` — Toyota 2025 | `PASS`, HTTP 200, `application/json`, 1,826 bytes, SHA-256 `63741973a12e5efcdc6ae452cce19dd022a91fffba18d330c8c3b05d32e2e915` | parsed `Results`: 22 model records; keys `Make_ID`, `Make_Name`, `Model_ID`, `Model_Name`; first observed models included Corolla, Prius, Land Cruiser, Highlander and 4Runner |
| EEA `[CO2Emission].[latest].[co2cars_2025Pv31]` bounded query | `PASS`, HTTP 200, `application/json`, 3,478 bytes, SHA-256 `aee9d6cf0529950232d5e20e676c2c9d0f3bb9cdd9b015df3132cfceb49324b2` | parsed `results`: 5 records; result keys included `Mk`, `Cn`, `Man`, `TAN`, `T`, `Va`, `Ve`, `M (kg)`, `Ec (cm3)`, `Ep (KW)`, `Ft`, `Year`, `Z (Wh/km)` and other monitoring fields |
| Inmetro PBEV landing page | `PASS`, HTTP 200, `text/html`, 152,033 bytes, SHA-256 `54bb3bffe06a3f6a30d7939108c9b55440b57b73aacaa46b13d0668fdcf9b8de` | current page contained `Veículos leves 2026`, `Tabela PBEV` and PDF resource links |
| Inmetro Brazilian Open Data detail endpoint for PBE | `FAIL`, HTTP 401 | official FAQ still advertises CSV availability, but the unauthenticated API locator tested in this runner was not usable; do not claim automated CSV acquisition until a concrete resource locator is independently verified |
| Inmetro 2026 PDF resource discovered from landing-page HTML | `FAIL` under the default Podium policy with HTTP 200 | response media type was `application/pdf`; the failure was `UNSUPPORTED_CONTENT_TYPE`, a deliberate current transport-policy boundary rather than a site refusal |
| FuelEconomy.gov model menu — Toyota 2025 | `PASS`, HTTP 200, `application/json`, 3,427 bytes, SHA-256 `be18d61bb6c505ff8f75ed9fb4c165321407e5956d041e5f9b6be36e0e27e6f6` | parsed 63 model/options menu entries; observed examples included 4Runner variants and bZ4X variants |

A preceding transport-only probe (`32655352277`, job `97233065804`) produced the same NHTSA, Inmetro landing-page and FuelEconomy transport hashes and established the initial EEA transport success before relevance parsing. The relevance-aware run above is the decision record.

## Dispositions

### NHTSA vPIC — `ADAPT`

Use as an official **source-discovery and identity-support path**, especially make/model/year enumeration and VIN-backed attributes where applicable. It is not selected as a universal specification source. Respect documented automated rate control and U.S.-market scope. A deterministic adapter should preserve NHTSA IDs and exact request locators as provenance.

### EEA passenger-car CO2 data — `ADAPT`

Select as the strongest next **third structured source-family implementation candidate**. It has current machine-readable JSON access, independently documented schema/semantics, useful mass/power/capacity/fuel/type-variant-version evidence, and an explicit public-sector reuse framework. The first implementation should be a bounded frozen source-family benchmark, not a production-wide import.

### Inmetro PBE Veicular — `REFERENCE`

Retain as a high-value **Brazilian official source candidate**, but do not call it production-ready yet. The landing page is normally acquirable and the source is highly relevant to Brazilian model/version, fuel, consumption, emissions and efficiency semantics. However, the advertised Open Data API detail route returned 401 in the live probe and the current public table is exposed as PDF to the default Podium transport. A future bounded unit may either verify an exact unauthenticated CSV resource locator or deliberately add a source-specific document media-type/acquisition path with independent extraction evidence. Do not weaken the global default policy just to make this row pass.

### FuelEconomy.gov discovery menu — `REFERENCE`

Keep as an already-characterized U.S. official reference and a proven deterministic menu/discovery path. Do not count it as a new independent source-family result in this work unit.

### Autoevolution refused live path — no further bypass work selected

The prior direct-HTTP and normal-Chromium failures remain evidence that the current live Autoevolution route is not worth escalating with stealth/proxy/challenge-bypass machinery. Its frozen retained evidence remains valid for historical benchmark purposes, but new live acquisition should prefer the official alternatives above.

## What this changes

The open question is no longer "can Podium find any compliant alternatives?" It can. Two official machine-readable paths now have both current primary documentation and live normal-access evidence:

1. NHTSA vPIC for discovery/identity support;
2. EEA passenger-car CO2 monitoring data for a third structured factual source family.

Inmetro PBEV is also a high-value official Brazilian reference, with a specific transport/resource-discovery blocker rather than an unknown source-quality question.

## What this does not prove

This work does **not** establish:

- arbitrary-web or production-wide coverage;
- that NHTSA model names equal canonical global trim identities;
- that EEA registration/type-approval rows equal one retail configuration each;
- automated current Inmetro CSV availability;
- PDF extraction correctness for PBEV;
- recurring-operation robots/rate/politeness policy compliance beyond the rate-control constraints explicitly documented by a source;
- comprehensive SSRF/DNS-rebinding protection;
- permission to ignore dataset-specific notices, attribution or third-party rights.

## Next evidence-backed implementation order

1. **EEA source-family V1** — freeze a small independently inspected sample, define explicit field semantics, build deterministic extraction/alignment and measure strict/partial correctness separately from transport.
2. **Official source discovery V1** — use NHTSA vPIC plus the already-proven FuelEconomy.gov menu flow to produce bounded candidate locators/identifiers for U.S.-market vehicles, without treating discovery as identity proof.
3. **Inmetro PBEV machine-readable/document characterization** — only after an exact current CSV resource URL is verified or a deliberate PDF acquisition/extraction contract is justified by a concrete Brazilian coverage need.
4. Add recurring-operation host policy (rate/politeness/robots where applicable) before scheduling large live acquisition.
5. Strengthen network target binding before accepting arbitrary untrusted locators.

These priorities are engineering choices constrained by the evidence above, not claims that the sources are universally best.
