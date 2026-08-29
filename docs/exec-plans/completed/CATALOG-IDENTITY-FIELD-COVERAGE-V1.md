# Catalog Identity Field Coverage V1

Status: completed

## Outcome

Measured consumer-visible coverage of `powertrain`, `transmission`, and `body_style` through the existing Production Corpus V2 ingestion/resolution/consumer path before any downstream BPT2 field decision.

## Integrated scope

- full consumer pagination, including a regression beyond the 100-item page ceiling;
- contract-strict known versus JSON `null` handling;
- raw/normalized cardinality and normalization-collision reporting;
- market breakdown plus exact-code `BR` slice;
- isolated per-dataset evidence slices through the same operational path;
- dataset schema/version/SHA-256 binding;
- aggregate review evidence without invented field-level attribution;
- deterministic CLI JSON output, including deterministic ordering for case-only raw variants;
- standalone CLI bootstrap proven without site packages.

No resolver policy, source-family policy, BPT2 schema/filter, semantic taxonomy, or arbitrary readiness threshold was introduced.

## Integrated evidence

PR #176 integrated by squash as commit `9a541d0c073d4c0094ec5b6b3cd0d5112519a737`.

Final validated PR head: `fac573619ef14924ea44f639f0fa3d8bb6d433e9`.

Fresh pull-request workflow `33224951642` ran against base `e28ae01486c31dcaaedae90dbf15bed708f2d6aa` and passed:

- `tests`;
- `minimum-python` (Python 3.11);
- secret hygiene;
- repository Harness;
- project facts;
- runtime health;
- package build/install;
- every test in isolation in both jobs;
- validation evidence upload.

Review found and the final head fixed two defects: clean-checkout standalone CLI import and nondeterministic ordering for case-only raw variants. All review threads were resolved before integration.

## Bounded measurement

Retained corpus consumer output: 21 published Vehicles.

- `powertrain`: 17/21 present (`80.95%`);
- `transmission`: 11/21 present (`52.38%`);
- `body_style`: 17/21 present (`80.95%`).

Exact-code `BR` slice: 13 Vehicles.

- `powertrain`: 9/13 present (`69.23%`);
- `transmission`: 9/13 present (`69.23%`);
- `body_style`: 9/13 present (`69.23%`).

These figures are retained-corpus measurements, not production-wide completeness estimates and not a readiness threshold for downstream schema or filtering.

## Downstream boundary

`CATALOG_IDENTITY_FIELD_COVERAGE = MEASURED_BOUNDED_EVIDENCE`

The measurement gate requested by the BPT2 consumer boundary is complete. Downstream adoption remains a separate consumer decision and must not infer readiness from field existence or these percentages alone.
