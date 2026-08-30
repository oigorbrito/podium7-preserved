# ExtractBench-style extraction evaluation — issue #168

Status: completed with `NO_MATERIAL_GAIN` disposition.

## Goal

Measure extraction quality with an executable, evidence-aware contract before evaluating or adopting any PDF/document extractor.

## Retained source boundary

The comparison uses the exact repository-retained Inmetro PBEV PDF fixture with SHA-256 `cb8ab26789b75a596f75ebf5f6454f30950d31ff8fff1de99ad56a502679db2b`, page 1. The historical gold was not rebound; #214 proved that freshly acquired official bytes were byte-identical to the existing digest and retained those exact bytes in the repository.

Only the seven fields already authorized by the extraction gold are scored: category, make, model, variant, motor, propulsion type and transmission. Quantitative columns remain excluded because their semantics are separately gated by #232.

## Comparison

Baseline: Podium `pdfplumber` line-based PBEV extraction, measured with pdfplumber 0.11.9.

Candidate: `camelot-py` 1.0.9 using lattice mode on the same PDF bytes and page.

The first real-PDF run exposed a baseline omission: `transmission` was not preserved in the source record, producing 18/21 correct authorized fields (85.7%). Issues #257 and #259, integrated through PRs #258 and #260, corrected the omission and hardened the parser for the real PDF's garbled transmission-header text without changing source authority, identity, canonical, evidence, fusion or publication rules.

After remediation, both extractors produced 21/21 correct authorized fields across the three retained gold cases. For both:

- schema-valid rate: 1.0;
- field correctness: 1.0;
- required-field recall: 1.0;
- hallucinated-field rate: 0.0;
- omitted-field rate: 0.0;
- evidence-linked field rate: 1.0;
- unsupported canonical write rate: 0.0.

Camelot lattice reported table parsing accuracies of 98.6%, 100.0% and 100.0% for its three page-1 tables, but this produced no decision-relevant improvement on the authorized gold fields after the baseline defect was corrected.

The deterministic retained comparison is `benchmarks/inmetro_pbev_extractor_comparison_v1.json`; repository tests recalculate the ExtractBench-style metrics from the retained observations and verify the source fixture digest.

## Disposition

`EXTRACTOR_COMPARISON = NO_MATERIAL_GAIN`

Retain pdfplumber as the current PBEV extractor. Camelot lattice remains a benchmarked alternative, not an adopted dependency or replacement. No owner-consent gate is triggered because no material replacement is proposed.

This disposition is bounded to the retained page-1 automotive-document slice and the seven authorized fields; it is not a claim that pdfplumber is globally superior for all PDFs or wider schemas.

## Safety

- exact source/raw evidence and provenance remain mandatory;
- no direct extractor canonical writes;
- unsupported canonical write rate remains zero;
- quantitative semantics remain gated by #232;
- no evidence/publication weakening occurred;
- no new infrastructure or production dependency was adopted.
