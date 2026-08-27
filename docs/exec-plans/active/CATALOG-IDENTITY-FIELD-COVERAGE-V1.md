# Catalog Identity Field Coverage V1

Status: active

## Outcome

Measure consumer-visible coverage of `powertrain`, `transmission`, and `body_style` using the existing Production Corpus V2 path before any downstream BPT2 field decision.

## Acceptance

- replay the three retained identity datasets through the existing operational path;
- measure canonical vehicles returned by the consumer API;
- report present/missing, coverage, raw/normalized cardinality, and market breakdown;
- keep the result explicitly bounded to the retained corpus;
- validate the focused test and repository harness before integration.

## Non-goals

No resolver change, new data source, BPT2 schema change, filter implementation, or arbitrary readiness threshold.

## References

- `docs/PRODUCTION-CORPUS-RUN-V2.md`
- `docs/CATALOG-JSON-CONTRACT-V2.md`
- `tests/test_production_corpus_run_v2.py`
- `docs/DEVELOPMENT-WORKFLOW.md`

## Decision

The denominator is canonical vehicles returned by the consumer API after the real corpus replay, not source records. This measurement remains bounded evidence and does not establish production-wide completeness.

## Validation

Pending branch execution.
