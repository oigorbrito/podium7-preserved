# ADR-0002: Operational replay with multi-source field provenance

- Status: Proposed / `DECISION_REQUIRED`
- Date: 2026-08-31
- Decision class: `PRODUCT_ARCHITECTURE_CHOICE`
- Trigger: `PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01`

## Context

Podium 7 currently converts provenance-eligible benchmark record-sides into operational batch records containing exactly one `source`, one `evidence` object, and one `vehicle` object.

The retained benchmark model is more expressive: `fieldSourceIds` can attribute different present fields to different declared sources. The current operational eligibility contract nevertheless requires one source to be common to every present field before replay.

Wave 01 classified the 48 currently blocked record-sides as:

- 36 `COMPOSITE_SUPPORT`;
- 10 `VERIFIED_SINGLE_SOURCE`;
- 2 `INSUFFICIENT_SINGLE_SOURCE_SUPPORT`.

Therefore the dominant blocker is not malformed attribution metadata. A material majority of the retained blocked observations are structurally multi-source.

Under the unchanged unique-source replay contract, the 10 verified single-source sides define an immediate data-completion lane, but the remaining valid composite observations cannot become replayable without either losing provenance semantics or changing the operational replay representation.

## External reference model

This ADR does not require Podium 7 to adopt RDF, OWL, or the W3C PROV serialization formats.

W3C PROV is used only as an architecture reference because it treats provenance as information about the entities, activities, and agents involved in producing data, and provides qualified relations for representing more detailed influence/attribution rather than requiring all provenance to collapse to one origin.

References:

- https://www.w3.org/TR/prov-dm/
- https://www.w3.org/TR/prov-o/
- https://www.w3.org/TR/prov-primer/

The relevant principle for Podium 7 is narrower: a derived record may preserve multiple contributing evidence entities and their roles at field granularity.

## Existing contract

Current operational batch input is intentionally simple:

```text
record
  recordId
  source      -> exactly one Source
  evidence    -> exactly one RawEvidence bound to source.id
  vehicle     -> vehicle fields
```

`CatalogBatchEnvelope` and `ingest_catalog_record` are built around that single source/evidence pair.

Current provenance eligibility therefore admits either:

- `SOLE_CASE_SOURCE`; or
- `EXPLICIT_FIELD_ATTRIBUTION` only when exactly one source is common to all present fields.

A fully attributed record-side whose fields are validly split across two sources remains `NO_UNIQUE_COMMON_SOURCE`.

## Decision to make

Choose one of two admissible policies.

### Option A — `KEEP_UNIQUE_SOURCE_REPLAY`

Keep the current operational envelope and unique-common-source requirement.

Consequences:

- complete the 10 verified single-source record-sides;
- composite observations remain non-replayable by design;
- operational replay stays simple and backwards compatible;
- retained-scope replayability has a known ceiling unless future qualified evidence supplies a genuine common source;
- benchmark field attribution may still improve even when replayability does not.

This option is conservative and low-risk, but accepts that valid multi-source evidence is outside operational replay.

### Option B — `PRESERVE_FIELD_LEVEL_MULTI_SOURCE_REPLAY`

Extend operational replay so every present vehicle field can retain one or more qualified evidence/source references, without manufacturing a record-level unique source.

The design may introduce a new envelope/schema version, but MUST preserve the current v1 path for existing single-source inputs during migration.

Minimum semantic shape:

```text
record
  recordId
  vehicle
  provenance
    sources[]
    evidence[]
    fieldEvidence
      <vehicle-field> -> one-or-more evidence/source references
```

The exact serialization is intentionally not selected by this proposed ADR.

## Non-negotiable invariants for Option B

A multi-source replay implementation MUST satisfy all of the following:

1. No synthetic source
   - never create a fake aggregate source merely to satisfy the existing envelope.

2. Field-complete provenance
   - every present vehicle field must have explicit evidence attribution before replay.

3. Qualified-source preservation
   - source qualification/authority rules continue to apply per attributed field.

4. Conflict preservation
   - conflicting evidence must remain conflict/review evidence; aggregation must not turn disagreement into fact.

5. Determinism
   - canonical source/evidence ordering and stable identifiers must make equivalent inputs replay identically.

6. Fail closed
   - unknown source/evidence identifiers, missing field attribution, invalid references, or unresolved required provenance prevent replay rather than selecting a source heuristically.

7. No evidence duplication semantics
   - the same evidence may support several fields, but repeated references must not be interpreted as independent corroborating sources.

8. Backwards compatibility
   - existing single-source operational records remain valid during a versioned migration path.

9. Traceability after ingestion
   - field-level provenance must remain reconstructable after catalog ingestion/merge/review; accepting a multi-source envelope and then discarding the field mapping is not sufficient.

10. Measurement separation
   - field-attribution completeness and operational replayability remain separate metrics.

## Required tests before Option B implementation can be accepted

At minimum, regressions must cover:

- two-source record with complete field attribution replays without requiring a common source;
- two-source record missing attribution for one present field fails closed;
- unknown source ID fails closed;
- unknown evidence ID fails closed;
- evidence/source mismatch fails closed;
- duplicate source/evidence references are canonicalized or rejected deterministically;
- conflicting attributed values still route through existing conflict/review behavior;
- supporting-only source cannot be silently promoted where authoritative evidence is required;
- single-source v1 record produces behavior equivalent to its v2/multi-source representation;
- provenance remains queryable/reconstructable after CREATE, MATCH, and REVIEW outcomes;
- metrics distinguish `FIELD_ATTRIBUTION_COMPLETE` from `OPERATIONAL_REPLAYABLE`.

## Migration constraints

If Option B is chosen:

1. define the new envelope/domain contract before changing the retained benchmark;
2. add parser/domain validation and negative tests first;
3. add ingestion persistence/traceability second;
4. add operational-provenance builder support third;
5. migrate a small representative composite fixture before broad corpus mutation;
6. remeasure replayability, publication, conflicts, and provenance completeness;
7. preserve the old single-source path until equivalence tests are green.

Do not perform a flag-day schema replacement.

## Evidence-mutation work independent of this decision

The 10 `VERIFIED_SINGLE_SOURCE` sides do not require Option B. They can receive explicit field attribution in a separate evidence-mutation change set after the blocker-classification PR is validated/integrated.

The two insufficient sides remain blocked unless existing retained evidence can be strengthened without inference or a separately qualified source change is justified.

## Rejected shortcuts

The following are not admissible decisions:

- choose the first source in `sourceIds`;
- choose the source covering the largest number of fields;
- assign all fields to the highest-authority source even when it does not support them;
- create a synthetic aggregate source/evidence object;
- discard field-level provenance after replay;
- lower replay thresholds to increase coverage;
- treat `fieldSourceIds` completeness as proof of conflict-free identity.

## Decision criteria

The final choice should be based on:

- whether composite retained observations are intended to participate in operational/product replay;
- implementation and persistence complexity;
- auditability and evidence reconstruction requirements;
- backwards compatibility risk;
- effect on conflict semantics and source qualification;
- expected product value of moving beyond the unique-source replay ceiling.

## Current recommendation status

No option is accepted by this ADR yet.

Evidence establishes that Option B is technically justified if the product requires replay of the 36 valid composite sides. Option A remains valid if Podium 7 deliberately defines operational replay as a stricter single-source subset of the retained evidence model.

Implementation of multi-source replay is blocked until this ADR moves from `Proposed / DECISION_REQUIRED` to an accepted decision.
