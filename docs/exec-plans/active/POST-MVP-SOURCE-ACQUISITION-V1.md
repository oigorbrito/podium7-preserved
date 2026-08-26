# Post-MVP source acquisition execution plan V1

Status: implementation prepared through #128; integration/executable validation pending
Parent mission: #122
Current block: #128 complete on branch; mission pending repository validation

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
- `docs/SOURCE-EVIDENCE-GAP-MATRIX-V1.md`
- `docs/SOURCE-QUALIFICATION-V1.md`
- `docs/NHTSA-VPIC-EVIDENCE-CONTRACT-V1.md`
- `docs/EEA-EVIDENCE-CONTRACT-V2.md`
- source/acquisition/provenance contracts indexed by `docs/INDEX.md`

## Execution sequence

1. #123 — reconstruct current source baseline and produce `SOURCE-EVIDENCE-GAP-MATRIX-V1.md`. **Prepared on branch; integration pending repository validation availability.**
2. #124 — qualify only the smallest current source set needed to address measured gaps. **Prepared.**
3. #125 — define source-specific semantic/provenance contracts before coding adapters. **Prepared for NHTSA vPIC and EEA; restricted WSDenatran intentionally deferred.**
4. #126 — implement bounded approved adapters with deterministic fail-closed behavior. **Prepared; focused contracts hardened against malformed boolean/int coercion.**
5. #127 — validate multi-source fusion, corroboration, conflicts, review load and provenance. **Prepared; validation fixtures reject duplicate/malformed cases.**
6. #128 — operationalize recurring acquisition safely, including drift/outage handling. **Prepared; integration/executable validation pending.**

## #123 evidence reconstruction

Recoverable durable evidence established the source baseline and measured primary gaps: 13 `MISSING_IDENTITY_EVIDENCE` and 9 `LABEL_AMBIGUITY` review causes on the retained 60-record replay. No broad retest was justified.

## #124 targeted qualification

- NHTSA vPIC remains `ADAPT` within documented U.S. discovery/VIN semantics.
- EEA passenger-car monitoring remains `ADAPT` within EU regulatory/type-approval semantics.
- WSDenatran is `UNDECIDED` for automated use because official access requires SENATRAN authorization and SERPRO contracting.
- SENATRAN fleet and CAT/SISCAT remain `REFERENCE`, not substitutes for row-level identity evidence.
- Manufacturer-published primary artifacts remain a case-bound `REFERENCE` evidence class.

## #125 contracts

### NHTSA vPIC

`NHTSA-VPIC-EVIDENCE-CONTRACT-V1.md` fixes discovery-vs-evidence roles, U.S. scope, field-presence semantics, identifier-strength nonclaims, normalization boundaries, conflicts/abstention, provenance, rate/access constraints and deterministic fixture requirements.

### EEA

`EEA-EVIDENCE-CONTRACT-V2.md` fixes regulatory type-approval/type/variant/version roles, registration-year nonclaims, external-identifier boundaries, normalization/conflict behavior, provenance/reuse constraints and deterministic fixture requirements.

No contract promotes a new `STRONG` namespace, changes year semantics, weakens `REVIEW`, or converts missing data into inferred facts.

## #126 implementation

The bounded NHTSA and EEA adapters are prepared on the stacked branch. They preserve raw/source-native semantics, use exact content-addressed evidence, fail closed on malformed/unsupported responses, and do not promote regulatory/source-scoped fields into stronger retail identity semantics.

## #127 validation

The bounded multi-source harness is prepared. It retains explicit conflicts and REVIEW outcomes, measures source contribution/corroboration/provenance, and now rejects duplicate case IDs or malformed fixture identifiers before measurement so corpus counts cannot be inflated silently.

## #128 recurring acquisition

The recurring coordinator is prepared with contracted-source-only operation, existing host/HTTPS/robots/pacing authority, expected media/schema checks, content hash verification, idempotent unchanged checkpoints, bounded retry/degraded behavior, and fail-closed drift states. Source terms/license drift is extended separately by #164/#165 without changing evidence or resolver policy.

## Decisions

- Existing source evidence is reused as long as its version/scope remains adequate for the decision.
- Transport availability, semantic coverage, identity strength, market scope, and reuse/access status are tracked separately.
- A field exposed by a source is not automatically identity proof; source semantics govern its role.
- Missing or conflicting evidence stays explicit. Resolver/evidence thresholds are not tuned merely to improve coverage.
- A source with authoritative semantics but unavailable/contractual access is not disguised as an implementable adapter.

## Validation / blockers

Issue #112 still prevents normal GitHub-hosted execution evidence from being assumed: observed hosted jobs terminate before executing workflow steps (`steps=null`). Therefore implementation through #128 is reviewable/prepared but cannot be called repository-executable PASS or integrated by bypassing CI. No repeated rerun is justified while #112 is unchanged.
