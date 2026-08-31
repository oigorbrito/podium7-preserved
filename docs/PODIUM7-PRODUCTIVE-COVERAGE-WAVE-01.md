# PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01

Status: `DECISION_REQUIRED` — retained-evidence classification shows operational replay design, not only missing attribution metadata, is the dominant remaining limiter

## Objective

Increase replayable, evidence-backed coverage for the retained Brazil-relevant catalog corpus without weakening identity, provenance, field attribution, conflict handling, source qualification, or fail-closed semantics.

## Frozen baseline before mutation

Measurement scope used by `tests/test_catalog_identity_field_coverage.py`:

- datasets: `catalog_identity_golden_v1.json`, `catalog_identity_golden_br_v1.json`, `catalog_identity_br_adjacent_incomplete_v1.json`;
- retained record-sides: 60;
- replayable record-sides: 12;
- blocked record-sides: 48;
- replay method for current replayable records: `SOLE_CASE_SOURCE`;
- current retained V3 field-attribution coverage: `0.0` according to `tests/test_catalog_field_provenance.py`;
- published consumer vehicles in the previously executed retained-scope measurement: 4;
- measured published-field coverage from that execution: `body_style=1.0`, `powertrain=1.0`, `transmission=0.5`.

The last two published-output metrics are retained execution evidence and must be re-executed before claiming a new final value.

## Frozen root-cause taxonomy

The taxonomy is defined before corpus mutation from the existing fail-closed branches in `unique_source_for_record`:

- `MULTI_SOURCE_WITHOUT_EXPLICIT_FIELD_ATTRIBUTION`
- `MISSING_SIDE_FIELD_ATTRIBUTION`
- `MISSING_PRESENT_FIELD_ATTRIBUTION`
- `NO_UNIQUE_COMMON_SOURCE`
- `INVALID_CASE_SOURCE_ATTRIBUTION`
- `UNKNOWN_CASE_SOURCE`
- `INVALID_FIELD_ATTRIBUTION`
- `UNKNOWN_FIELD_SOURCE`

For the current 48 blocked record-sides in the three-dataset coverage scope, repository tests already constrain the observed reason to multiple case-level `sourceIds` without explicit field attribution. Therefore the current measured first bucket remains:

`MULTI_SOURCE_WITHOUT_EXPLICIT_FIELD_ATTRIBUTION = 48`

No other executed blocker count is claimed until corpus attribution is actually mutated and measurements are re-run.

## Invariants

- `CONTRACT_READY != DATA_READY != PRODUCT_READY`
- `MORE_SOURCE != MORE_COVERAGE`
- `UNKNOWN != ZERO`
- `CONFLICT != FACT`
- no synthetic attribution;
- no source-semantic reinterpretation;
- no threshold reduction for count gain;
- no new source family until existing-evidence closure is shown insufficient;
- source qualification cannot be weakened merely to manufacture a unique replay source.

## Required measurements

Before and after each mutation, record:

- total record-sides;
- replayable and blocked record-sides;
- blocked count by frozen root-cause code;
- published vehicle count;
- identity-field coverage;
- provenance / field-attribution completeness;
- quantitative-envelope coverage by field and knowledge state;
- unresolved conflict count;
- vehicles with N known quantitative fields;
- market and source-family distribution.

## Evidence-review finding 01

The original `MULTI_SOURCE_WITHOUT_EXPLICIT_FIELD_ATTRIBUTION` bucket conflates materially different evidence states.

A record-side with multiple declared case sources can be:

1. fully supportable by one declared source once each present field is checked;
2. correctly composite, with required fields split across multiple retained sources;
3. insufficiently supported for a safe unique-source attribution.

The benchmark/provenance model can represent valid field-level attribution from multiple sources, while `unique_source_for_record` currently requires exactly one source common to every present field before operational replay.

The branch freezes that boundary with a focused regression: synthetically valid field-attributed data with `make/model` from one source and `generation` from another remains blocked as `NO_UNIQUE_COMMON_SOURCE`.

Therefore:

`FIELD_ATTRIBUTION_COMPLETE != OPERATIONAL_REPLAYABLE`

and

`MULTI_SOURCE_EVIDENCE != INVALID_EVIDENCE`

## Retained-evidence classification 02

The 48 blocked record-sides were reviewed against the retained `sources[].supports` contract. The initially promising/ambiguous sides were then checked against their declared source content where accessible. Representative composite cases were also checked across the global, Brazil, and adjacent/incomplete slices to ensure the source split was not merely an artifact of coarse support summaries.

Classification terms:

- `VERIFIED_SINGLE_SOURCE`: one declared retained source can support every present vehicle field on that record-side without inference and without weakening source qualification.
- `COMPOSITE_SUPPORT`: the retained support needed for the present fields is distributed across multiple declared sources, or collapsing to one source would over-promote a supporting source and lose authoritative semantics.
- `INSUFFICIENT_SINGLE_SOURCE_SUPPORT`: no declared source safely supports every present field and the missing support cannot be inferred.

### Final review ledger for the current 48 blocked sides

| Dataset | Case | Left | Right |
| --- | --- | --- | --- |
| `catalog_identity_golden_v1.json` | `match-ford-mustang-dark-horse` | `COMPOSITE_SUPPORT` | `COMPOSITE_SUPPORT` |
| `catalog_identity_golden_v1.json` | `match-porsche-911-992-carrera-4s` | `VERIFIED_SINGLE_SOURCE` | `VERIFIED_SINGLE_SOURCE` |
| `catalog_identity_golden_v1.json` | `no-match-toyota-corolla-10g-vs-12g` | `INSUFFICIENT_SINGLE_SOURCE_SUPPORT` | `VERIFIED_SINGLE_SOURCE` |
| `catalog_identity_golden_v1.json` | `no-match-ford-mustang-gt-vs-dark-horse` | `COMPOSITE_SUPPORT` | `COMPOSITE_SUPPORT` |
| `catalog_identity_golden_v1.json` | `no-match-porsche-911-991-vs-992` | `INSUFFICIENT_SINGLE_SOURCE_SUPPORT` | `VERIFIED_SINGLE_SOURCE` |
| `catalog_identity_golden_v1.json` | `review-porsche-911-partial-variant-label` | `VERIFIED_SINGLE_SOURCE` | `VERIFIED_SINGLE_SOURCE` |
| `catalog_identity_golden_br_v1.json` | `br-match-corolla-cross-xrx-hybrid-my25` | `COMPOSITE_SUPPORT` | `COMPOSITE_SUPPORT` |
| `catalog_identity_golden_br_v1.json` | `br-match-onix-premier-turbo-my25` | `COMPOSITE_SUPPORT` | `COMPOSITE_SUPPORT` |
| `catalog_identity_golden_br_v1.json` | `br-match-tcross-highline-250-tsi` | `COMPOSITE_SUPPORT` | `COMPOSITE_SUPPORT` |
| `catalog_identity_golden_br_v1.json` | `br-match-strada-ranch-13-cvt` | `COMPOSITE_SUPPORT` | `COMPOSITE_SUPPORT` |
| `catalog_identity_golden_br_v1.json` | `br-no-match-corolla-cross-xrx-hybrid-vs-xrx-flex` | `COMPOSITE_SUPPORT` | `COMPOSITE_SUPPORT` |
| `catalog_identity_golden_br_v1.json` | `br-no-match-tcross-highline-vs-comfortline` | `COMPOSITE_SUPPORT` | `COMPOSITE_SUPPORT` |
| `catalog_identity_golden_br_v1.json` | `br-no-match-strada-volcano-manual-vs-cvt` | `COMPOSITE_SUPPORT` | `COMPOSITE_SUPPORT` |
| `catalog_identity_golden_br_v1.json` | `br-no-match-corsa-shared-fipe-different-model-year` | `COMPOSITE_SUPPORT` | `COMPOSITE_SUPPORT` |
| `catalog_identity_golden_br_v1.json` | `br-review-corolla-cross-xrx-hybrid-missing-variant` | `COMPOSITE_SUPPORT` | `COMPOSITE_SUPPORT` |
| `catalog_identity_golden_br_v1.json` | `br-review-onix-premier-missing-variant` | `COMPOSITE_SUPPORT` | `COMPOSITE_SUPPORT` |
| `catalog_identity_golden_br_v1.json` | `br-review-tcross-250-tsi-missing-variant` | `COMPOSITE_SUPPORT` | `COMPOSITE_SUPPORT` |
| `catalog_identity_golden_br_v1.json` | `br-review-shared-fipe-code-alone` | `COMPOSITE_SUPPORT` | `COMPOSITE_SUPPORT` |
| `catalog_identity_br_adjacent_incomplete_v1.json` | `br-hard-control-match-tcross-highline-complete-official-sources` | `COMPOSITE_SUPPORT` | `COMPOSITE_SUPPORT` |
| `catalog_identity_br_adjacent_incomplete_v1.json` | `br-hard-no-match-corolla-altis-hybrid-my25-vs-my26` | `VERIFIED_SINGLE_SOURCE` | `VERIFIED_SINGLE_SOURCE` |
| `catalog_identity_br_adjacent_incomplete_v1.json` | `br-hard-no-match-onix-premier-my26-vs-my27` | `VERIFIED_SINGLE_SOURCE` | `VERIFIED_SINGLE_SOURCE` |
| `catalog_identity_br_adjacent_incomplete_v1.json` | `br-hard-review-onix-my26-premier-incomplete-mechanical-mapping` | `COMPOSITE_SUPPORT` | `COMPOSITE_SUPPORT` |
| `catalog_identity_br_adjacent_incomplete_v1.json` | `br-hard-review-tcross-highline-current-page-missing-transmission-mapping` | `COMPOSITE_SUPPORT` | `COMPOSITE_SUPPORT` |
| `catalog_identity_br_adjacent_incomplete_v1.json` | `br-hard-review-tcross-highline-model-year-present-one-side` | `COMPOSITE_SUPPORT` | `COMPOSITE_SUPPORT` |

Classification totals:

- `COMPOSITE_SUPPORT = 36`
- `VERIFIED_SINGLE_SOURCE = 10`
- `INSUFFICIENT_SINGLE_SOURCE_SUPPORT = 2`
- total = `48`

These are evidence-review classifications, not new executed replay counts. The measured operational state remains 12 replayable / 48 blocked until benchmark attribution is mutated and measurements are executed again.

## Source-level findings that changed the first-pass triage

- Toyota Corolla 10th-generation left side: the declared 2006 Toyota source explicitly establishes Corolla Axio sedan, 10th generation and a 1.8-liter 2ZR-FE engine, but the inspected retained source does not explicitly establish the benchmark field value `powertrain = "1.8 petrol"`. That field is not inferred; the side remains insufficient.
- Toyota Corolla 12th-generation right side: the declared 2018 Toyota source explicitly establishes Corolla sedan, present 12th generation and hybrid models; it is a valid unique-source candidate.
- Porsche 992: the retained Porsche generation/powertrain material directly establishes 992, Carrera 4S, the 3.0-litre turbo six-cylinder boxer configuration and coupe context. Several Porsche sides that looked composite from the support summary are therefore valid unique-source candidates.
- Porsche 991 left side: retained material establishes 991/Carrera S/boxer-engine context but does not safely establish every present field, specifically the benchmark's 991 `body_style = "coupe"`, from a declared unique source. It remains insufficient rather than inferred.
- Corsa/FIPE sides: the secondary enumeration directly supplies the Corsa model, FIPE code and model-year rows, while the official FIPE source supplies authoritative national/model-year semantics. Treating the secondary enumeration as sole provenance would over-promote a source intentionally retained as supporting; these sides remain composite.
- Adjacent Corolla MY25/MY26: Toyota do Brasil directly identifies Corolla Altis Hybrid Premium in model year 2025 and the retained 2026 offer identifies Corolla Altis Premium Hybrid 26/26, making each side independently supportable.
- Adjacent Onix MY26/MY27: Chevrolet's retained MY26 price material identifies Onix Premier with model year 2026, while the official 2027 line announcement explicitly includes Onix Premier Turbo AT in the 2027 family. Each side is independently supportable for the fields present in this benchmark case.

## Verified composite boundary

The composite classification is not only theoretical. Representative retained cases show the same split across all three wave slices:

- global slice: Mustang records combine technical trim/body/powertrain material with separate seventh-generation evidence;
- Brazil slice: Corolla Cross combines global model/generation context with Brazil MY25 configuration evidence; Onix combines second-generation context with Brazil model-year/configuration evidence;
- adjacent/incomplete slice: Onix and T-Cross hard cases intentionally combine generation, model-year and mechanical evidence from different official sources.

A unique-source replay requirement therefore rejects valid evidence structures by design, not merely malformed attribution metadata.

## Data-completion ceiling under the current replay contract

The 10 `VERIFIED_SINGLE_SOURCE` sides define the maximum immediate existing-evidence data-completion lane identified by this review.

If all 10 are explicitly attributed and validation confirms the classification, the theoretical replay count under the unchanged unique-source contract would move from:

- 12 replayable / 48 blocked

to at most:

- 22 replayable / 38 blocked.

This is a planning ceiling, not an executed result. No claim of 22 replayable records is valid until the benchmark is changed and the measurement/test suite is rerun.

The remaining 38 sides divide into:

- 36 valid/composite sides limited by the unique-source operational replay contract;
- 2 sides that still lack enough retained support for a safe unique-source attribution.

Therefore data completion alone cannot close this wave.

## Decision required

`DECISION_REQUIRED = OPERATIONAL_REPLAY_PROVENANCE_MODEL`

Before implementing any multi-source replay path, choose one of the following bounded policies:

1. `KEEP_UNIQUE_SOURCE_REPLAY`
   - complete only the 10 verified single-source sides;
   - leave composite evidence non-replayable by design;
   - accept a retained-scope replay ceiling unless future qualified evidence creates a genuine common source.

2. `PRESERVE_FIELD_LEVEL_MULTI_SOURCE_REPLAY`
   - redesign operational replay so an output record carries and preserves per-field provenance from multiple qualified sources;
   - never collapse composite attribution to a synthetic unique source;
   - keep existing conflict/source-qualification/fail-closed rules intact;
   - require a separately reviewed architecture contract and regressions before corpus migration.

No third option that invents a source, weakens source qualification, drops provenance, or silently chooses one source is admissible under the current invariants.

The evidence favors treating multi-source replay as an explicit architecture decision rather than disguising it as data cleanup.

## Work allowed before the decision

The following work remains independently safe:

- preserve the machine-readable blocker taxonomy introduced by PR #278;
- prepare exact field-attribution patches for the 10 `VERIFIED_SINGLE_SOURCE` sides in a separate evidence-mutation change set;
- document the two insufficient sides as retained blockers;
- write the architecture decision contract/options and tests without implementing a chosen multi-source behavior;
- continue hosted-CI recovery monitoring.

Do not merge a benchmark mutation into the blocker-classification PR merely to improve the count.

## Exit states

- `COMPLETE`: coverage improved and all required local/remote validation applicable to the wave is green;
- `COMPLETE_EXTERNAL_VALIDATION_PENDING`: internal evidence is complete but hosted validation remains externally blocked;
- `DECISION_REQUIRED`: evidence proves the current replay contract, not missing attribution data, is the dominant limiting factor and an architecture/product decision is required;
- `REJECTED_BY_EVIDENCE`: attempted coverage change would require inference, semantic weakening, or unsupported source claims.
