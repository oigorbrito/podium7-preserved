# Podium 7 Repeatable Web Extraction V1

**Work unit:** `PODIUM7_REPEATABLE_WEB_EXTRACTION_V1`

## Scientific basis

WebLists supports discover/configure/reuse for repeated structured extraction; SODIUM, WideSearch, WebDS, and WANDR motivate explicit evidence and measured completeness rather than trusting generic agent navigation.

## Source

One known automotive page was selected: Autoevolution Artega GT (2010-2012), verified on 2026-08-19. A factual spec-table snapshot is retained under `data/raw/web/` as acquisition evidence.

## Compiled artifact

`AUTOEVOLUTION_ARTEGA_GT_RULES` contains deterministic label/parser mappings. The second extraction over the same compatible structure reuses these rules and does not require fresh LLM inference.

## Validation

- required fields: 12
- repeated-run equality: PASS
- power normalization: PASS
- changed structure: explicit failure PASS
- direct silent field loss: NO

## Classification

- discover/configure/reuse direction: `EVIDENCE_BACKED`
- exact source and regex rule format: `ENGINEERING_CHOICE`
- measured precision/recall on a broad page corpus: `UNKNOWN`

## Gate

- `REPEATABLE_EXTRACTION = PASS`
- web extraction tests: 4/4 PASS, run individually
- cumulative tests run individually: 36/36 PASS
