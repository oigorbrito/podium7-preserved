# Post-MVP source acquisition execution plan V1

Status: active
Parent mission: #122
Current block: #123

## Outcome

Expand Podium 7's evidence-backed automotive acquisition/enrichment layer using multiple qualified sources without changing existing evidence, fusion, ambiguity, identity-resolution, or publication principles.

## Acceptance criteria

- Existing evaluated source evidence is reconstructed before any retest.
- Measured catalog evidence gaps are recorded durably and separated from transport/access limitations.
- New source discovery is driven only by measured gaps and uses primary/official or otherwise documentably defensible evidence.
- Every selected source receives an explicit semantic/provenance contract before implementation.
- Multi-source enrichment preserves conflicts, abstention/`REVIEW`, and complete provenance rather than guessing missing values.
- Bounded measurements show source contribution and conflict behavior with no identity-safety regression.

## Boundaries / non-goals

- Do not alter the project's existing evidence hierarchy, source principles, semantic conservatism, ambiguity handling, fusion/conflict rules, or publication gate without explicit owner authorization.
- Do not use Reddit, forums, blogs, search snippets, or opaque aggregators as canonical evidence.
- Do not introduce stealth, proxy rotation, CAPTCHA/challenge bypass, or alternate identities.
- Do not rerun historical source batteries merely because chat context is incomplete.
- Do not claim production-wide or universal automotive coverage from bounded measurements.

## Sources of truth

- `docs/DEVELOPMENT-WORKFLOW.md`
- `docs/INVARIANTS.md`
- `docs/CATALOG-IDENTITY-V2.md`
- `docs/CATALOG-EVIDENCE-POLICY-V2.md`
- `docs/DATA-FUSION-AND-CONFLICTS-V1.md`
- `docs/CANDIDATE-EVALUATION-LEDGER.md`
- `docs/COMPLIANT-ALTERNATIVE-SOURCES-V1.md`
- source/acquisition/provenance contracts indexed by `docs/INDEX.md`

## Execution sequence

1. #123 — reconstruct current source baseline and produce `SOURCE-EVIDENCE-GAP-MATRIX-V1.md`.
2. #124 — qualify only the smallest current source set needed to address measured gaps.
3. #125 — define source-specific semantic/provenance contracts before coding adapters.
4. #126 — implement bounded approved adapters with deterministic fail-closed behavior.
5. #127 — validate multi-source fusion, corroboration, conflicts, review load and provenance.
6. #128 — operationalize recurring acquisition safely, including drift/outage handling.

## Current evidence reconstruction — #123

No broad retest is justified. Recoverable durable evidence already establishes:

- the catalog identity dimensions and conservative resolver semantics in `CATALOG-IDENTITY-V2.md`;
- current evaluated source dispositions in `CANDIDATE-EVALUATION-LEDGER.md` and `COMPLIANT-ALTERNATIVE-SOURCES-V1.md`;
- bounded three-region source diversity in `PRODUCTION-SOURCE-DISTRIBUTION-V1.md`;
- a 60-record source-backed replay with 22 `REVIEW` outcomes in `PRODUCTION-OPERATIONAL-MEASUREMENT-V1.md`;
- measured review causes of 13 `MISSING_IDENTITY_EVIDENCE` and 9 `LABEL_AMBIGUITY` in `PRODUCTION-OPERATIONAL-GAP-PRIORITY-V1.md`.

The durable gap matrix is `docs/SOURCE-EVIDENCE-GAP-MATRIX-V1.md`.

## Decisions

- Existing source evidence is reused as long as its version/scope remains adequate for the decision.
- Transport availability, semantic coverage, identity strength, market scope, and reuse/access status are tracked separately.
- A field exposed by a source is not automatically identity proof; source semantics govern its role.
- Missing or conflicting evidence stays explicit. Resolver/evidence thresholds are not tuned merely to improve coverage.

## Validation / blockers

#123 is documentation/evidence reconstruction only; no executable behavior is changed and no external source retest is required. Repository harness/CI validation remains required according to `DEVELOPMENT-WORKFLOW.md` before integration. Issue #112 may still block normal GitHub-hosted execution; use only the repository's documented accepted validation path and do not introduce runner workarounds.
