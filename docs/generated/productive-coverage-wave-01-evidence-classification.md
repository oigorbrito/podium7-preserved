# Productive Coverage Wave 01 — retained-evidence classification

Status: evidence classification, no corpus mutation

Scope: the 48 blocked record-sides from the three-dataset coverage scope frozen in `PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01.md`.

This artifact classifies only what the retained benchmark `sources[].supports`, case fields, case rationales, and retained review-disposition evidence establish without adding external evidence or inferring source ownership from `sourceIds` order.

## Classification semantics

- `SINGLE_SOURCE_PER_SIDE_CANDIDATE`: the retained support descriptions identify one declared source that can account for the present identity fields of that record-side. This is a candidate for explicit `fieldSourceIds`; it is not yet a mutation authorization until field-by-field attribution is encoded and validated.
- `GENUINELY_COMPOSITE_MULTI_SOURCE`: the retained descriptions explicitly distribute present fields across more than one source, so a unique source common to every present field is not supported by the retained evidence. Adding complete field attribution would still leave the current operational replay contract blocked by `NO_UNIQUE_COMMON_SOURCE`.
- `UNRESOLVED_FROM_RETAINED_SUMMARY`: the retained summaries are insufficient to choose either category without source-level review. No attribution is authorized.

## Single-source-per-side candidates

### `catalog_identity_golden_v1.json`

Case `no-match-toyota-corolla-10g-vs-12g`:

- `left` → candidate source `toyota-corolla-2006-global`.
  - retained support: 10th-generation Corolla/Axio sedan and 1.8-liter 2ZR-FE powertrain;
  - present side fields are the 10th-generation Corolla, 1.8 petrol, sedan observation.
- `right` → candidate source `toyota-corolla-2018-global`.
  - retained support: 12th-generation Corolla sedan family and hybrid availability;
  - present side fields are the 12th-generation Corolla hybrid sedan observation.

Count: `2 record-sides`.

### `catalog_identity_golden_br_v1.json`

Case `br-no-match-corsa-shared-fipe-different-model-year`:

- `left` and `right` → candidate source `corsa-wind-fipe-code-secondary`.
  - retained support describes the Corsa Wind model, FIPE code `004001-0`, and the code across multiple model years;
  - the official FIPE source remains semantic/supporting context and must not be promoted into automatic identity authority.

Case `br-review-shared-fipe-code-alone`:

- `left` and `right` → candidate source `corsa-wind-fipe-code-secondary` for the fields actually present in the code-only observations.
  - retained review evidence explicitly says the observations lack model-year evidence and therefore remain non-deterministic for identity;
  - candidate provenance does not change that `FIPE SUPPORTING != AUTOMATIC IDENTITY`.

Count: `4 record-sides`.

### `catalog_identity_br_adjacent_incomplete_v1.json`

Case `br-hard-no-match-corolla-altis-hybrid-my25-vs-my26`:

- `left` → candidate source `toyota-connected-services-corolla-my25`.
  - retained support explicitly lists Corolla model year 2025 configurations including Altis Hybrid Premium.
- `right` → candidate source `toyota-corolla-altis-hybrid-offer-2026`.
  - retained support explicitly describes the Corolla Altis Premium Hybrid 2026 offer.

Case `br-hard-no-match-onix-premier-my26-vs-my27`:

- `left` → candidate source `chevrolet-onix-my26-price-list`.
  - retained support explicitly identifies Onix Premier, hatch and model year 2026.
- `right` → candidate source `chevrolet-onix-line-2027`.
  - retained support explicitly identifies the Brazil Onix line 2027 and Premier Turbo AT hatch configuration.

Count: `4 record-sides`.

Total candidate count:

`SINGLE_SOURCE_PER_SIDE_CANDIDATE = 10 record-sides`

No `fieldSourceIds` are added by this classification.

## Genuinely composite multi-source observations

### `catalog_identity_golden_v1.json`

The following blocked record-sides are composite under the retained summaries because generation/trim/body or powertrain facts are distributed across the declared sources rather than established as a complete side observation by one retained support description:

- `match-ford-mustang-dark-horse`: left, right;
- `match-porsche-911-992-carrera-4s`: left, right;
- `no-match-ford-mustang-gt-vs-dark-horse`: left, right;
- `no-match-porsche-911-991-vs-992`: left, right;
- `review-porsche-911-partial-variant-label`: left, right.

Count: `10 record-sides`.

### `catalog_identity_golden_br_v1.json`

The following blocked record-sides are composite under the retained source summaries and case rationales:

- `br-match-corolla-cross-xrx-hybrid-my25`: left, right — generation history and MY25 trim/mechanical evidence are supplied by separate Toyota sources;
- `br-match-onix-premier-turbo-my25`: left, right — second-generation evidence and MY25 Premier mechanical evidence are supplied by separate Chevrolet sources;
- `br-match-tcross-highline-250-tsi`: left, right — Brazil generation history and current Highline/configuration evidence are supplied by separate Volkswagen sources;
- `br-match-strada-ranch-13-cvt`: left, right — second-generation/powertrain context and Ranch/CVT configuration evidence are supplied by separate Fiat sources;
- `br-no-match-corolla-cross-xrx-hybrid-vs-xrx-flex`: left, right — generation context and MY25 hybrid/combustion configuration evidence are split across Toyota sources;
- `br-no-match-tcross-highline-vs-comfortline`: left, right — generation context and trim/powertrain evidence are split across Volkswagen sources;
- `br-no-match-strada-volcano-manual-vs-cvt`: left, right — generation/powertrain context and transmission-specific Volcano evidence are split across Fiat sources;
- `br-review-corolla-cross-xrx-hybrid-missing-variant`: left, right — retained review evidence confirms multiple hybrid trims while generation and MY25 configuration evidence come from different Toyota sources;
- `br-review-onix-premier-missing-variant`: left, right — retained review evidence confirms the missing variant cannot be inferred, while generation and MY25 mechanical evidence are split across Chevrolet sources;
- `br-review-tcross-250-tsi-missing-variant`: left, right — retained review evidence confirms the generic 250 TSI observation is ambiguous, while generation and current trim evidence are split across Volkswagen sources.

Count: `20 record-sides`.

The two Corsa/FIPE cases are intentionally excluded from this composite bucket and remain single-source-per-side candidates because the retained secondary enumeration can account for their present observation fields; this does not elevate FIPE beyond `SUPPORTING` identity semantics.

### `catalog_identity_br_adjacent_incomplete_v1.json`

The following blocked record-sides are composite under the retained summaries:

- `br-hard-control-match-tcross-highline-complete-official-sources`: left, right — generation history and mechanical/configuration evidence are split across Volkswagen sources;
- `br-hard-review-onix-my26-premier-incomplete-mechanical-mapping`: left, right — generation comes from the second-generation source while detailed/incomplete MY26 configuration evidence comes from separate sources;
- `br-hard-review-tcross-highline-current-page-missing-transmission-mapping`: left, right — generation, current trim/powertrain page and transmission evidence are explicitly split;
- `br-hard-review-tcross-highline-model-year-present-one-side`: left, right — generation, technical-sheet/current-page facts and MY26 mechanical/model-year context are split.

Count: `8 record-sides`.

Total composite count:

`GENUINELY_COMPOSITE_MULTI_SOURCE = 38 record-sides`

For these 38 sides, simply adding truthful per-field attribution cannot satisfy the current replay requirement for one unique source common to all present fields.

## Classification closure

Frozen blocked scope: `48` record-sides.

Retained-summary classification:

- `SINGLE_SOURCE_PER_SIDE_CANDIDATE = 10`;
- `GENUINELY_COMPOSITE_MULTI_SOURCE = 38`;
- `UNRESOLVED_FROM_RETAINED_SUMMARY = 0`.

This closes classification at the retained-summary level, not field-attribution mutation. The ten candidates still require field-by-field encoding and validation against the declared source evidence before they can become replayable.

## Falsified hypothesis

The hypothesis that all 48 blocked record-sides are merely missing attribution metadata is rejected by retained evidence:

- `38/48 = 79.17%` are genuinely composite under the retained source summaries;
- only `10/48 = 20.83%` are candidates for the existing one-source-per-record replay contract.

Therefore a bulk attribution operation would be scientifically invalid and operationally misleading.

## Next experiment

Apply explicit field attribution only to the 10 candidate record-sides, one case family at a time, and rerun the frozen measurements.

Success for that experiment means:

- candidate sides become `EXPLICIT_FIELD_ATTRIBUTION` replayable without changing source semantics;
- the 38 composite sides remain blocked, expected to move from `MULTI_SOURCE_WITHOUT_EXPLICIT_FIELD_ATTRIBUTION` to `NO_UNIQUE_COMMON_SOURCE` once truthful per-field attribution exists;
- no resolver threshold, source qualification, identity precedence, or conflict semantics changes;
- no increase is counted as valid if provenance completeness regresses.

If the 10 candidates validate, the theoretical replayable upper bound under the current one-source-per-record contract becomes `22/60 = 36.67%` for the active three-dataset scope before any replay redesign. The remaining 38 blocked sides would then be evidence of an architectural replay limitation rather than missing attribution data.
