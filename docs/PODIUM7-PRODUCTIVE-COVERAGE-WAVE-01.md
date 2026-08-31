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

## Evidence-review finding 01

The retained corpus contains at least two materially different situations inside the current `MULTI_SOURCE_WITHOUT_EXPLICIT_FIELD_ATTRIBUTION` bucket.

1. `ATTRIBUTION_METADATA_MISSING_BUT_SINGLE_SOURCE_PER_RECORD_SIDE_PLAUSIBLE`
   - example: `no-match-toyota-corolla-10g-vs-12g` in `catalog_identity_golden_v1.json`;
   - each record-side is associated with a distinct declared source whose retained support statement covers the corresponding generation/product context;
   - this class is a candidate for explicit attribution only after every present field is verified against the retained evidence.

2. `GENUINELY_COMPOSITE_RECORD_SIDE`
   - examples appear in the Mustang, Porsche, Brazil generation/configuration, and adjacent/incomplete slices;
   - retained source-support statements intentionally distribute generation, variant, model-year, or mechanical facts across different sources;
   - no `fieldSourceIds` value may be invented merely to make the record replayable.

The second class exposes an operational-replay boundary: the benchmark/provenance model can represent valid field-level attribution from multiple sources, while `unique_source_for_record` currently requires exactly one source common to every present field before operational replay.

A focused test on the current wave branch freezes this boundary: a synthetically valid field-attributed record with `make/model` from one source and `generation` from another remains blocked as `NO_UNIQUE_COMMON_SOURCE`.

Therefore:

`FIELD_ATTRIBUTION_COMPLETE != OPERATIONAL_REPLAYABLE`

and

`MULTI_SOURCE_EVIDENCE != INVALID_EVIDENCE`

This prevents the wave from treating all 48 blocked record-sides as a data-cleanup task.

## First implementation question

For each of the 48 blocked record-sides, determine whether the retained evidence can support explicit field attribution without inference. A case may become replayable only if its present fields have a valid unique common source under the existing operational-replay contract. If evidence is genuinely multi-source with no single source supporting every present field, it remains blocked unless a separately justified replay design can preserve per-field provenance without collapsing evidence semantics.

## Decision boundary

Do not redesign operational replay until the 48 record-sides are classified into:

- evidence-valid single-source-per-side candidates;
- genuinely composite, correctly multi-source observations;
- insufficiently supported observations that must remain blocked.

If a material portion of valid observations is genuinely composite, the limiting factor is replay design rather than missing attribution metadata. At that point the wave transitions to `DECISION_REQUIRED` before implementation of any multi-source replay path.

## Exit states

- `COMPLETE`: coverage improved and all required local/remote validation applicable to the wave is green;
- `COMPLETE_EXTERNAL_VALIDATION_PENDING`: internal evidence is complete but hosted validation remains externally blocked;
- `DECISION_REQUIRED`: evidence proves the current replay contract, not missing attribution data, is the limiting factor and a product/architecture decision is required;
- `REJECTED_BY_EVIDENCE`: attempted coverage change would require inference, semantic weakening, or unsupported source claims.
