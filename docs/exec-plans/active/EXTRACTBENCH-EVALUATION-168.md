# ExtractBench-style extraction evaluation — issue #168

Status: active

## Goal

Measure extraction quality with an executable, evidence-aware contract before evaluating or adopting any PDF/document extractor.

## Baseline

Podium already preserves source/raw evidence and routes unsupported/ambiguous identity claims conservatively, but `main` has no dedicated PDF-to-structured benchmark contract covering schema validity, field correctness, omission/hallucination, schema width and field-level evidence linkage.

## Work

1. Freeze deterministic evaluation metrics without changing extraction or publication behavior.
2. Validate the evaluator with focused regressions, including the hard gate `unsupportedCanonicalWriteRate = 0` for a safe candidate.
3. Build a bounded automotive-document fixture/corpus only from defensible retained evidence or qualified source material.
4. Compare the current available Podium extraction path, if any, with candidate schema-executable extraction approaches using identical fixtures.
5. Record `CURRENT_BETTER`, `NEW_BETTER`, `COMPLEMENTARY`, or `NO_MATERIAL_GAIN`.
6. Any material replacement remains owner-consent gated after reproducible measurements.

## Current block

The measurement contract is implemented in `podium7/extraction_quality_benchmark.py` with focused tests. No extractor has been adopted or replaced. No real-PDF superiority result is claimed yet.

## Safety

- Exact source/raw evidence and provenance remain mandatory.
- Missing/ambiguous fields remain absent or reviewable.
- No direct LLM/extractor canonical writes.
- No evidence/publication weakening.
- Targeted horizontal research is allowed only when a measured gap justifies it.
- No material replacement without explicit owner consent.

## Validation

Required before integration: repository harness, focused tests, sequential suite, project facts and real CI execution where available. Issue #112 remains an independent hosted-runner blocker and must not be represented as a code failure or green run when no steps execute.
