# PODIUM7 Productive Coverage Wave 02

Status: REALIGNED / VALIDATION PENDING

## Objective

Establish whether Podium7 currently has minimum Brazilian quantitative productive coverage for the first BPT2 technical-sheet surface without expanding product scope or inventing missing values.

## Current base

- Repository: `tihotm/podium7`
- Realigned base commit: `44b96d47685eecd34d8fb849ceead37666ec7754`
- Base commit subject: `data: retain Toyota Porsche multisource attribution (#309)`
- Working branch: `codex/podium7-productive-coverage-wave-02-realigned`

The original Wave 02 branch was based on `990b340f3b523567e07266fb3e87be57174cc135`. After #309 advanced `main`, the five Wave 02 paths were verified to have no overlap with the intervening Toyota/Porsche changes. The Wave 02 implementation was therefore reapplied from the current `main` rather than merged from the stale branch.

## Authority rule

`CODE/TEST EXECUTED > CURRENT AUTHORITY DOCS > GENERATED/RETAINED ARTIFACTS > HISTORICAL EVIDENCE > INFERENCE`

Readiness distinctions remain frozen:

- `CONTRACT_READY != DATA_READY != PRODUCT_READY`
- `SOURCE_AVAILABLE != FIELD_SUPPORTED`
- `FIELD_SUPPORTED != NORMALIZED`
- `NORMALIZED != PUBLICATION_READY`
- `PUBLICATION_READY != PRODUCT_COVERAGE`

## Current quantitative decision

Current public quantitative enrichment contract: `podium7.quantitative-enrichment.v1`.

The retained Brazilian quantitative fixture contains:

- source family: `INMETRO_PBEV`
- market: `BR`
- vehicles: 3
- contract fields per vehicle: 9
- candidate facts: 27
- provenance references complete: 27
- known facts: 0
- unknown facts: 27
- normalized facts: 0
- publication-ready facts: 0
- blocked facts: 27
- fully publication-ready vehicles: 0

Therefore the retained decision remains:

`BR_QUANTITATIVE_DATA_READY_FOR_BPT2_TECHNICAL_SHEET_V1 = NO`

No BPT2 quantitative technical-sheet feature is authorized by this wave.

## Implementation

The realigned branch adds or restores:

- `summarize_coverage_result()` in `podium7/quantitative_coverage.py`;
- `scripts/measure_quantitative_coverage.py`;
- deterministic summary coverage tests in `tests/test_quantitative_coverage.py`;
- this decision record and its documentation index entry.

No retained source fixture, catalog identity record, Toyota/Porsche attribution record, public contract, or BPT2 UI surface is mutated.

## Prior execution evidence

Before realignment, the same Wave 02 code on base `990b340f3b523567e07266fb3e87be57174cc135` recorded:

- `python -m unittest tests.test_quantitative_coverage`: PASS, 10 tests;
- quantitative measurement commands: PASS;
- Inmetro quantitative regression group: PASS, 19 tests;
- harness: PASS;
- runtime health: PASS;
- package installation: PASS;
- full isolated suite: PASS, 743/743.

These results are historical evidence for the Wave 02 implementation, not proof of execution on the realigned head.

## Validation gate

The realigned head must not be merged until execution evidence is obtained for the current branch. Required checks are:

- targeted quantitative coverage tests;
- quantitative measurement command, compact and full modes;
- Inmetro quantitative regression group;
- harness and package installation checks;
- runtime health;
- full isolated suite or equivalent repository quality gate.

GitHub-hosted workflow failures with `steps=null` remain classified as pre-repository infrastructure failures and do not constitute code-test failures.

## Product consequence

Until publication-ready Brazilian quantitative facts exist under an accepted contract, do not release quantitative comparator, broad ficha tecnica, quantitative filters/ranking, quantitative Saved Search, or recommendations based on quantitative similarity.

The next producer decision remains whether BPT2 should adopt source-native PBEV quantities through a deliberate contract-gap wave or obtain primary Brazilian evidence aligned with the existing V1 fields.
