# EEA Source Family V1

Status: active

## Outcome

Implement a bounded third structured automotive source family from the European Environment Agency passenger-car CO2 monitoring dataset. The implementation must be driven by frozen official evidence and independent gold expectations, not by nominal schema richness.

## Evidence boundary

Primary dataset: EEA Monitoring of CO2 emissions from passenger cars under Regulation (EU) 2019/631.

Current selected table at work start: `[CO2Emission].[latest].[co2cars_2025Pv31]`, 2025 provisional data published 2026-06-25.

Discodata documents SQL-over-HTTPS JSON access through `/sql`, with JSON records under `results`.

EEA rows are registration/type-approval monitoring observations. Type, variant and version fields are preserved as source identifiers/evidence; they are not silently redefined as globally unique retail trims.

## Work

1. Acquire a bounded deterministic live sample with the existing Direct HTTP policy and retain the exact query locator, bytes and SHA-256.
2. Inspect the sample independently and freeze benchmark expectations separately from extraction logic.
3. Implement a source-specific structured JSON adapter with explicit required/optional field semantics and stable issues.
4. Normalize only already-supported Podium facts whose units/meaning align: curb weight kg, displacement cc, power kW and fuel type where the source value is semantically supported.
5. Preserve EEA identity/support fields such as member state, make, commercial name, manufacturer, type-approval number, type, variant, version and registration year without claiming they prove canonical retail identity.
6. Characterize strict and partial evidence correctness on the frozen sample, including missing source values.
7. Add deterministic tests, durable documentation, benchmark/snapshot lineage and technical-debt updates.
8. Remove temporary public-network workflow after evidence capture; permanent CI must remain deterministic/offline.
9. Self-review, green merge-candidate CI, concurrency recheck, squash merge, then archive this plan and clear CURRENT-WORK.

## Acceptance

- [ ] exact EEA query locator and acquired bytes frozen with SHA-256;
- [ ] benchmark sample independently inspected and gold expectations committed;
- [ ] source-specific adapter rejects malformed/ambiguous structures explicitly;
- [ ] no unsupported semantic reinterpretation of monitoring fields;
- [ ] strict and partial benchmark metrics measured with zero incorrect emitted fields;
- [ ] public network is not a permanent CI dependency;
- [ ] docs/index/technical debt updated;
- [ ] harness PASS, runtime health PASS and every isolated repository test PASS;
- [ ] branch zero commits behind main before merge;
- [ ] squash merge completed;
- [ ] completed plan archived and CURRENT-WORK reset to none in housekeeping PR.

## Decision classification

- EEA dataset/API ownership, publication and field definitions: `EVIDENCE_BACKED`;
- exact live acquisition and frozen bytes: `LOCALLY_VERIFIED`;
- adapter field selection/mapping: `ENGINEERING_CHOICE` constrained by source semantics;
- production-wide European coverage/identity resolution quality: `UNKNOWN`.
