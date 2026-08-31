# Productive Coverage Wave 01 — retained-evidence classification

Status: evidence classification, no corpus mutation

Scope: the 48 blocked record-sides from the three-dataset coverage scope frozen in `PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01.md`.

This artifact classifies only what the retained benchmark `sources[].supports`, case fields and case rationales establish without adding external evidence or inferring source ownership from `sourceIds` order.

## Classification semantics

- `SINGLE_SOURCE_PER_SIDE_CANDIDATE`: the retained support descriptions identify one declared source that can account for the present identity fields of that record-side. This is a candidate for explicit `fieldSourceIds`; it is not yet a mutation authorization until field-by-field attribution is encoded and validated.
- `GENUINELY_COMPOSITE_MULTI_SOURCE`: the retained descriptions explicitly distribute present fields across more than one source, so a unique source common to every present field is not supported by the retained evidence. Adding complete field attribution would still leave the current operational replay contract blocked by `NO_UNIQUE_COMMON_SOURCE`.
- `UNRESOLVED_FROM_RETAINED_SUMMARY`: the retained summaries inspected so far are insufficient to choose either category without source-level review. No attribution is authorized.

## Proven single-source-per-side candidates

### `catalog_identity_golden_v1.json`

Case `no-match-toyota-corolla-10g-vs-12g`:

- `left` → candidate source `toyota-corolla-2006-global`.
  - retained support: 10th-generation Corolla/Axio sedan and 1.8-liter 2ZR-FE powertrain;
  - present side fields are the 10th-generation Corolla, 1.8 petrol, sedan observation.
- `right` → candidate source `toyota-corolla-2018-global`.
  - retained support: 12th-generation Corolla sedan family and hybrid availability;
  - present side fields are the 12th-generation Corolla hybrid sedan observation.

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

Proven lower bound:

`SINGLE_SOURCE_PER_SIDE_CANDIDATE >= 6 record-sides`

No `fieldSourceIds` are added by this classification.

## Proven genuinely composite observations

### `catalog_identity_golden_v1.json`

The following blocked record-sides are composite under the retained summaries because generation/trim/body or powertrain facts are distributed across the declared sources rather than established as a complete side observation by one retained support description:

- `match-ford-mustang-dark-horse`: left, right;
- `match-porsche-911-992-carrera-4s`: left, right;
- `no-match-ford-mustang-gt-vs-dark-horse`: left, right;
- `no-match-porsche-911-991-vs-992`: left, right;
- `review-porsche-911-partial-variant-label`: left, right.

Count: `10 record-sides`.

### `catalog_identity_br_adjacent_incomplete_v1.json`

The following blocked record-sides are composite under the retained summaries:

- `br-hard-control-match-tcross-highline-complete-official-sources`: left, right — generation history and mechanical/configuration evidence are split across Volkswagen sources;
- `br-hard-review-onix-my26-premier-incomplete-mechanical-mapping`: left, right — generation comes from the second-generation source while detailed/incomplete MY26 configuration evidence comes from separate sources;
- `br-hard-review-tcross-highline-current-page-missing-transmission-mapping`: left, right — generation, current trim/powertrain page and transmission evidence are explicitly split;
- `br-hard-review-tcross-highline-model-year-present-one-side`: left, right — generation, technical-sheet/current-page facts and MY26 mechanical/model-year context are split.

Count: `8 record-sides`.

Proven lower bound:

`GENUINELY_COMPOSITE_MULTI_SOURCE >= 18 record-sides`

For these 18 sides, simply adding truthful per-field attribution cannot satisfy the current replay requirement for one unique source common to all present fields.

## Unresolved remainder

Frozen blocked scope: `48` record-sides.

Proven classified so far:

- single-source-per-side candidates: `6`;
- genuinely composite: `18`;
- unresolved remainder: `24`.

The unresolved 24 record-sides are the blocked sides in `catalog_identity_golden_br_v1.json`. They remain `UNRESOLVED_FROM_RETAINED_SUMMARY` until each side is checked field-by-field against the declared source support/evidence. In particular, case-level `sourceIds` must not be converted into field attribution by position, source count, publisher identity, or rationale wording alone.

## Decision boundary

The current evidence falsifies the hypothesis that all 48 blocked record-sides are merely missing metadata:

- at least 18 are genuinely multi-source under retained evidence;
- at least 6 are candidates for valid single-source-per-side attribution;
- 24 still require evidence-level classification.

Therefore the next mutation, if any, must target only individually proven candidate sides. A general replay relaxation or bulk attribution is not authorized by this artifact.
