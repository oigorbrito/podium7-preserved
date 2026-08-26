# Production Quality Measurement V2 execution plan

Status: active

Parent mission: #139
Issue: #141
Depends on: #140 / Production Corpus Run V3

## Outcome and acceptance criteria

Measure identity safety and operational review load on the 72-record / 36-case V3 source-backed corpus using the repository's existing quality and operational measurement paths.

Acceptance:

- evaluate all four V3 identity gold sets through `evaluate_identity_quality`;
- evaluate the same four datasets through `measure_source_backed_operational_corpus`;
- report auto-match precision/recall, false merges, missed matches, ambiguous overcommit, review rate, CREATED/MATCHED/REVIEW/failure distribution and durable review causes;
- verify every operational replay record retains an HTTPS locator and deterministic benchmark raw-content reference;
- preserve existing resolver/evidence/fusion/publication policy regardless of measured values;
- do not create follow-up source/region/semantic/resolver work until executable results establish a concrete gap.

## Evidence granularity boundary

The current gold schema binds `sourceIds` at case level, not field/dimension level. Therefore this block must not invent per-dimension source attribution. If executable measurement confirms that dimension-level contribution is required for a downstream decision, record that as an instrumentation gap rather than assigning unsupported field provenance.

## Implementation steps

1. Add a V2 measurement test over the four V3 datasets.
2. Assert corpus/case cardinality and safety invariants without hard-coding unexecuted outcome counts.
3. Add provenance-completeness assertions over the 72 operational records.
4. Add a design record describing what can and cannot be measured from the current corpus schema.
5. Run focused and repository-required validation when runners execute; until then, keep numerical results pending.

## Validation blocker

Issue #112 currently prevents GitHub-hosted jobs from executing workflow steps. Do not publish guessed metrics and do not treat no-step failures as test results.
