# ExtractBench-style extraction evaluation — issue #168

Status: benchmark contract prepared; hash-bound Inmetro gold retained; exact remote snapshot bytes not yet reproducibly retrievable; real-PDF comparison pending

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

## Snapshot provenance and retrievability

The official Inmetro PBEV page-1 gold remains bound to SHA-256 `cb8ab26789b75a596f75ebf5f6454f30950d31ff8fff1de99ad56a502679db2b`. Historical commit `d67718a103870e4894127dccd66d7ae52637635a` changed the gold from `PENDING_RAW_SNAPSHOT` to `RAW_SNAPSHOT_BOUND`, but repository inspection shows that commit added the digest/status only; it did not add the PDF bytes or a durable snapshot locator.

Fresh inspection of `main`, the retained ExtractBench backup branches, and the relevant GitHub Actions artifacts did not locate the exact bound PDF bytes. The benchmark therefore records `snapshotRetrievability = REMOTE_BYTES_UNRESOLVED` and `snapshotLocator = null` until #214 provides a reproducible locator whose retrieved bytes verify against the bound digest.

This does not assert that the original acquisition never retained bytes locally. It states only the narrower evidence-backed result: a fresh authorized runner cannot currently retrieve the exact bound bytes from the available remote repository/artifact evidence.

The upstream Inmetro locator is mutable-in-place and may not be used as archival substitution unless freshly acquired bytes hash exactly to the bound digest.

## Candidate-comparison disposition

`EXTRACTOR_COMPARISON = EXTRACTOR_COMPARISON_PENDING`

No extractor is currently declared better. `camelot-py` / `lattice` remains the first bounded comparison candidate, while the current Podium baseline remains `pdfplumber` with line-based table extraction. The same exact bound bytes/page must be fed to both. Until #214 makes those bytes reproducibly retrievable, no comparative result may be claimed from a current live-source substitute.

A replacement can only be proposed after reproducible material gain and still requires explicit owner consent.

## Safety

- Exact source/raw evidence and provenance remain mandatory.
- Missing/ambiguous fields remain absent or reviewable.
- No direct LLM/extractor canonical writes.
- No evidence/publication weakening.
- Targeted horizontal research is allowed when a measured gap justifies it.
- No material replacement without explicit owner consent.
- Mutable upstream URLs are not archival storage.
- A benchmark runner must fail closed if the expected bound bytes cannot be retrieved and digest-verified.

## Validation

Required before integration: repository harness, focused tests, sequential suite, project facts and real CI execution where available. The retrievability correction itself is documentation/fixture fail-closed hardening; it does not introduce an extractor, storage layer, source-policy change or canonical-write path.
