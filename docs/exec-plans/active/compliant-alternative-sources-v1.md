# Compliant alternative sources V1

Status: active — research and live characterization complete; final repository validation/integration pending

## Outcome

Identify current, compliant live automotive data paths that fit Podium 7 after the retained Autoevolution URLs refused both direct HTTP and normal Chromium. Selection must be grounded in primary documentation and reproducible acquisition evidence, not in convenience or a desire to close the task.

## Evaluated candidates

1. **NHTSA vPIC** — official U.S. vehicle/manufacturer API for make/model/year discovery, VIN decoding and vehicle attributes. Current docs state JSON/CSV/XML support and automated rate control; U.S.-sale/import scope is explicit.
2. **European Environment Agency passenger-car CO2 monitoring data** — official EEA dataset under Regulation (EU) 2019/631, exposed through Discodata SQL-over-HTTP JSON. Current 2025 provisional table provides make/commercial name/type/variant/version, mass, fuel, engine capacity/power and electric/emissions fields.
3. **Inmetro PBE Veicular** — official Brazilian PBEV source for model/version, fuel, consumption, emissions and efficiency. Current page is public; Inmetro also advertises CSV through Dados Abertos, but the exact unauthenticated dataset-detail API locator tested here returned 401 and the public table resource is PDF.
4. **FuelEconomy.gov menu flow** — already characterized source family, used only as an existing official discovery/reference baseline.

## Evidence criteria

A candidate was not selected merely because it was public or returned HTTP 200. The durable record covers primary ownership/version, semantics/scope, license/reuse/access constraints, current transport behavior, useful fields, nonclaims and disposition.

## Live evidence

Decision run: GitHub Actions `32655508584`, job `97233453958`, Ubuntu 24.04.4 / Python 3.13.15. Policy: existing `DirectHttpPolicy` defaults, no proxy/browser/retry/stealth/challenge interaction. Artifact `9497328553`, ZIP SHA-256 `cac6e7bb31c9dfd1b98bfd0d9bc74932081114517b2845e6eae4756e9ec96a23`.

- NHTSA vPIC Toyota 2025 models: PASS HTTP 200 JSON, 22 parsed model rows, SHA-256 `63741973a12e5efcdc6ae452cce19dd022a91fffba18d330c8c3b05d32e2e915`.
- EEA 2025 provisional bounded query: PASS HTTP 200 JSON, five parsed records with the expected automotive monitoring fields, SHA-256 `aee9d6cf0529950232d5e20e676c2c9d0f3bb9cdd9b015df3132cfceb49324b2`.
- Inmetro PBEV landing page: PASS HTTP 200 HTML and current 2026 table markers, SHA-256 `54bb3bffe06a3f6a30d7939108c9b55440b57b73aacaa46b13d0668fdcf9b8de`.
- Inmetro advertised Open Data dataset-detail API locator: FAIL HTTP 401.
- Inmetro current 2026 PDF resource: HTTP 200 but explicit `UNSUPPORTED_CONTENT_TYPE` because `application/pdf` is outside the default policy.
- FuelEconomy.gov Toyota 2025 model menu: PASS HTTP 200 JSON, 63 parsed menu entries, SHA-256 `be18d61bb6c505ff8f75ed9fb4c165321407e5956d041e5f9b6be36e0e27e6f6`.

The temporary live workflow was removed after evidence capture so external services are not a permanent required CI dependency.

## Decisions

- NHTSA vPIC: `ADAPT` for bounded official source discovery / identity support; not universal specifications.
- EEA passenger-car CO2 data: `ADAPT` as strongest next third structured source-family implementation candidate; first implementation must be a frozen independently inspected benchmark.
- Inmetro PBEV: `REFERENCE` until an exact current unauthenticated CSV resource is verified or a deliberate document acquisition/extraction path is justified.
- FuelEconomy.gov discovery menu: `REFERENCE`; strengthens an already-characterized official discovery path but is not a new independent family.
- No further Autoevolution bypass work selected.

Durable details and nonclaims are in `docs/COMPLIANT-ALTERNATIVE-SOURCES-V1.md`; candidate dispositions are recorded in `docs/CANDIDATE-EVALUATION-LEDGER.md`; concrete remaining work is in `docs/TECH-DEBT.md`.

## Acceptance criteria

- [x] current primary-source research is durably recorded;
- [x] at least three alternative source families evaluated without unsupported legal/coverage claims;
- [x] live outcomes recorded with exact runner, status/media type and hashes for successful acquisitions;
- [x] selected next source paths have both useful semantics and measured normal-access evidence;
- [x] no permanent browser/crawler dependency added;
- [x] temporary public-network workflow removed after evidence capture;
- [x] candidate ledger and technical debt updated;
- [ ] final merge candidate passes repository harness, runtime health and every isolated test;
- [ ] branch is zero commits behind `main` before squash merge;
- [ ] completed plan archived and `CURRENT-WORK` cleared in housekeeping PR.

## Decision classification

- primary-source documentation and published dataset/API properties: `EVIDENCE_BACKED`;
- observed live acquisition behavior: `LOCALLY_VERIFIED` for run `32655508584` and its exact sample;
- candidate adaptation/reference decisions: `ENGINEERING_CHOICE` constrained by the evidence;
- arbitrary-web or production-wide coverage: `UNKNOWN`.
