# Field Source Provenance V1 execution plan

Status: active

Parent mission: #139
Issue: #144
Related measurement: #141

## Documentation basis

`PRODUCTION-QUALITY-MEASUREMENT-V2.md` records a concrete instrumentation gap: current `podium7.catalog-identity-golden.v1` cases bind sources only at case level, so source contribution by catalog dimension cannot be measured without inventing attribution. `CATALOG-EVIDENCE-POLICY-V2.md` requires auditable evidence/provenance and forbids silent semantic fusion.

## Outcome

Add an additive field-level source attribution contract to the existing catalog identity benchmark schema and a deterministic measurement that reports source contribution by dimension only where attribution is explicit.

## Acceptance

- existing benchmark files remain valid unchanged;
- `fieldSourceIds.left/right.<identity field>` may explicitly list one or more case-declared sources;
- malformed, unknown, duplicate, absent-field, or out-of-case attribution fails closed;
- loaded benchmark cases preserve the explicit mapping;
- benchmark reports expose the mapping;
- quality measurement reports total present fields, explicitly attributed fields, attribution coverage, unattributed counts, and source contribution by dimension;
- no case-level source list, rationale, source description, or lexical semantics are used to infer field provenance;
- resolver/evidence/fusion/publication policy is unchanged.

## Validation

1. focused deterministic tests for valid and legacy cases;
2. malformed attribution tests for every fail-closed boundary;
3. repository harness/sequential validation when executable runners are available;
4. no historical benchmark backfill without separately inspectable retained evidence.

## Non-goals

- This block does not assert that the existing 72-record corpus already has complete field-level attribution.
- It does not change source strength or canonical identity semantics.
- It does not create a new external source family.
- It does not derive field attribution from case-level `sourceIds`.
