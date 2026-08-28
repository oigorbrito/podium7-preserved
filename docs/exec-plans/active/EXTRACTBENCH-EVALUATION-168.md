# ExtractBench-style extraction evaluation — issue #168

Status: benchmark contract prepared; real-PDF comparison pending

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

## Benchmark-contract utility disposition

`EXTRACTION_BENCHMARK_CONTRACT_UTILITY = INTEGRATE_AFTER_REPOSITORY_VALIDATION`

The measurement contract closes a real observability gap independent of which extractor eventually wins. Existing Podium identity-quality metrics cannot tell whether a document extractor produced schema-invalid output, omitted required fields, hallucinated fields, degraded on wider schemas, misaligned arrays, or emitted canonical writes without field-level evidence.

The evaluator is therefore useful as a durable acceptance harness even if the later extractor comparison concludes `NO_MATERIAL_GAIN`.

Audit hardening requires benchmark fixtures to use explicit container types, strict JSON-compatible values, unique evidence references, and finite numeric values; malformed fixtures fail closed rather than contaminating rates.

## Candidate-comparison disposition

`EXTRACTOR_COMPARISON = EXTRACTOR_COMPARISON_PENDING`

No extractor is currently declared better. The official Inmetro PBEV page-1 gold is now `RAW_SNAPSHOT_BOUND` with exact PDF bytes/SHA retained. The same evidence-bound gold must be used for current/candidate extraction comparison. A replacement can only be proposed after reproducible material gain and still requires explicit owner consent.

## Safety

- Exact source/raw evidence and provenance remain mandatory.
- Missing/ambiguous fields remain absent or reviewable.
- No direct LLM/extractor canonical writes.
- No evidence/publication weakening.
- Targeted horizontal research is allowed when a measured gap justifies it.
- No material replacement without explicit owner consent.

## Validation

Required before integration: repository harness, focused tests, sequential suite, project facts and real CI execution where available. Issue #112 remains an independent hosted-runner blocker and must not be represented as a code failure or green run when no steps execute.
