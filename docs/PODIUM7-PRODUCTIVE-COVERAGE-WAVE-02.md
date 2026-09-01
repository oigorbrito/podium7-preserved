# PODIUM7 Productive Coverage Wave 02

Status: COMPLETE

## Objective

Establish whether Podium7 currently has minimum Brazilian quantitative productive coverage for the first BPT2 technical-sheet surface.

This wave is producer-side only. It does not authorize or implement a BPT2 UI expansion.

## Base

- Repository: `tihotm/podium7`
- Remote `main` checked by `git ls-remote`: `990b340f3b523567e07266fb3e87be57174cc135`
- Base commit: `990b340f3b523567e07266fb3e87be57174cc135`
- Base commit subject: `data: retain Mustang multisource attribution (#308)`
- Working branch: `codex/podium7-productive-coverage-wave-02`

`main` had advanced since `PODIUM7-REVALIDATION-WAVE-01`; this wave used the newer remote `main` as base.

## Methodology

Authority order:

`CODE/TEST EXECUTED > CURRENT AUTHORITY DOCS > GENERATED/RETAINED ARTIFACTS > HISTORICAL EVIDENCE > INFERENCE`

Frozen readiness distinctions:

- `CONTRACT_READY != DATA_READY != PRODUCT_READY`
- `SOURCE_AVAILABLE != FIELD_SUPPORTED`
- `FIELD_SUPPORTED != NORMALIZED`
- `NORMALIZED != PUBLICATION_READY`
- `PUBLICATION_READY != PRODUCT_COVERAGE`

No missing value was inferred. No secondary source was promoted to publication-ready quantitative authority.

## Contract inventory

Current public quantitative enrichment contract: `podium7.quantitative-enrichment.v1`.

| Field | Shapes allowed by contract | Publication unit requirement | Normalization evidence | Current BR coverage status |
| --- | --- | --- | --- | --- |
| `displacement` | scalar/range/limit/multiple | unit required | `cc`, `L/l` to `cc` | `NORMALIZATION_READY`, `NO_PUBLICATION_READY_BR_DATA` |
| `power` | scalar/range/limit/multiple | unit required | `kW`, `hp/bhp`, `cv/PS` to `kW` | `NORMALIZATION_READY`, `NO_PUBLICATION_READY_BR_DATA` |
| `torque` | scalar/range/limit/multiple | unit required | `Nm`, `lb-ft/lbft`, `kgfm` to `Nm` | `NORMALIZATION_READY`, `NO_PUBLICATION_READY_BR_DATA` |
| `length` | scalar/range/limit/multiple | unit required | `mm`, `in/inch/inches` to `mm` | `NORMALIZATION_READY`, `NO_PUBLICATION_READY_BR_DATA` |
| `width` | scalar/range/limit/multiple | unit required | `mm`, `in/inch/inches` to `mm` | `NORMALIZATION_READY`, `NO_PUBLICATION_READY_BR_DATA` |
| `height` | scalar/range/limit/multiple | unit required | `mm`, `in/inch/inches` to `mm` | `NORMALIZATION_READY`, `NO_PUBLICATION_READY_BR_DATA` |
| `wheelbase` | scalar/range/limit/multiple | unit required | `mm`, `in/inch/inches` to `mm` | `NORMALIZATION_READY`, `NO_PUBLICATION_READY_BR_DATA` |
| `curb_weight` | scalar/range/limit/multiple | unit required | `kg`, `lb/lbs` to `kg`; bounded kg/lb retained | `NORMALIZATION_READY`, `NO_PUBLICATION_READY_BR_DATA` |
| `fuel_economy_combined` | scalar/range/limit/multiple | unit required | `L/100km`, `mpg-US` to `L/100km` | `NORMALIZATION_READY`, `NO_PUBLICATION_READY_BR_DATA` |

The current contract does not include separate ethanol/gasoline city/road fields, electric-equivalent city/road efficiency, energy consumption in `MJ/km`, electric range, or PBE class labels.

## Brazilian source inventory

| Source | Authority | Market | Fields observed | Parser/extractor | Current status |
| --- | --- | --- | --- | --- | --- |
| Inmetro PBEV retained PDF page 1 | Official Brazilian source | BR | ethanol city/road, gasoline city/road, electric-equivalent city/road, `MJ/km`, electric range, PBE classes | `podium7.inmetro_pbev_benchmark` with `pdfplumber` fixture extraction | `SOURCE_OPERATIONAL_BOUNDED`, not contract-aligned for V1 publication |
| Manufacturer retained identity evidence | Official/manufacturer identity sources | BR | powertrain/transmission/body style and identity attributes | catalog identity benchmarks and multisource overlays | `SOURCE_OPERATIONAL_BOUNDED` for identity, not quantitative V1 publication |
| Retained Autoevolution web corpus | Secondary retained web evidence | non-BR/control | examples include `curb_weight` range | web extraction corpus | structural control only; excluded from BR coverage denominator |

No current BR source is both contract-aligned and measured as publication-ready for the V1 quantitative fields.

## BPT2 technical sheet V1 minimum

No BPT2 quantitative technical-sheet field is released by this wave.

Candidate user-value fields were evaluated against current contract and current retained BR source evidence:

| Candidate | Decision | Evidence |
| --- | --- | --- |
| `power` | excluded | Contract and normalization ready, but no publication-ready BR facts in measured corpus. |
| `torque` | excluded | Contract and normalization ready, but no publication-ready BR facts in measured corpus. |
| `displacement` | excluded | Contract and normalization ready, but no publication-ready BR facts in measured corpus. |
| dimensions/weight | excluded | Contract and normalization ready, but no publication-ready BR facts in measured corpus. |
| `fuel_economy_combined` | excluded | PBEV provides split city/road and electric-equivalent values, not current contract `fuel_economy_combined`. |
| PBEV city/road consumption, electric range, `MJ/km`, class labels | excluded | Source values exist in retained PBEV benchmark, but they are outside the current public quantitative V1 contract. |

## Corpus and measurement

Current retained BR quantitative coverage fixture:

- Corpus version: `br-pbev-retained-page1-quantitative-baseline-1.0`
- Source family: `INMETRO_PBEV`
- Market: `BR`
- Vehicles: 3
- Contract fields per vehicle: 9
- Candidate quantitative facts: 27
- Provenance references complete: 27
- Known facts: 0
- Unknown facts: 27
- Not applicable facts: 0
- Normalized facts: 0
- Publication-ready facts: 0
- Blocked facts: 27
- Fully publication-ready vehicles: 0
- Partially publication-ready vehicles: 0

Blocked reason:

`retained Inmetro PBEV gold establishes identity/table fields only; no publication-ready quantitative value is retained for this field`

The wave added a deterministic measurement summary on top of the existing fixture instead of changing the source data.

## Publication-ready criterion

For this wave, a `PUBLICATION_READY_QUANTITATIVE_FACT` requires:

- source is qualified for the field;
- explicit field support exists;
- evidence is retained;
- raw value is retained;
- normalization is valid for the current contract field;
- canonical unit is valid;
- no unresolved conflict exists;
- entity association is valid;
- the current publication contract is satisfied.

The current BR fixture satisfies provenance retention for 27 facts but not known raw value, normalization, canonical unit, or publication eligibility.

## Executed tests

| Command | Result |
| --- | --- |
| `git ls-remote https://github.com/tihotm/podium7.git refs/heads/main` | PASS, remote `main` = `990b340f3b523567e07266fb3e87be57174cc135` |
| `python -m unittest tests.test_quantitative_coverage` | PASS, 10 tests |
| `python scripts/measure_quantitative_coverage.py` | PASS |
| `python scripts/measure_quantitative_coverage.py --full` | PASS |
| `python -m unittest tests.test_inmetro_pbev_quantitative_benchmark tests.test_inmetro_pbev_quantitative_semantic_observation tests.test_inmetro_pbev tests.test_inmetro_pbev_extractor_comparison` | PASS, 19 tests |
| `python scripts/check_harness.py` | PASS |
| `python -m podium7 health` | PASS |
| `python scripts/check_package_installation.py` | PASS |
| `python scripts/run_tests_one_by_one.py` | PASS, 743/743 tests executed one by one |

## Findings

- The quantitative enrichment contract is healthy and testable.
- The current BR PBEV retained evidence is operationally extractable for source-bound benchmark semantics.
- The current V1 public contract does not contain the source-native PBEV quantities that page 1 already proves.
- The existing BR quantitative coverage fixture intentionally records all V1 contract fields as `unknown`.
- Therefore a retained rollout of publication-ready BPT2 technical-sheet facts would require either new contract-aligned BR source evidence or a deliberate contract expansion for source-native PBEV fields.

## Data readiness decision

`BR_QUANTITATIVE_DATA_READY_FOR_BPT2_TECHNICAL_SHEET_V1 = NO`

Reason: `publicationReady=0/27` and `fullyPublicationReadyVehicles=0/3` for the current BR quantitative fixture.

## BPT2 consequence

No BPT2 quantitative technical sheet is product-ready from current Podium7 data.

Do not release:

- Comparator;
- broad ficha tecnica;
- quantitative filters;
- quantitative ranking;
- quantitative Saved Search;
- recommendations based on quantitative similarity.

Safe next producer work:

- decide whether BPT2's first technical sheet should use source-native PBEV fields;
- if yes, create a Podium contract-gap wave for PBEV city/road consumption, electric-equivalent efficiency, energy consumption, electric range, and PBE labels;
- if no, acquire or retain primary/manufacturer BR evidence for current V1 fields.

## Blockers

| Blocker | Scope affected | Evidence | Required unblock | Stops wave |
| --- | --- | --- | --- | --- |
| GitHub write/auth not verified | Remote PR/merge | Earlier `gh` listing returned HTTP 401 in this environment. | Authenticated GitHub CLI/session. | No |

## Next action

`PODIUM_CONTRACT_GAP_WAVE_REQUIRED_FOR_PBEV_TECHNICAL_SHEET`

The next coherent block should decide and implement a source-native PBEV quantitative publication contract if BPT2 wants a Brazil technical-sheet V1 based on currently retained official INMETRO data.
