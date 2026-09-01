# PODIUM7 Productive Coverage Wave 01 — verified single-source patch plan

Status: prepared / not applied

Purpose: define the exact evidence mutation for the 10 `VERIFIED_SINGLE_SOURCE` record-sides identified by Wave 01 without mixing benchmark mutation into the blocker-classification PR.

This document is an execution plan, not a claim that the benchmark has already changed.

## Guardrails

- apply in a separate evidence-mutation branch/PR after the classification change is authoritative;
- do not modify vehicle values, expected outcomes, source definitions, rationales, thresholds, or source qualification;
- add only explicit `fieldSourceIds` supported by the retained source review;
- do not add attribution for the 36 `COMPOSITE_SUPPORT` sides under the current unique-source replay contract;
- do not add attribution for the 2 `INSUFFICIENT_SINGLE_SOURCE_SUPPORT` sides;
- after mutation, rerun provenance eligibility and all catalog identity/provenance regressions before claiming any replay-count change.

## Expected planning delta

Current executed baseline:

- 60 retained record-sides;
- 12 replayable;
- 48 blocked;
- `MULTI_SOURCE_WITHOUT_EXPLICIT_FIELD_ATTRIBUTION = 48`.

If and only if all 10 patches below validate under the unchanged replay contract, the planning expectation is:

- 22 replayable;
- 38 blocked;
- `EXPLICIT_FIELD_ATTRIBUTION = 10` newly replayable sides;
- `MULTI_SOURCE_WITHOUT_EXPLICIT_FIELD_ATTRIBUTION = 36` blocked sides;
- `MISSING_SIDE_FIELD_ATTRIBUTION = 2` blocked sides.

Why two sides move to `MISSING_SIDE_FIELD_ATTRIBUTION`: the Toyota 10g/12g and Porsche 991/992 cases receive a `fieldSourceIds` object for only the verified right side. Their unpatched left side then correctly fails at the explicit missing-side attribution gate instead of the original no-field-attribution gate.

This is not an executed result.

## Patch set A — `catalog_identity_golden_v1.json`

### 1. `match-porsche-911-992-carrera-4s` — left

Unique retained source:

`porsche-911-generations-2019`

Present fields to attribute:

- `make`
- `model`
- `generation`
- `variant`
- `powertrain`
- `body_style`

Planned mapping:

```json
"left": {
  "make": ["porsche-911-generations-2019"],
  "model": ["porsche-911-generations-2019"],
  "generation": ["porsche-911-generations-2019"],
  "variant": ["porsche-911-generations-2019"],
  "powertrain": ["porsche-911-generations-2019"],
  "body_style": ["porsche-911-generations-2019"]
}
```

### 2. `match-porsche-911-992-carrera-4s` — right

Unique retained source:

`porsche-911-generations-2019`

Present fields to attribute:

- `make`
- `model`
- `generation`
- `variant`
- `powertrain`
- `body_style`
- `aliases`

Planned mapping:

```json
"right": {
  "make": ["porsche-911-generations-2019"],
  "model": ["porsche-911-generations-2019"],
  "generation": ["porsche-911-generations-2019"],
  "variant": ["porsche-911-generations-2019"],
  "powertrain": ["porsche-911-generations-2019"],
  "body_style": ["porsche-911-generations-2019"],
  "aliases": ["porsche-911-generations-2019"]
}
```

### 3. `no-match-toyota-corolla-10g-vs-12g` — right

Unique retained source:

`toyota-corolla-2018-global`

Present fields to attribute:

- `make`
- `model`
- `generation`
- `powertrain`
- `body_style`

Planned mapping:

```json
"right": {
  "make": ["toyota-corolla-2018-global"],
  "model": ["toyota-corolla-2018-global"],
  "generation": ["toyota-corolla-2018-global"],
  "powertrain": ["toyota-corolla-2018-global"],
  "body_style": ["toyota-corolla-2018-global"]
}
```

Do not attribute the left side. The 2006 Toyota source establishes 10th-generation Corolla Axio sedan and a 1.8-liter 2ZR-FE engine but does not explicitly establish the benchmark value `powertrain = "1.8 petrol"` in the retained source review.

### 4. `no-match-porsche-911-991-vs-992` — right

Unique retained source:

`porsche-911-generations-2019`

Present fields to attribute:

- `make`
- `model`
- `generation`
- `variant`
- `powertrain`
- `body_style`

Planned mapping:

```json
"right": {
  "make": ["porsche-911-generations-2019"],
  "model": ["porsche-911-generations-2019"],
  "generation": ["porsche-911-generations-2019"],
  "variant": ["porsche-911-generations-2019"],
  "powertrain": ["porsche-911-generations-2019"],
  "body_style": ["porsche-911-generations-2019"]
}
```

Do not attribute the left side. The retained 991 material does not safely establish every present field, specifically `body_style = "coupe"`, from a declared unique source.

### 5. `review-porsche-911-partial-variant-label` — left

Unique retained source:

`porsche-911-992-powertrain-2019`

Present fields to attribute:

- `make`
- `model`
- `generation`
- `powertrain`

Planned mapping:

```json
"left": {
  "make": ["porsche-911-992-powertrain-2019"],
  "model": ["porsche-911-992-powertrain-2019"],
  "generation": ["porsche-911-992-powertrain-2019"],
  "powertrain": ["porsche-911-992-powertrain-2019"]
}
```

### 6. `review-porsche-911-partial-variant-label` — right

Unique retained source:

`porsche-911-992-powertrain-2019`

Present fields to attribute:

- `make`
- `model`
- `generation`
- `powertrain`

Planned mapping:

```json
"right": {
  "make": ["porsche-911-992-powertrain-2019"],
  "model": ["porsche-911-992-powertrain-2019"],
  "generation": ["porsche-911-992-powertrain-2019"],
  "powertrain": ["porsche-911-992-powertrain-2019"]
}
```

The generic `911 Carrera` label remains a REVIEW identity case; attribution does not change the expected identity outcome.

## Patch set B — `catalog_identity_br_adjacent_incomplete_v1.json`

### 7. `br-hard-no-match-corolla-altis-hybrid-my25-vs-my26` — left

Unique retained source:

`toyota-connected-services-corolla-my25`

Present fields to attribute:

- `make`
- `model`
- `variant`
- `market`
- `model_year_from`
- `model_year_to`

Planned mapping:

```json
"left": {
  "make": ["toyota-connected-services-corolla-my25"],
  "model": ["toyota-connected-services-corolla-my25"],
  "variant": ["toyota-connected-services-corolla-my25"],
  "market": ["toyota-connected-services-corolla-my25"],
  "model_year_from": ["toyota-connected-services-corolla-my25"],
  "model_year_to": ["toyota-connected-services-corolla-my25"]
}
```

### 8. `br-hard-no-match-corolla-altis-hybrid-my25-vs-my26` — right

Unique retained source:

`toyota-corolla-altis-hybrid-offer-2026`

Present fields to attribute:

- `make`
- `model`
- `variant`
- `market`
- `model_year_from`
- `model_year_to`

Planned mapping:

```json
"right": {
  "make": ["toyota-corolla-altis-hybrid-offer-2026"],
  "model": ["toyota-corolla-altis-hybrid-offer-2026"],
  "variant": ["toyota-corolla-altis-hybrid-offer-2026"],
  "market": ["toyota-corolla-altis-hybrid-offer-2026"],
  "model_year_from": ["toyota-corolla-altis-hybrid-offer-2026"],
  "model_year_to": ["toyota-corolla-altis-hybrid-offer-2026"]
}
```

### 9. `br-hard-no-match-onix-premier-my26-vs-my27` — left

Unique retained source:

`chevrolet-onix-my26-price-list`

Present fields to attribute:

- `make`
- `model`
- `variant`
- `market`
- `model_year_from`
- `model_year_to`

Planned mapping:

```json
"left": {
  "make": ["chevrolet-onix-my26-price-list"],
  "model": ["chevrolet-onix-my26-price-list"],
  "variant": ["chevrolet-onix-my26-price-list"],
  "market": ["chevrolet-onix-my26-price-list"],
  "model_year_from": ["chevrolet-onix-my26-price-list"],
  "model_year_to": ["chevrolet-onix-my26-price-list"]
}
```

### 10. `br-hard-no-match-onix-premier-my26-vs-my27` — right

Unique retained source:

`chevrolet-onix-line-2027`

Present fields to attribute:

- `make`
- `model`
- `variant`
- `market`
- `model_year_from`
- `model_year_to`

Planned mapping:

```json
"right": {
  "make": ["chevrolet-onix-line-2027"],
  "model": ["chevrolet-onix-line-2027"],
  "variant": ["chevrolet-onix-line-2027"],
  "market": ["chevrolet-onix-line-2027"],
  "model_year_from": ["chevrolet-onix-line-2027"],
  "model_year_to": ["chevrolet-onix-line-2027"]
}
```

## Expected blocker transition after application

Because `fieldSourceIds` is case-scoped, partial case attribution is intentional in exactly two cases.

Expected post-mutation distribution under the current implementation:

```text
records = 60
replayable = 22
blocked = 38

replayableByMethod:
  SOLE_CASE_SOURCE = 12
  EXPLICIT_FIELD_ATTRIBUTION = 10

blockedByReasonCode:
  MULTI_SOURCE_WITHOUT_EXPLICIT_FIELD_ATTRIBUTION = 36
  MISSING_SIDE_FIELD_ATTRIBUTION = 2
```

The two `MISSING_SIDE_FIELD_ATTRIBUTION` sides are:

- `no-match-toyota-corolla-10g-vs-12g:left`;
- `no-match-porsche-911-991-vs-992:left`.

Any different distribution requires inspection before the patch can be accepted. Do not rewrite attribution merely to force these expected counts.

## Mandatory validation for the separate mutation PR

At minimum:

1. load all changed benchmark files through `load_catalog_identity_benchmark`;
2. run `measure_operational_provenance_eligibility` on the three-dataset wave scope;
3. assert total record-sides remain 60;
4. assert exactly 10 new sides become replayable via `EXPLICIT_FIELD_ATTRIBUTION` if the planned mappings are accepted;
5. assert `SOLE_CASE_SOURCE = 12` remains unchanged;
6. assert no previously replayable side becomes blocked;
7. assert blocker distribution is exactly 36 multi-source-without-attribution + 2 missing-side-attribution;
8. run catalog identity golden tests unchanged;
9. run field-provenance validation;
10. run operational replay/corpus tests;
11. remeasure published vehicle/field coverage and conflicts before claiming product coverage improvement;
12. require exact-head hosted CI when GitHub Actions is capable of executing repository steps.

Any failure that shows a planned source does not support a present field invalidates that side's patch; do not substitute another source merely to retain the expected count.
