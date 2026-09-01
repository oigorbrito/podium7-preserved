# PODIUM7 Revalidation Wave 01

Status: COMPLETE

## Authority order

This wave used the following authority order:

`CODE/TEST EXECUTED > CURRENT AUTHORITY DOCS > GENERATED/RETAINED ARTIFACTS > HISTORICAL EVIDENCE > INFERENCE`

Historical source-acquisition and PR outcome records remain evidence only. They do not override current code, current authority documents, or executed tests on the measured SHA.

## Repository state

- Repository under test: `tihotm/podium7`
- Tested SHA: `f875b156a6213aa0d8ddcb689784cfb634913cee`
- Tested branch context: local revalidation branch created from `origin/main`
- Current top commit observed: `data: retain Onix multisource attribution (#307)`
- Prior expected merge verified: PR `#307` content is present at the tested SHA.

GitHub API issue/PR listing was not available from the execution environment because `gh` returned HTTP 401. This blocks remote issue/PR hygiene evidence only; it does not change local code/test results.

## Current authority reconciliation

| Area | Status | Evidence | Consequence |
| --- | --- | --- | --- |
| Project stage | CONSISTENT | `docs/PROJECT-STATE.md` states `MAINTENANCE / CONTROLLED_PRODUCT_EVOLUTION` and `FIXTURE_OPERATIONAL` data mode. | Podium7 is ready for its accepted private fixture-operational baseline, not for inferred broad live production coverage. |
| Live acquisition | CONSISTENT | `docs/REQUIREMENTS.md` explicitly excludes live acquisition as a current baseline requirement. | Live acquisition absence is not a baseline failure. |
| Catalog identity contract | CONSISTENT | `docs/CATALOG-IDENTITY-V2.md`, catalog tests, and full suite pass. | BPT2 can continue consuming stable catalog identity by `entity.id`; labels remain presentation, not join keys. |
| Quantitative enrichment contract | CONSISTENT | `docs/QUANTITATIVE-ENRICHMENT-CONSUMER-CONTRACT-V1.md` plus `tests.test_quantitative_coverage` pass. | Contract is ready; data coverage is not ready for broad product surfaces. |
| Historical source-acquisition outcome | DOC_STALE_AS_AUTHORITY | `docs/DOCUMENTATION-AUTHORITY-MATRIX.md` classifies `POST-MVP-SOURCE-ACQUISITION-OUTCOME-V1.md` as historical/archive candidate. | Use only as history; do not treat old stacked PR or runner state as current. |

## Executed validation

| Command | Result | Evidence |
| --- | --- | --- |
| `python -m unittest tests.test_operational_multisource_onix_retained` | PASS | 2 tests passed. Composed overlay measurement asserted `records=60`, `replayableRecords=50`, `blockedRecords=10`. |
| `python scripts/check_harness.py` | PASS | Harness reported `HARNESS PASS`. |
| `python -m podium7 health` | PASS | JSON health reported `status=PASS`, `schema_version=1`, `expected_schema_version=1`. |
| `python scripts/check_package_installation.py` | PASS | Wheel/sdist build and import health passed. |
| `python scripts/run_tests_one_by_one.py` | PASS | 739/739 tests executed one by one; report written to `artifacts/test-report.json`. |
| `python scripts/measure_catalog_identity_coverage.py` | PASS | Native current metric reports 22/60 replayable without retained overlay composition. |
| `python -m unittest tests.test_quantitative_coverage` | PASS | 8 tests passed. |

## Frozen coverage metrics

The active identity corpus metrics were frozen before interpretation:

| Metric | Measured value |
| --- | --- |
| Total active benchmark cases | 30 |
| Total active record sides | 60 |
| Record sides by market | `BR=36`, `<unknown:null>=24` |
| Unique retained source IDs in active corpus | 28 |
| Operational overlay replayability | 50/60 |
| Overlay blocked records | 10 |
| Overlay replayable methods | `SOLE_CASE_SOURCE=12`, `EXPLICIT_FIELD_ATTRIBUTION=10`, `MULTISOURCE_FIELD_ATTRIBUTION_V2=28` |
| Overlay blocked reason codes | `MISSING_SIDE_FIELD_ATTRIBUTION=2`, `MULTI_SOURCE_WITHOUT_EXPLICIT_FIELD_ATTRIBUTION=8` |
| Native published consumer vehicles | 7 |
| Native operational replay | `created=7`, `matched=7`, `review=8`, `failed=0`, `total=22` |
| Native consumer field coverage | `powertrain=5/7`, `transmission=2/7`, `body_style=5/7` |

The 50/60 result is executed authority for the retained overlay composition. It does not convert the fixture corpus into production-wide market coverage.

## Quantitative enrichment coverage

| Metric | Measured value |
| --- | --- |
| Contract schema | `podium7.quantitative-enrichment.v1` |
| Frozen V1 fields | `displacement`, `power`, `torque`, `length`, `width`, `height`, `wheelbase`, `curb_weight`, `fuel_economy_combined` |
| Brazil coverage fixture vehicles | 3 |
| Brazil coverage fixture records | 27 |
| Known publication-ready quantitative records | 0 |
| Unknown or not-publishable quantitative records | 27 |
| Unresolved quantitative conflicts | 0 |
| Comparable distinct-vehicle quantitative pairs | 0 |

`CONTRACT_READY != DATA_READY != PRODUCT_READY`: the envelope, revision, provenance, conflict, and fail-closed semantics are ready, but the retained Brazil quantitative corpus is not data-ready for broad BPT2 ficha tecnica, Comparator, filters, ranking, or Saved Search semantics.

## Source-family classification

| Source family | Classification | Evidence | BPT2 consequence |
| --- | --- | --- | --- |
| Retained catalog identity fixtures | OPERATIONAL_CURRENT | Full suite and 50/60 overlay measurement pass on current SHA. | Safe for bounded identity consumption already authorized by Catalog JSON 2.0. |
| NHTSA vPIC | INTEGRATED_BUT_NOT_PRODUCTION_PROVEN | Distribution artifact has 22 US records and inspected source family evidence. | Useful as producer-side evidence path; not a Brazil marketplace coverage authority. |
| FuelEconomy.gov | INTEGRATED_BUT_NOT_PRODUCTION_PROVEN | Distribution artifact has 63 US records and reference/discovery evidence. | Useful as producer-side evidence path; not authorization for BPT2 broad quantitative UX. |
| EEA CO2 cars | INTEGRATED_BUT_NOT_PRODUCTION_PROVEN | Distribution artifact has 4 EU records and EEA evidence docs. | Useful for EU-specific semantics; not current BPT2 Brazil coverage authority. |
| Inmetro PBEV | INTEGRATED_BUT_NOT_PRODUCTION_PROVEN | Distribution artifact has 2 BR records and quantitative fixture tests pass fail-closed. | Not enough data-ready quantitative coverage for BPT2 broad ficha tecnica or Comparator. |
| Historical arbitrary-web extraction | HISTORICAL/SUPERSEDED | Current docs route old extraction/source records as evidence or completed plans. | Do not use as current BPT2 product authority. |

No source family was reclassified as production-wide operational coverage by this wave.

## Readiness by layer

| Layer | Status | Evidence | Consequence for BPT2 |
| --- | --- | --- | --- |
| Catalog identity contract 2.0 | CONTRACT_READY | Current contract docs and full regression suite pass. | Safe to consume stable identity and redirects under existing BPT2 catalog boundary. |
| Catalog retained fixture corpus | DATA_READY_FOR_BOUNDED_FIXTURE_SCOPE | 50/60 overlay replayability with 10 explicit fail-closed blocked sides. | Safe only for bounded retained-corpus behavior; not broad production coverage. |
| Quantitative enrichment V1 | CONTRACT_READY | Contract docs and 8 quantitative coverage tests pass. | Safe to design against the contract only when product scope remains fail-closed. |
| Brazil quantitative data | DATA_NOT_READY | 3 vehicles x 9 fields; 0 known publication-ready quantitative records. | Blocks broad BPT2 ficha tecnica, Comparator, quantitative filters, ranking, and alerts. |
| Comparator or broad decision support | PRODUCT_NOT_READY | Contract nonclaims plus absent data-ready quantitative corpus. | Requires a new Podium productive coverage wave before BPT2 implementation. |

## BPT2 consequence matrix

| BPT2 candidate | Classification | Evidence | Required next action |
| --- | --- | --- | --- |
| Stable catalog identity joins | SAFE_TO_CONSUME_NOW | Catalog identity 2.0 and current BPT2 rule to join by `entity.id`. | Continue current consumption discipline. |
| Bounded display of existing catalog identity fields | SAFE_TO_CONSUME_NOW | Contract-ready identity fields and fail-closed retained corpus evidence. | Keep UI semantics bounded to existing data. |
| Broad technical ficha | REQUIRES_NEW_PODIUM_WAVE | Quantitative contract ready, but Brazil data has 0 known publication-ready facts in the measured fixture. | Build a Podium productive Brazil quantitative coverage wave first. |
| Comparator | STILL_BLOCKED | Quantitative contract nonclaims and no comparable distinct-vehicle quantitative pairs. | Do not implement in BPT2 until Podium proves field comparability and coverage. |
| Quantitative filters/ranking/search alerts | STILL_BLOCKED | Quantitative facts are not data-ready and should not drive identity or ranking. | Require producer data coverage and product semantics first. |
| Recommendations based on similarity | RESEARCH_FIRST | Current corpus is bounded fixture evidence, not broad marketplace similarity coverage. | Keep BPT2 recommendations frozen until producer/product evidence exists. |

## Decision

`PODIUM_PRODUCTIVE_COVERAGE_WAVE_REQUIRED`

The current Podium7 `main` is healthy for its accepted fixture-operational/private baseline and contract semantics. It is not evidence-ready as a broad productive data source for BPT2 Comparator, wide ficha tecnica, quantitative filters, ranking, or recommendation expansion.

## Recommended next action

Run a Podium7 productive coverage wave before returning to BPT2 data-enhanced product expansion.

Minimum wave boundary:

- choose one BPT2-relevant product surface first, preferably Brazil technical ficha coverage before Comparator;
- define field-level acceptance before measuring;
- acquire or retain source-backed Brazil quantitative facts for a representative corpus;
- prove known/unknown/not_applicable density, provenance, revision stability, conflicts, and comparability;
- expose only data-ready fields to BPT2.

