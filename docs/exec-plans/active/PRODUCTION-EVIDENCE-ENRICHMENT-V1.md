# Production Evidence Enrichment V1

Status: active

## Outcome

Reduce measured catalog `REVIEW` load only when additional source-backed evidence justifies a stronger identity decision.

## Boundaries

- Preserve conservative Catalog Identity V2 semantics and the Senatran-aligned year rule.
- Do not weaken resolver thresholds or infer missing identity fields from labels alone.
- Public internet observations are operational evidence, not a permanent CI dependency.
- Official discovery candidates remain discovery evidence and are not upgraded to identity proof.
- Public/package release licensing is out of scope.

## Large blocks

1. Build a deterministic enrichment-work queue from measured review causes and retain explicit evidence requirements/source locators.
2. Apply source-backed identity and label enrichment under a fail-closed contract; unsupported/conflicting evidence remains `REVIEW`.
3. Replay the bounded corpus, measure before/after decisions, and establish the next integrated quality gate.

## Acceptance

- Every measured review task maps to explicit enrichment work or durable review with no unknown cause.
- At least one source-backed review case is demonstrably resolved without resolver-policy change, or the block records evidence that no safe resolution exists.
- Baseline identity precision/recall and zero-false-merge invariants do not regress.
- CI is green on the merge candidate and the cycle is documented without claiming production completeness.
