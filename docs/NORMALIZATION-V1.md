# Podium 7 Normalization V1

**Work unit:** `PODIUM7_NORMALIZATION_V1`

## Scientific basis

MaDI-Bench treats value normalization as a distinct integration stage. The supplied handoff also requires preservation of `rawValue`, `normalizedValue`, and `normalizationRule`.

## Decision classification

### `EVIDENCE_BACKED`

- Normalization is logically separate from entity resolution and fusion.
- Raw source values must remain available after normalization.
- Normalization must be reproducible through an explicit rule identifier.

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

## Preservation

`CandidateFact.raw_value` always keeps the acquired structured value. `CandidateFact.normalized_value`, `unit`, and `normalization_rule` contain the reproducible normalized representation.

## Gate

- `RAW_PRESERVED = YES`
- `NORMALIZED_VALUE_REPRODUCIBLE = YES`
- `UNIT_TESTS = PASS (16/16 repository tests run individually; 10 normalization + 6 domain)`

Two incorrect expected constants in the newly written tests were detected during individual execution and corrected before the gate was closed.
