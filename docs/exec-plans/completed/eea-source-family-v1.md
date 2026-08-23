# EEA Source Family V1

Status: completed — integrated by PR #65 on 2026-08-23

## Outcome

Implemented a bounded third structured automotive source family from the European Environment Agency passenger-car CO2 monitoring dataset. The implementation is driven by frozen official evidence and independent gold expectations rather than nominal schema richness.

## Evidence boundary

Primary dataset: EEA Monitoring of CO2 emissions from passenger cars under Regulation (EU) 2019/631.

Selected table at freeze: `[CO2Emission].[latest].[co2cars_2025Pv31]`, 2025 provisional data published 2026-06-25.

EEA rows remain registration/type-approval monitoring observations. Type, variant and version are preserved as source identifiers/evidence and are not silently redefined as globally unique retail trims.

## Live acquisition and frozen evidence

Bounded live acquisition used the existing `DirectHttpPolicy` defaults with no proxy, browser, retry, stealth or alternate identity.

- GitHub Actions run: `32656518259`;
- job: `97235995006`;
- runner: Ubuntu 24.04.4 / Python 3.13.15;
- returned source IDs: `162744190`, `162744191`, `162744196`, `162744197`;
- HTTP 200, `application/json`, UTF-8, zero redirects;
- exact response size: 1,165 bytes;
- exact SHA-256: `847fa97a46ae32d60673fe63b5ebeeb2d35575771c607b806e3bdedd1c7d2ec9`;
- frozen snapshot: `data/raw/web/eea-v1/eea-passenger-cars-2025-bounded-v1.json`;
- independent gold: `benchmarks/eea_source_family_v1.json`.

The temporary live workflow was removed after evidence capture. Public network access is not a permanent CI dependency.

## Semantic correction made during implementation

The initial plan listed `curb_weight` among candidate normalized facts because the EEA source exposes `M (kg)`. Primary-source review established that this field is **mass in running order**. Equal units do not establish equal semantics, so the implementation deliberately changed course:

- `M (kg)` is preserved as `mass_in_running_order_kg` regulatory evidence;
- it is **not** promoted to Podium `curb_weight`;
- WLTP CO2 and electric-energy fields are also retained as regulatory evidence without inventing new normalized attributes.

This correction is part of the completed outcome, not an unresolved implementation gap.

## Implemented V1 mappings

The frozen inspected slice promotes only:

- `Ep (KW)` -> `power` with kW identity normalization;
- `Ec (cm3)` -> `displacement` for applicable non-electric observations;
- `Ft=petrol`, `Fm=M` -> `fuel_type=gasoline`;
- `Ft=petrol`, `Fm=H` -> `fuel_type=hybrid`;
- `Ft=petrol/electric`, `Fm=P` -> `fuel_type=plug_in_hybrid`;
- `Ft=electric`, `Fm=E` -> `fuel_type=electric` for the frozen V1 combination.

Unsupported fuel type/mode combinations fail explicitly rather than falling through to generic token normalization.

## Frozen benchmark result

Four independently inspected cases cover electric, petrol hybrid, petrol/electric plug-in hybrid and petrol monofuel observations, with 11 promoted source target facts in total.

- strict: 4/4 cases PASS;
- strict facts: 11/11 correct;
- incorrect emitted facts: 0;
- strict precision: 1.0;
- strict recall: 1.0;
- partial evidence: 11/11 retained correctly;
- unresolved target facts: 0 on this bounded slice;
- partial issues: 0 on this bounded slice.

These are bounded source-family measurements, not production-wide European precision/recall claims.

## Final validation and integration evidence

- PR: #65 `Implement EEA source family V1`;
- validated branch head: `28caaa92a8b4e357e29d84e9a06a8ea0331060c6`;
- final merge-candidate ref: `457ff3d4fcc1df603fe5954e8cf8751017d6d657`;
- final validation run: `32656948133`;
- job: `97237068273`;
- runner: Ubuntu 24.04.4, Azure `westcentralus`;
- Python: `3.13.15`;
- `HARNESS PASS`;
- runtime health: `PASS`;
- repository isolated suite: **399/399 PASS**;
- validation artifact metadata: ID `9497690418`, SHA-256 `d30daa8444c18290d7c972874627daa5da1a858875c7351c6af624fbe2537f1d`;
- validation artifact was not downloaded into chat context;
- clean pre-merge concurrency check: branch behind `0` commits;
- PR #65 squash merge commit: `4e59ab7488e663e8157392b2677cee6c418b9ac1`.

## Acceptance criteria

- [x] exact EEA query locator and acquired bytes frozen with SHA-256;
- [x] benchmark sample independently inspected and gold expectations committed;
- [x] source-specific adapter rejects malformed/unsupported structures and semantics explicitly;
- [x] no unsupported semantic reinterpretation of monitoring fields;
- [x] strict and partial benchmark metrics measured with zero incorrect emitted fields;
- [x] public network is not a permanent CI dependency;
- [x] docs/index/technical debt updated;
- [x] harness PASS, runtime health PASS and every isolated repository test PASS;
- [x] branch zero commits behind `main` before merge;
- [x] squash merge completed;
- [x] completed plan archived and `CURRENT-WORK` reset to none through the housekeeping PR.

## Remaining bounded debt

1. official source discovery V1 using NHTSA vPIC plus the existing FuelEconomy.gov menu flow, with discovery treated as candidate generation rather than identity proof;
2. Inmetro PBEV machine-readable/document characterization only when Brazilian coverage becomes active need;
3. recurring robots/rate/politeness and host pacing before broad scheduled live acquisition;
4. stronger network target binding before arbitrary untrusted locators;
5. broader production source distribution/corpus coverage only through independently inspected source-family evidence, including any future EEA fuel-mode expansion or canonical identity use.

## Decision classification

- EEA dataset/API ownership, publication and field definitions: `EVIDENCE_BACKED`;
- exact live acquisition and frozen bytes: `LOCALLY_VERIFIED`;
- promoted/non-promoted field mappings: `ENGINEERING_CHOICE` constrained by source semantics;
- production-wide European coverage/identity resolution quality: `UNKNOWN`.
