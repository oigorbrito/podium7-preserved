# Podium 7 Repeatable Web Extraction V1

**Work unit:** `PODIUM7_REPEATABLE_WEB_EXTRACTION_V1`

## Scientific basis

WebLists supports discover/configure/reuse for repeated structured extraction; SODIUM, WideSearch, WebDS, and WANDR motivate explicit evidence and measured completeness rather than trusting generic agent navigation.

## Original source and artifact

The original V1 selected one known automotive page: Autoevolution Artega GT (2010-2012), verified on 2026-08-19. A factual spec-table snapshot is retained under `data/raw/web/` as acquisition evidence.

`AUTOEVOLUTION_ARTEGA_GT_RULES` contains 12 deterministic label/parser mappings. Repeated extraction over a compatible structure reuses these rules and does not require fresh LLM inference.

Original validation established:

- required fields: 12;
- repeated-run equality: PASS;
- power normalization: PASS;
- changed structure: explicit failure PASS;
- direct silent field loss: NO.

## Source-family corpus characterization

The original one-page validation did not establish precision/recall or page coverage across a broader set of pages. The repository now contains a frozen characterization corpus at:

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

Gold target facts and expected structural failures are stored independently of extractor output. The strict artifact can be evaluated through:

```text
PYTHONPATH=. python scripts/run_web_extraction_corpus.py
```

## Strict measured result — 2026-08-23

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

Strict extractor semantics remain fail-fast: an unsupported required rule causes an explicit failure rather than returning a silently incomplete strict result. The strict Pathfinder run therefore still stops on the unsupported weight range before returning a successful page result.

## Explicit partial evidence retention — 2026-08-23

The strict API remains unchanged in intent. A second additive path, `extract_with_rules_report()`, now preserves facts that were independently parsed and normalized correctly while also returning explicit per-field issues. A report with issues is **not** a strict page PASS and does not promote an incomplete record to a complete one.

Reusable rules may declare validated label aliases. `Combined (EPA)` is an explicit alias for the existing `fuel_economy_combined` rule. If both the canonical label and an alias occur simultaneously, extraction records an ambiguity rather than selecting one silently. Every extracted fact records the exact `source_label` observed in the source so alias handling does not erase provenance.

The report path can be reproduced with:

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

The distinction between artifact requirements and source targets matters. The BMW and Onix snapshots each truly omit one artifact field, so those missing fields are recorded as `MISSING_FIELD` issues but are not counted as source target facts. Their other source facts are retained. The two unresolved source target fields are the non-scalar `curb_weight` ranges in the Toyota and Nissan cases. They remain unresolved deliberately; their raw values are preserved in `PARSER_MISMATCH` issues instead of being collapsed to arbitrary scalar weights.

For the Nissan case, the report path independently extracts the `Combined (EPA)` value through the declared alias while still recording the unsupported weight range. Thus the source-label variation is supported without weakening the unresolved non-scalar weight semantics.

The report path improves retained evidence coverage on this corpus without changing the meaning of strict success. It does not establish heterogeneous-web performance, and it does not select a future semantic representation for ranges.

## Classification

- discover/configure/reuse direction: `EVIDENCE_BACKED`;
- exact source and regex rule format: `ENGINEERING_CHOICE`;
- frozen source-family corpus design and metrics: `ENGINEERING_CHOICE`, grounded in the documented measurement gap;
- strict source-family precision/recall and page coverage: `LOCALLY_VERIFIED`;
- explicit partial-evidence retention metrics above: `LOCALLY_VERIFIED`;
- facts+issues report shape, declared alias mechanism and exact `source_label` provenance field: `ENGINEERING_CHOICE`;
- remaining non-scalar weight semantics: `UNKNOWN / NOT SELECTED`;
- heterogeneous-web / production precision and recall: `UNKNOWN`.

## Evidence boundary

The source-family corpus establishes what the current reusable artifact does on the frozen Autoevolution configurations in the repository. It cannot establish:

- performance on arbitrary websites;
- acquisition/navigation completeness;
- production source distribution;
- the correct canonical representation for non-scalar values such as weight ranges;
- whether one global rule set, per-template rules, optional-field schemas, variant-aware parsers, or another artifact strategy is the correct broader design.

Any follow-up architecture choice must be driven by measured failure modes and the existing invariants: preserve source evidence, keep unresolved information explicit, and keep reusable extraction artifacts inspectable.

## Gate

Original V1 gate remains historical evidence:

- `REPEATABLE_EXTRACTION = PASS` on the original compatible page;
- direct silent field loss: NO.

Source-family strict characterization gate:

- frozen source evidence: PASS;
- independent gold targets: PASS;
- strict structural failures preserved: PASS;
- strict source-family metrics recorded as `LOCALLY_VERIFIED`: PASS.

Explicit partial-evidence gate:

- strict API remains fail-fast: PASS;
- valid facts preserved alongside explicit issues: PASS;
- no arbitrary scalar produced from weight ranges: PASS;
- declared alias ambiguity fails explicitly: PASS;
- observed source label preserved on extracted facts: PASS;
- partial-evidence source-family metrics recorded as `LOCALLY_VERIFIED`: PASS;
- heterogeneous-web / production generalization: **not established**.
