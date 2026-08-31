# PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01

Status: active measurement-first product-evolution wave

## Objective

Increase replayable, evidence-backed coverage for the retained Brazil-relevant catalog corpus without weakening identity, provenance, field attribution, conflict handling, source qualification, or fail-closed semantics.

## Frozen baseline before mutation

Measurement scope used by `tests/test_catalog_identity_field_coverage.py`:

- datasets: `catalog_identity_golden_v1.json`, `catalog_identity_golden_br_v1.json`, `catalog_identity_br_adjacent_incomplete_v1.json`;
- retained record-sides: 60;
- replayable record-sides: 12;
- blocked record-sides: 48;
- replay method for current replayable records: `SOLE_CASE_SOURCE`;
- current retained V3 field-attribution coverage: `0.0` according to `tests/test_catalog_field_provenance.py`;
- published consumer vehicles in the previously executed retained-scope measurement: 4;
- measured published-field coverage from that execution: `body_style=1.0`, `powertrain=1.0`, `transmission=0.5`.

The last two published-output metrics are retained execution evidence and must be re-executed before claiming a new final value.

## Frozen root-cause taxonomy

The taxonomy is defined before corpus mutation from the existing fail-closed branches in `unique_source_for_record`:

- `MULTI_SOURCE_WITHOUT_EXPLICIT_FIELD_ATTRIBUTION`
- `MISSING_SIDE_FIELD_ATTRIBUTION`
- `MISSING_PRESENT_FIELD_ATTRIBUTION`
- `NO_UNIQUE_COMMON_SOURCE`
- `INVALID_CASE_SOURCE_ATTRIBUTION`
- `UNKNOWN_CASE_SOURCE`
- `INVALID_FIELD_ATTRIBUTION`
- `UNKNOWN_FIELD_SOURCE`

For the current 48 blocked record-sides in the three-dataset coverage scope, repository tests already constrain the observed reason to multiple case-level `sourceIds` without explicit field attribution. Therefore the current measured first bucket is:

`MULTI_SOURCE_WITHOUT_EXPLICIT_FIELD_ATTRIBUTION = 48`

No other bucket is assigned a positive count without an executed measurement.

## Invariants

- `CONTRACT_READY != DATA_READY != PRODUCT_READY`
- `MORE_SOURCE != MORE_COVERAGE`
- `UNKNOWN != ZERO`
- `CONFLICT != FACT`
- no synthetic attribution;
- no source-semantic reinterpretation;
- no threshold reduction for count gain;
- no new source family until existing-evidence closure is shown insufficient.

## Required measurements

Before and after each mutation, record:

- total record-sides;
- replayable and blocked record-sides;
- blocked count by frozen root-cause code;
- published vehicle count;
- identity-field coverage;
- provenance / field-attribution completeness;
- quantitative-envelope coverage by field and knowledge state;
- unresolved conflict count;
- vehicles with N known quantitative fields;
- market and source-family distribution.

## First implementation question

For each of the 48 blocked record-sides, determine whether the retained evidence can support explicit field attribution without inference. A case may become replayable only if its present fields have a valid unique common source under the existing operational-replay contract. If evidence is genuinely multi-source with no single source supporting every present field, it remains blocked unless a separately justified replay design can preserve per-field provenance without collapsing evidence semantics.

## Exit states

- `COMPLETE`: coverage improved and all required local/remote validation applicable to the wave is green;
- `COMPLETE_EXTERNAL_VALIDATION_PENDING`: internal evidence is complete but hosted validation remains externally blocked;
- `DECISION_REQUIRED`: evidence proves the current replay contract, not missing attribution data, is the limiting factor and a product/architecture decision is required;
- `REJECTED_BY_EVIDENCE`: attempted coverage change would require inference, semantic weakening, or unsupported source claims.
