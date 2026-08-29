# Catalog Identity Field Coverage V1

Status: active

## Outcome

Measure consumer-visible coverage of `powertrain`, `transmission`, and `body_style` using the existing Production Corpus V2 path before any downstream BPT2 field decision.

## Acceptance

- replay the three retained identity datasets through the existing operational path;
- measure all canonical vehicles returned by the consumer API using cursor pagination, with no fixed population ceiling;
- prove the measurement reads beyond the consumer API's 100-item maximum page size;
- prove repeated measurement of the same retained inputs yields an equivalent report;
- report known/present versus contract-defined unknown (`null`), coverage, raw/normalized cardinality and normalization collisions;
- fail explicitly if a measured consumer key is missing, blank or has a JSON type outside the frozen Catalog `2.0` contract instead of counting contract violations as coverage misses;
- report market breakdown and an explicit exact-code `BR` slice without inventing a geographic taxonomy;
- report isolated per-dataset evidence slices through the same operational path;
- do not claim source-family attribution unless the published/operational data exposes a source-family dimension independently of dataset identity;
- expose the current operational review count and state explicitly when field-level contradiction attribution is unavailable;
- bind the report to the consumer contract version and each retained dataset's schema, dataset version and SHA-256 digest;
- allow deterministic JSON to be emitted to stdout or retained through an explicit output path;
- keep the result explicitly bounded to the retained corpus;
- validate the focused test, repository harness and repository one-by-one suite before integration.

## Non-goals

No resolver change, new data source, BPT2 schema change, filter implementation, semantic taxonomy normalization or arbitrary readiness threshold.

## References

- `docs/PRODUCTION-CORPUS-RUN-V2.md`
- `docs/CATALOG-JSON-CONTRACT-V2.md`
- `tests/test_production_corpus_run_v2.py`
- `docs/DEVELOPMENT-WORKFLOW.md`

## Decision

The denominator is every canonical vehicle returned by the consumer API after the real corpus replay, not source records and not the first API page. Catalog contract `2.0` guarantees the measured keys exist and uses JSON `null` for unknown, so the report treats null as the unknown knowledge state and rejects missing/blank/wrong-type values as contract violations. Dataset breakdowns are isolated evidence slices only; a dataset name is not treated as proof of source-family attribution and dataset/source is not promoted into catalog identity. `BR` is highlighted only as the exact market code already present in the retained corpus. Review evidence remains aggregate when the operational pipeline does not expose field-level attribution; the measurement must not invent contradiction ownership. This remains bounded evidence and does not establish production-wide completeness.

## Progress log

- 2026-08-27 — initial bounded measurement implemented over Production Corpus V2.
- 2026-08-27 — audit found three consumer-contract gaps: fixed `limit=100`, no isolated dataset breakdown and no explicit review/contradiction granularity statement.
- 2026-08-27 — measurement hardened to cursor-pagination of all consumer vehicles, isolated per-dataset replay, contract-version binding and fail-honest aggregate review evidence.
- 2026-08-28 — BPT2 consumer-contract reconciliation found remaining precision gaps: `missing` conflated contract-defined unknown with invalid shape, Brazil was only implicit in generic market output, and retained inputs were bound only by filename.
- 2026-08-28 — report hardened to `present + unknownNull`, contract-shape failure, explicit exact-code `BR` slice, dataset schema/version/SHA-256 identity and optional deterministic JSON output file.
- 2026-08-28 — focused tests added to prove consumer pagination beyond 100 vehicles and deterministic repeated reporting; source-family language narrowed to per-dataset evidence because the current consumer/operational projection does not independently expose source-family attribution.

## Validation

Focused branch validation remains pending on the hardened head. Hosted GitHub Actions issue #112 remains a separate infrastructure condition when jobs fail before workflow steps are created. Do not rerun unchanged hosted Actions or reinterpret pre-step runner failure as product-test evidence.
