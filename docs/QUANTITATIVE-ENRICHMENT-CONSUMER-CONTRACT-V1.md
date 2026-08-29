# Quantitative Enrichment Consumer Contract V1

Status: candidate public consumer contract for issue #221.

## Purpose

Publish evidence-backed technical facts for consumers such as BPT2 without exposing Podium persistence, candidate storage, raw acquisition internals, or the frozen Catalog JSON `2.0` shape.

This contract is separate from Catalog JSON `2.0`. It does not change automotive identity resolution, evidence policy, fusion, source policy, or public catalog identity semantics.

## Envelope

Schema identifier:

`podium7.quantitative-enrichment.v1`

A payload contains:

- `schema`: exact contract schema identifier;
- `vehicleId`: stable Podium vehicle/configuration identity supplied by the publication boundary;
- `revision`: SHA-256 over the canonical semantic payload (`schema`, `vehicleId`, ordered facts and unresolved conflicts); unchanged semantic state produces the same revision;
- `facts`: deterministic field-ordered list of published facts;
- `conflicts`: deterministic field-ordered list of unresolved publication conflicts.

The revision is a publication-state identifier, not a timestamp and not a claim that the underlying evidence is globally complete.

## Frozen V1 field vocabulary

V1 exposes only quantitative fields already represented in retained extraction evidence:

- `displacement`;
- `power`;
- `torque`;
- `length`;
- `width`;
- `height`;
- `wheelbase`;
- `curb_weight`;
- `fuel_economy_combined`.

Unknown field identifiers fail closed. Expanding this vocabulary is a public-contract change and requires evidence-backed semantics.

## Fact contract

Every fact contains:

- `field`: one of the frozen V1 field identifiers;
- `knowledgeState`: `known`, `unknown`, or `not_applicable`;
- `provenanceRef`: stable producer-side reference sufficient to audit the publication decision without requiring the consumer to read raw acquisition storage.

A `known` fact also contains:

- `valueShape`: `scalar`, `range`, `limit`, or `multiple`;
- `value`: strict JSON-compatible typed value whose structure matches `valueShape`;
- `unit`: mandatory for V1 quantitative fields;
- optional `context` with `market`, `applicability`, and/or `methodology` when those qualifiers are material to interpretation.

`unknown` and `not_applicable` are semantic states, not special numeric/string values. They cannot carry a value, value shape, or unit.

## Unresolved conflict contract

An unresolved conflict contains:

- `field`;
- at least two unique `provenanceRefs`;
- a non-empty producer-side `reason`.

A field cannot appear simultaneously in `facts` and `conflicts`. If evidence for a field remains unresolved, publication fails closed for a canonical value while preserving the conflict explicitly in the envelope.

## Shape semantics

### scalar

One JSON scalar value. For V1 quantitative fields the scalar must be numeric. The producer must not use this shape to flatten a retained range, limit, or multiple value.

### range

Exactly:

```json
{"minValue": 1490, "maxValue": 1508}
```

Bounds must be numeric and `minValue <= maxValue`.

### limit

Exactly `operator` plus numeric `value`. V1 reserves `lt`, `lte`, `gt`, and `gte` as operators. Representational support does not assert that a retained publication-ready limit example currently exists.

### multiple

A non-empty JSON list. For V1 quantitative fields every item must be numeric. Representational support does not authorize concatenating semantically different measurements into one field.

## Unit semantics

Every `known` V1 fact requires a non-empty unit. Units remain part of fact meaning and are not inferred by the consumer.

## Retained range example

The repository already retains the Toyota Corolla Cross 2025 source snapshot with:

`Unladen Weight: | 3285 - 3325 lbs (1490 - 1508 kg)`

`AUTOEVOLUTION_ARTEGA_GT_RULES_V2` preserves this as `curb_weight`, range `{minValue: 1490, maxValue: 1508}`, unit `kg`. The focused contract test maps that already-retained extraction into this public envelope and binds provenance to the retained Git blob. No market/applicability claim, new source, or synthetic measurement is introduced for the example.

## Correction and replay

Facts and conflicts are sorted deterministically before revision computation and serialization. Reordering identical semantic state does not change the payload or revision.

A correction that changes a value, provenance reference, knowledge state, unit, material context, conflict reason, or conflict provenance produces a new revision while preserving the stable `vehicleId`.

Consumers should treat a newer publication revision as replacement current state for the facts/conflicts in that payload. V1 does not define partial patch semantics.

## Fail-closed rules

V1 rejects rather than coerces:

- empty field, vehicle identity, provenance reference, or conflict reason;
- field identifiers outside the frozen V1 vocabulary;
- `known` without a value/value shape/unit;
- `unknown`/`not_applicable` carrying value/shape/unit;
- malformed or reversed ranges;
- unsupported limit operators;
- non-JSON-compatible values;
- non-numeric scalar/multiple values;
- duplicate published fields or duplicate conflicts;
- conflict with fewer than two unique provenance references;
- simultaneous canonical fact and unresolved conflict for the same field.

## Compatibility boundary

Catalog JSON Contract `2.0` remains unchanged.

V1 is additive as a separate publication surface. Consumers must match the exact `schema` they support. Any incompatible envelope/fact/conflict semantic change requires a new contract version rather than silent reinterpretation.

## Nonclaims

This contract does not prove:

- production-wide enrichment coverage;
- Comparator readiness;
- cross-market comparability of similarly named facts;
- that all V1 representational states/shapes have retained publication-ready examples;
- authorization for BPT2 schema, UI, filtering, Saved Search, or ranking changes.

BPT2 Comparator remains gated on integration of this contract plus usable evidence-backed coverage and field-specific comparability semantics.
