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

## Classification

- discover/configure/reuse direction: `EVIDENCE_BACKED`;
- exact source and regex rule format: `ENGINEERING_CHOICE`;
- frozen source-family corpus design and metrics: `ENGINEERING_CHOICE`, grounded in the documented measurement gap;
- strict historical V1 source-family precision/recall and page coverage: `LOCALLY_VERIFIED`;
- historical V1 explicit partial-evidence retention metrics: `LOCALLY_VERIFIED`;
- V2 bounded source-family metrics above: `LOCALLY_VERIFIED`;
- facts+issues report shape, declared alias mechanism and exact `source_label` provenance field: `ENGINEERING_CHOICE`;
- preserve observed curb-weight intervals without scalar collapse: `EVIDENCE_BACKED` direction;
- `minValue` / `maxValue` internal JSON representation and curb-weight-only V2 parser boundary: `ENGINEERING_CHOICE`;
- heterogeneous-web / production precision and recall: `UNKNOWN`.

## Evidence boundary

The source-family corpus establishes what the reusable artifacts do on the frozen Autoevolution configurations in the repository. It cannot establish:

- performance on arbitrary websites;
- acquisition/navigation completeness;
- production source distribution;
- that all quantitative properties should accept ranges;
- whether one global rule set, per-template rules, optional-field schemas, variant-aware parsers, or another artifact strategy is the correct broader design.

Any follow-up architecture choice must be driven by measured failure modes and the existing invariants: preserve source evidence, keep unresolved information explicit, and keep reusable extraction artifacts inspectable.

## Gate

Historical V1 gates remain reproducible and unchanged.

Bounded V2 gate:

- historical V1 metrics unchanged: PASS;
- exact source range and source label preserved: PASS;
- no midpoint/endpoint scalar fabrication: PASS;
- bounded values normalized to canonical `kg`: PASS;
- malformed/reversed/unsupported bounded values fail explicitly: PASS;
- missing source fields remain explicit issues: PASS;
- bounded gold remains additive/versioned: PASS;
- persistence/domain compatibility: PASS;
- Catalog JSON Contract `2.0` unchanged: PASS;
- heterogeneous-web / production generalization: **not established**.
