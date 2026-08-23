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

- a required target field absent from a configuration;
- `Unladen Weight` represented as a range instead of one scalar value;
- a semantic target exposed under the label variant `Combined (EPA)` instead of exact `Combined`;
- multiple fuel, drivetrain, transmission and era combinations.

The corpus remains source-family evidence. It does **not** estimate production-wide, cross-site, or heterogeneous-web performance.

Gold target facts and expected structural failures are stored independently of extractor output. The existing `AUTOEVOLUTION_ARTEGA_GT_RULES` were evaluated unchanged through:

```text
PYTHONPATH=. python scripts/run_web_extraction_corpus.py
```

## Measured result — 2026-08-23

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

The Pathfinder run stops explicitly at the earlier unsupported weight-range field, so the label variation remains independently visible in the frozen source evidence but is not reached by the current strict extractor.

Strict extractor semantics remain intentional in this characterization: an unsupported required field causes an explicit failure rather than returning a silently incomplete record. Consequently, precision among emitted facts is perfect on this corpus while page coverage and field recall are materially lower. The result identifies **coverage/generalization of reusable artifacts** as a real local gap; it does not support weakening explicit-failure behavior.

CI evidence for the first measured merge candidate: GitHub Actions run `32643262400`, job `97203527673`; focused corpus tests passed and the repository suite completed `309/309` tests one by one.

## Classification

- discover/configure/reuse direction: `EVIDENCE_BACKED`;
- exact source and regex rule format: `ENGINEERING_CHOICE`;
- frozen source-family corpus design and metrics: `ENGINEERING_CHOICE`, grounded in the documented measurement gap;
- source-family precision/recall and page coverage above: `LOCALLY_VERIFIED`;
- observed coverage/generalization gap: `LOCALLY_VERIFIED`;
- heterogeneous-web / production precision and recall: `UNKNOWN`.

## Evidence boundary

The source-family corpus establishes what the current reusable artifact does on the frozen Autoevolution configurations in the repository. It cannot establish:

- performance on arbitrary websites;
- acquisition/navigation completeness;
- production source distribution;
- whether one global rule set, per-template rules, optional-field schemas, variant-aware parsers, or another artifact strategy is the correct future design.

Any follow-up architecture choice must be driven by the measured failure modes and the existing invariants: preserve source evidence, fail explicitly rather than silently losing fields, and keep reusable extraction artifacts inspectable. The exact remediation remains an `ENGINEERING_CHOICE`; this characterization does not select it.

## Gate

Original V1 gate remains historical evidence:

- `REPEATABLE_EXTRACTION = PASS` on the original compatible page;
- web extraction tests: 4/4 PASS, run individually;
- cumulative tests at that work unit: 36/36 PASS.

Source-family characterization gate:

- frozen source evidence: PASS;
- independent gold targets: PASS;
- existing artifact evaluated unchanged: PASS;
- explicit structural failures preserved: PASS;
- source-family metrics recorded as `LOCALLY_VERIFIED`: PASS;
- heterogeneous-web / production generalization: **not established**.
