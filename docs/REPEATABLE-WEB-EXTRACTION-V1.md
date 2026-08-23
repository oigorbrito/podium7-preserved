# Podium 7 Repeatable Web Extraction V1

**Work unit:** `PODIUM7_REPEATABLE_WEB_EXTRACTION_V1`

## Scientific basis

WebLists supports discover/configure/reuse for repeated structured extraction; SODIUM, WideSearch, WebDS, and WANDR motivate explicit evidence and measured completeness rather than trusting generic agent navigation.

## Original source and artifact

The original V1 selected one known automotive page: Autoevolution Artega GT (2010-2012), verified on 2026-08-19. A factual spec-table snapshot is retained under `data/raw/web/` as acquisition evidence.

The historical `AUTOEVOLUTION_ARTEGA_GT_RULES_V1` contains 12 deterministic label/parser mappings. Repeated extraction over a compatible structure reuses these rules and does not require fresh LLM inference. `AUTOEVOLUTION_ARTEGA_GT_RULES_V2` is additive and handles the bounded curb-weight structure documented below. `AUTOEVOLUTION_ARTEGA_GT_RULES` points to the current V2 artifact, while V1 remains explicitly addressable for historical replay.

Original validation established:

- required fields: 12;
- repeated-run equality: PASS;
- power normalization: PASS;
- changed structure: explicit failure PASS;
- direct silent field loss: NO.

## Source-family corpus characterization

The original one-page validation did not establish precision/recall or page coverage across a broader set of pages. The repository contains a frozen characterization corpus at:

```text
benchmarks/web_extraction_source_family_corpus_v1.json
```

with source snapshots under:

```text
data/raw/web/corpus-v1/
```

The corpus contains 12 independently inspected Autoevolution vehicle configurations across seven manufacturers and source pages spanning old and current page generations. It deliberately includes both structures compatible with the original artifact and observed incompatible structures:

- a required artifact field absent from a configuration;
- `Unladen Weight` represented as a range instead of one scalar value;
- a semantic target exposed under the label variant `Combined (EPA)` instead of exact `Combined`;
- multiple fuel, drivetrain, transmission and era combinations.

The corpus remains source-family evidence. It does **not** estimate production-wide, cross-site, or heterogeneous-web performance.

Historical V1 gold target facts and expected structural failures remain unchanged. Replay them through:

```text
PYTHONPATH=. python scripts/run_web_extraction_corpus.py
```

## Strict historical V1 result — 2026-08-23

`LOCALLY_VERIFIED` on frozen dataset `autoevolution-source-family-1.0`:

```text
configurations:              12
page successes:               8 / 12  (66.7%)
explicit failures:            4 / 12  (33.3%)
expected outcome agreement:  12 / 12  (100%)
target fields in sources:   142
emitted fields:              96
correct emitted fields:      96
field precision:              1.000
field recall:                96 / 142 (67.6%)
```

The four explicit failures were caused by observed source-shape limitations rather than incorrect emitted facts:

1. one BMW configuration omitted `Unladen Weight` entirely;
2. one Chevrolet Onix configuration omitted `Combined` entirely;
3. one Toyota Corolla Cross configuration represented `Unladen Weight` as a range;
4. one Nissan Pathfinder configuration represented weight as a range and also exposed consumption as `Combined (EPA)` rather than exact `Combined`.

Strict extractor semantics remain fail-fast: an unsupported required rule causes an explicit failure rather than returning a silently incomplete strict result.

## Explicit partial evidence retention — historical V1

The strict API remains unchanged in intent. The additive `extract_with_rules_report()` path preserves facts that were independently parsed and normalized correctly while also returning explicit per-field issues. A report with issues is **not** a strict page PASS and does not promote an incomplete record to a complete one.

Reusable rules may declare validated label aliases. `Combined (EPA)` is an explicit alias for the existing `fuel_economy_combined` rule. If both the canonical label and an alias occur simultaneously, extraction records an ambiguity rather than selecting one silently. Every extracted fact records the exact `source_label` observed in the source so alias handling does not erase provenance.

Historical V1 partial evidence can be reproduced with:

```text
PYTHONPATH=. python scripts/run_web_extraction_corpus.py --partial-evidence
```

`LOCALLY_VERIFIED` on the same frozen corpus:

```text
configurations:                    12
cases without issues:               8
cases with explicit issues:         4
explicit field issues:              4
target fields in sources:         142
emitted fields:                   140
correct emitted fields:           140
incorrect emitted fields:           0
unresolved source target fields:    2
field precision:                    1.000
retained field recall:            140 / 142 (98.6%)
```

The BMW and Onix snapshots each truly omit one artifact field, so those missing fields are recorded as `MISSING_FIELD` issues but are not counted as source target facts. Their other source facts are retained. In V1, the two source target weight ranges remain explicit parser mismatches.

## Bounded curb-weight artifact V2

Two frozen source records publish curb weight as a real interval:

```text
Toyota: 1490 - 1508 kg
Nissan: 1966 - 2036 kg
```

The current V2 artifact preserves these as bounded quantitative values rather than selecting a midpoint or endpoint. The normalized shape is strict JSON with canonical unit `kg`:

```json
{"minValue": 1490, "maxValue": 1508}
```

The representation direction is consistent with Schema.org `QuantitativeValue` (`minValue` / `maxValue`) and GoodRelations `QuantitativeValue`, which models lower/upper bounds with a unit and explicitly includes weight ranges. The internal exact JSON keys remain an `ENGINEERING_CHOICE`; the evidence-backed requirement is to preserve the interval rather than fabricate a point value.

Primary vocabulary references:

- https://schema.org/QuantitativeValue
- https://www.heppnetz.de/ontologies/goodrelations/v1.html

The bounded gold is additive and does not rewrite the historical corpus:

```text
benchmarks/web_extraction_bounded_values_v1.json
```

Evaluate the current V2 artifact strictly with:

```text
PYTHONPATH=. python scripts/run_web_extraction_corpus.py --bounded-values
```

or preserve partial evidence with:

```text
PYTHONPATH=. python scripts/run_web_extraction_corpus.py --bounded-values --partial-evidence
```

### Measured V2 result — 2026-08-23

`LOCALLY_VERIFIED` on the frozen corpus plus additive bounded gold:

```text
strict page successes:             10 / 12  (83.3%)
strict explicit failures:           2 / 12  (16.7%)
strict emitted/correct fields:    120 / 120
strict field precision:             1.000
strict field recall:              120 / 142 (84.5%)

partial cases without issues:      10 / 12
partial cases with issues:          2 / 12
partial emitted/correct fields:   142 / 142
partial incorrect fields:           0
partial unresolved target fields:   0
partial field precision:            1.000
partial retained field recall:      1.000
```

The two range cases are now supported source targets. The BMW and Onix records still expose explicit `MISSING_FIELD` issues because the corresponding values do not exist in those source snapshots. A missing source value is never invented to make a page complete.

Validation evidence for the implemented behavior: PR #51 merge-candidate run `32646934156`, job `97212517296`, Python `3.13.15`, `HARNESS PASS`, runtime health PASS and `335/335` repository tests executed one by one. Historical V1 replay, V2 bounded extraction, persistence/fusion compatibility, alias provenance, invalid/reversed ranges and Catalog JSON Contract 2.0 regression checks all passed in that run.

## Second source-family characterization — FuelEconomy.gov

A second source family was selected to test whether the same deterministic extraction machinery can be reused without assuming Autoevolution labels or provenance. The source is FuelEconomy.gov `Find a Car`, operated in the U.S. Department of Energy/EPA ecosystem. Its official web-service documentation defines vehicle fields and covers model years from 1984 through current data. The benchmark retains only the minimal factual label/value observations required for the test.

Official reference:

- https://www.fueleconomy.gov/feg/ws/index.shtml

Frozen benchmark:

```text
benchmarks/web_extraction_fueleconomy_source_family_v1.json
```

Factual observations:

```text
data/raw/web/fueleconomy-v1/
```

The four cases use FuelEconomy vehicle IDs `48897`, `42793`, `45011`, and `38187`. The separate `FUELECONOMY_GOV_VEHICLE_RULES_V1` artifact targets only three fields: combined gasoline fuel economy, drivetrain, and fuel type. Extraction-rule provenance uses the `fueleconomy_gov` namespace rather than reusing an Autoevolution rule identity.

The source exposes a useful semantic boundary. Gasoline values such as `23 MPG` are accepted by the existing US-MPG normalization rule, and the PHEV label `Combined MPG on Gas Only` is an explicit alias with its exact observed label retained. Electric vehicle pages expose values such as `131 MPGe` and `119 MPGe`; the anchored gasoline-MPG parser rejects these values. Podium does not run MPGe through the MPG-to-L/100km formula merely because the strings share the letters `MPG`.

Reproduce strict evaluation with:

```text
PYTHONPATH=. python scripts/run_fueleconomy_web_corpus.py
```

and facts+issues preservation with:

```text
PYTHONPATH=. python scripts/run_fueleconomy_web_corpus.py --partial-evidence
```

### Measured second-family result — 2026-08-23

`LOCALLY_VERIFIED` on dataset `fueleconomy-find-a-car-source-family-1.0`:

```text
strict configurations:             4
strict page successes:             2 / 4  (50.0%)
strict explicit failures:          2 / 4  (50.0%)
strict expected agreement:         4 / 4  (100%)
strict target fields:             12
strict emitted/correct fields:     6 / 6
strict field precision:            1.000
strict field recall:               6 / 12 (50.0%)

partial cases without issues:      2 / 4
partial cases with issues:         2 / 4
partial explicit issues:           2
partial target fields:            12
partial emitted/correct fields:   10 / 10
partial incorrect fields:          0
partial unresolved target fields:  2
partial field precision:           1.000
partial retained field recall:    10 / 12 (83.3%)
```

The two unresolved targets are both MPGe observations. They remain explicit `PARSER_MISMATCH` evidence, while drivetrain and fuel-type facts from the same electric pages are retained correctly in partial mode. The first implementation CI exposed a separate normalization gap for official hyphenated drive labels; explicit aliases were added for labels including `Front-Wheel Drive`, `All-Wheel Drive`, and `Part-time 4-Wheel Drive`, preserving raw text while mapping to existing Podium drivetrain tokens.

Implementation validation evidence: PR #53 merge-candidate run `32648780263`, job `97217035510`, Python `3.13.15`, `HARNESS PASS`, runtime health PASS and `343/343` repository tests executed one by one. Validation artifact ID `9495597465`, ZIP SHA-256 `fb0c35d3e83ede4273fecbc6133309ca8cb3782639cc99de7c426f300a6522ca`.

## Classification

- discover/configure/reuse direction: `EVIDENCE_BACKED`;
- exact source and regex rule format: `ENGINEERING_CHOICE`;
- frozen Autoevolution source-family corpus design and metrics: `ENGINEERING_CHOICE`, grounded in the documented measurement gap;
- strict historical Autoevolution V1 source-family precision/recall and page coverage: `LOCALLY_VERIFIED`;
- historical Autoevolution V1 explicit partial-evidence retention metrics: `LOCALLY_VERIFIED`;
- Autoevolution V2 bounded source-family metrics above: `LOCALLY_VERIFIED`;
- second-family FuelEconomy.gov strict/partial metrics above: `LOCALLY_VERIFIED`;
- choosing the exact three-field FuelEconomy.gov artifact, corpus cases and source-specific namespace: `ENGINEERING_CHOICE`;
- facts+issues report shape, declared alias mechanism and exact `source_label` provenance field: `ENGINEERING_CHOICE`;
- preserve observed curb-weight intervals without scalar collapse: `EVIDENCE_BACKED` direction;
- `minValue` / `maxValue` internal JSON representation and curb-weight-only V2 parser boundary: `ENGINEERING_CHOICE`;
- refusing to reinterpret MPGe as gasoline MPG: `EVIDENCE_BACKED` semantic boundary from the observed source distinction and existing normalization contract;
- a future canonical MPGe representation/conversion: `UNKNOWN / NOT SELECTED`;
- heterogeneous-web / production precision and recall: `UNKNOWN`.

## Evidence boundary

The two frozen source-family corpora establish repository-local reuse of deterministic extraction machinery and explicit provenance across Autoevolution and FuelEconomy.gov. They cannot establish:

- performance on arbitrary websites;
- acquisition/navigation completeness;
- production source distribution;
- a general semantic mapping for MPGe;
- that all quantitative properties should accept ranges;
- whether one global rule set, per-template rules, optional-field schemas, variant-aware parsers, or another artifact strategy is the correct broader design.

Any follow-up architecture choice must be driven by measured failure modes and the existing invariants: preserve source evidence, keep unresolved information explicit, and keep reusable extraction artifacts inspectable.

## Gate

Historical Autoevolution V1 gates remain reproducible and unchanged.

Bounded Autoevolution V2 gate:

- historical V1 metrics unchanged: PASS;
- exact source range and source label preserved: PASS;
- no midpoint/endpoint scalar fabrication: PASS;
- bounded values normalized to canonical `kg`: PASS;
- malformed/reversed/unsupported bounded values fail explicitly: PASS;
- missing source fields remain explicit issues: PASS;
- bounded gold remains additive/versioned: PASS;
- persistence/domain compatibility: PASS;
- Catalog JSON Contract `2.0` unchanged: PASS.

Second-family FuelEconomy.gov gate:

- separate source-family artifact and provenance namespace: PASS;
- frozen factual source observations and independent gold: PASS;
- gasoline MPG and gas-only alias supported: PASS;
- MPGe rejected by gasoline-MPG semantics: PASS;
- valid facts retained alongside MPGe issues: PASS;
- official hyphenated drivetrain labels normalized deterministically: PASS;
- historical Autoevolution regression suite unchanged: PASS;
- heterogeneous-web / production generalization: **not established**.
