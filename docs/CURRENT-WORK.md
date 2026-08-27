# Current work

Status: active post-MVP measurement

Outcome: measure consumer-visible coverage of `powertrain`, `transmission`, and `body_style` through the existing Production Corpus V2 ingestion/resolution/consumer path before any downstream BPT2 field or filter decision.

Boundaries: measurement only. No resolver policy change, new source family, BPT2 schema/filter change, or arbitrary readiness threshold.

Acceptance: report present/missing counts, coverage ratio, raw/normalized cardinality and market breakdown on canonical vehicles returned by the consumer API; keep the result explicitly bounded to the retained source-backed corpus; validate focused behavior and repository harness.

Active plan: [`exec-plans/active/CATALOG-IDENTITY-FIELD-COVERAGE-V1.md`](exec-plans/active/CATALOG-IDENTITY-FIELD-COVERAGE-V1.md)

Issue #112, `Restore GitHub Actions hosted-runner execution`, remains infrastructure/operations debt. If hosted CI is still unable to create workflow steps, do not misreport it as product-test failure or add runner workarounds.
