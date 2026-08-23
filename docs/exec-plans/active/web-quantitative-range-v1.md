# Web bounded quantitative value V1

Status: active — implementation complete; final merge-candidate validation/integration pending

## Outcome

Represent an observed bounded automotive quantitative value without inventing a scalar, using explicit lower/upper bounds with the existing canonical unit and preserving raw source evidence.

## Acceptance criteria

- keep the historical source-family V1 benchmark reproducible;
- add a versioned reusable extraction artifact that handles scalar and bounded `curb_weight` values explicitly;
- normalize bounded curb weight as JSON `{"minValue": ..., "maxValue": ...}` with unit `kg` and a reproducible rule id;
- reject reversed, non-finite, malformed, or unsupported bounded values explicitly;
- preserve exact raw source text and observed source label;
- do not use midpoint/minimum/maximum as a fabricated scalar substitute;
- add a new benchmark version rather than rewriting historical V1 expectations;
- verify persistence/domain compatibility and keep Catalog JSON Contract 2.0 unchanged;
- update design/debt documentation and integrate only with green CI.

## Evidence basis

- frozen Toyota source: `Unladen Weight: | 3285 - 3325 lbs (1490 - 1508 kg)`;
- frozen Nissan source: `Unladen Weight: | 4334 - 4489 lbs (1966 - 2036 kg)`;
- Schema.org `QuantitativeValue` explicitly models ranges through `minValue` and `maxValue`, including automotive quantitative properties;
- GoodRelations defines a quantitative value as a numerical interval with lower/upper bounds and unit of measurement and gives weight ranges as an example;
- QUDT 3.5.0 remains useful for quantity/unit vocabulary but its current core schema did not provide the range representation used for this decision;
- Podium `CandidateFact.normalized_value` and `CanonicalFact.accepted_value` already accept strict JSON values, catalog persistence stores them as JSON, and Catalog JSON Contract 2.0 explicitly maps only catalog identity fields.

## Decision classification

- preserving source range rather than collapsing it to one scalar: `EVIDENCE_BACKED` direction;
- internal JSON keys `minValue`/`maxValue` and dedicated bounded normalization rule: `ENGINEERING_CHOICE`, aligned with established quantitative-value vocabularies;
- limiting the first bounded normalizer to `curb_weight`: `ENGINEERING_CHOICE` to avoid unsupported generalization.

## Boundaries

- no historical candidate replay;
- no heterogeneous-web claim;
- no public contract version change;
- no assumption that every quantity attribute supports ranges;
- no claim that every intermediate numeric value corresponds to a distinct vehicle configuration.

## Implemented behavior

- historical `AUTOEVOLUTION_ARTEGA_GT_RULES_V1` remains explicitly addressable and historical benchmark evaluators use it directly;
- current `AUTOEVOLUTION_ARTEGA_GT_RULES_V2` adds a bounded parser only for `curb_weight` while preserving scalar behavior;
- `normalize_bounded_fact()` normalizes each bound independently, rejects reversed/non-finite/unsupported values, and emits `{"minValue": ..., "maxValue": ...}` in canonical `kg`;
- validated reusable artifacts may declare `range_parser` only for `curb_weight`, with exactly two capture groups and supported curb-weight source units;
- raw text and exact source label remain on extracted facts;
- additive bounded gold lives in `benchmarks/web_extraction_bounded_values_v1.json`; historical V1 gold is unchanged;
- bounded candidate/canonical JSON values round-trip through persistence/fusion without changing Catalog JSON Contract 2.0;
- CLI supports strict and partial V2 reproduction through `--bounded-values`.

## Measured result

On the frozen 12-configuration source-family corpus:

- historical strict V1 remains 8/12 pages, 96/96 correct emitted fields, 96/142 field recall;
- historical partial V1 remains 140/140 correct emitted fields, 140/142 retained-field recall;
- strict V2 succeeds on 10/12 pages, emits 120/120 correct fields, and recalls 120/142 source target fields;
- partial-evidence V2 retains 142/142 source target fields, emits 142/142 correct fields, has zero incorrect emitted fields and zero unresolved source target fields;
- the two remaining strict failures correspond to genuinely absent source fields, not unsupported range semantics.

## Validation evidence

Green implementation merge-candidate CI before final documentation closeout:

- PR: #51 `Represent bounded curb weight without scalar collapse`;
- run `32646934156`, job `97212517296`;
- PR merge ref SHA `0b9f5859c1c747a23d9a3f4a2610e33dc0269ebd`;
- branch head validated: `82a613a0509040d7ef376b9bff0883d36cb4bf20`;
- Python `3.13.15`;
- `HARNESS PASS`;
- runtime health `PASS`;
- repository isolated suite `335/335` PASS;
- validation artifact ID `9495119435`, ZIP SHA-256 `4becc996f2f7d001e306f252c75ed652d31406c531cde6a87585fd97207deba7`.

The documentation/debt closeout commits after that run do not change executable behavior. Final integration still requires green CI on the resulting merge candidate plus the normal concurrency/self-review gate.
