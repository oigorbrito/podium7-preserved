# Podium 7 Normalization V1

**Work unit:** `PODIUM7_NORMALIZATION_V1`

## Scientific basis

MaDI-Bench treats value normalization as a distinct integration stage. The supplied handoff also requires preservation of `rawValue`, `normalizedValue`, and `normalizationRule`.

For bounded quantitative values, the implementation follows an evidence-preserving direction consistent with established product vocabularies rather than inventing a scalar. Schema.org `QuantitativeValue` supports `minValue` and `maxValue` for ranges, including automotive quantitative properties. GoodRelations defines a quantitative value as a numerical interval with lower and upper bounds plus a unit of measurement and explicitly uses weight ranges as an example.

Primary references:

- Schema.org `QuantitativeValue`: https://schema.org/QuantitativeValue
- GoodRelations language reference, `gr:QuantitativeValue`: https://www.heppnetz.de/ontologies/goodrelations/v1.html

## Decision classification

### `EVIDENCE_BACKED`

- Normalization is logically separate from entity resolution and fusion.
- Raw source values must remain available after normalization.
- Normalization must be reproducible through an explicit rule identifier.
- A source-observed quantitative interval must remain an interval unless separate evidence justifies a point value; midpoint or endpoint substitution would discard source semantics.

### `ENGINEERING_CHOICE`

Canonical units in v1 are:

- power: `kW`
- torque: `Nm`
- displacement: `cc`
- dimensions: `mm`
- curb weight: `kg`
- fuel consumption: `L/100km`

Text normalization uses stable lowercase tokens for fuel, transmission, and drivetrain.

Mechanical horsepower uses `1 hp = 0.7456998716 kW`; pound-foot uses `1 lb-ft = 1.3558179483314 Nm`; inch uses `25.4 mm`; pound uses `0.45359237 kg`; US mpg uses `235.214583 / mpg` to derive L/100km. These are deterministic implementation choices for v1 and are not presented as conclusions from the scientific corpus.

Bounded curb weight uses strict JSON:

```json
{"minValue": 1490, "maxValue": 1508}
```

with canonical unit `kg` and normalization rule `curb_weight.bounded_to_kg.v1`. The first bounded normalizer is deliberately limited to `curb_weight`; this is not a claim that all Podium quantitative attributes accept ranges. Both bounds are normalized independently with the existing curb-weight unit rules, must be finite, and must satisfy `minValue <= maxValue`.

## Preservation

`CandidateFact.raw_value` always keeps the acquired structured value. `CandidateFact.normalized_value`, `unit`, and `normalization_rule` contain the reproducible normalized representation.

For web-extracted ranges, the exact source text and observed source label remain on the extracted fact. The bounded normalized value is additive evidence; it does not fabricate a scalar weight.

## Compatibility boundary

`CandidateFact.normalized_value` and `CanonicalFact.accepted_value` already accept strict JSON-compatible values, and persistence stores these values as JSON. Therefore the bounded object requires no domain or persistence schema widening.

Catalog JSON Contract `2.0` is unchanged: its serializer explicitly exposes catalog identity fields and does not automatically surface candidate/canonical fact internals.

## Gate

Original scalar normalization gate remains historical evidence.

Bounded-value acceptance requires:

- source interval preserved as lower/upper bounds;
- canonical `kg` normalization reproducible;
- reversed/non-finite/unsupported values rejected explicitly;
- candidate and canonical persistence round-trip;
- no Catalog JSON Contract `2.0` change;
- repository required CI green.
