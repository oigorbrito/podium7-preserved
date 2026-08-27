# Catalog Identity Field Coverage V1

Status: active

## Outcome

Measure consumer-visible coverage of `powertrain`, `transmission`, and `body_style` using the existing Production Corpus V2 path before any downstream BPT2 field decision.

## Acceptance

- replay the three retained identity datasets through the existing operational path;
- measure all canonical vehicles returned by the consumer API using cursor pagination, with no fixed population ceiling;
- report present/missing, coverage, raw/normalized cardinality, normalization collisions and market breakdown;
- report isolated dataset/source-family evidence slices through the same operational path;
- expose the current operational review count and state explicitly when field-level contradiction attribution is unavailable;
- bind the report to the consumer contract version and retained datasets;
- keep the result explicitly bounded to the retained corpus;
- validate the focused test and repository harness before integration.

## Non-goals

No resolver change, new data source, BPT2 schema change, filter implementation, semantic taxonomy normalization or arbitrary readiness threshold.

## References

- `docs/PRODUCTION-CORPUS-RUN-V2.md`
- `docs/CATALOG-JSON-CONTRACT-V2.md`
- `tests/test_production_corpus_run_v2.py`
- `docs/DEVELOPMENT-WORKFLOW.md`

## Decision

The denominator is every canonical vehicle returned by the consumer API after the real corpus replay, not source records and not the first API page. Dataset breakdowns are isolated evidence slices only; dataset/source is not promoted into catalog identity. Review evidence remains aggregate when the operational pipeline does not expose field-level attribution; the measurement must not invent contradiction ownership. This remains bounded evidence and does not establish production-wide completeness.

## Progress log

- 2026-08-27 — initial bounded measurement implemented over Production Corpus V2.
- 2026-08-27 — audit found three consumer-contract gaps: fixed `limit=100`, no dataset/source-family breakdown and no explicit review/contradiction granularity statement.
- 2026-08-27 — measurement hardened to cursor-pagination of all consumer vehicles, isolated per-dataset replay, contract-version binding and fail-honest aggregate review evidence.

## Validation

Focused branch validation pending on the hardened head. Hosted GitHub Actions issue #112 remains a separate infrastructure condition when jobs fail before workflow steps are created.
