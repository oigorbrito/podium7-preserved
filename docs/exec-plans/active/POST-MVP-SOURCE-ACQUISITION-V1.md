# Post-MVP source acquisition execution plan V1

Status: utility/design review complete through #128; stacked synchronization + executable validation pending
Parent mission: #122
Current block: review hardening completed on #130/#131/#132; descendants must be synchronized before validation

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

## Utility dispositions

- #129 / #123–#125: `INTEGRATE_AFTER_REPOSITORY_VALIDATION` — establishes measured gaps, qualifies sources, and freezes NHTSA/EEA semantics before executable adapters. This is the decision basis for later code, not a coverage claim.
- #130 / #126: `INTEGRATE_AFTER_SYNC_AND_VALIDATION` — converts qualified NHTSA/EEA source evidence into `RawEvidence`/`CandidateFact` without semantic promotion. Utility review additionally requires EEA content refs to retain a real snapshot location and rejects duplicate source record IDs.
- #131 / #127: `INTEGRATE_AFTER_SYNC_AND_VALIDATION` — measures corroboration/conflict/abstention and candidate-to-fusion provenance on the unchanged fusion model. REVIEW cases without candidates are provenance `N/A`, not vacuously complete.
- #132 / #128: `INTEGRATE_AFTER_SYNC_AND_VALIDATION` — provides bounded recurring-source authorization, drift/idempotency/retry/degraded behavior. A later denied authorization now invalidates any earlier one-shot token for the source.

These utility dispositions establish purpose only. They are not executable PASS and do not authorize out-of-order integration.

## Execution sequence

1. #123 — reconstruct current source baseline and produce `SOURCE-EVIDENCE-GAP-MATRIX-V1.md`. Prepared; validation/integration pending.
2. #124 — qualify only the smallest source set needed for measured gaps. Prepared.
3. #125 — define source-specific semantic/provenance contracts before coding adapters. Prepared for NHTSA vPIC and EEA; restricted WSDenatran intentionally deferred.
4. #126 — bounded source adapters. Prepared and review-hardened on PR #130.
5. #127 — bounded multi-source validation. Prepared and review-hardened on PR #131.
6. #128 — recurring acquisition. Prepared and review-hardened on PR #132.

## Synchronization state

The stack is currently **not a single validated ancestry**. During the 2026-08-27 utility review:

- #130 advanced with stricter EEA raw-snapshot and duplicate-record validation;
- #131 advanced with non-vacuous provenance-completeness semantics and duplicate-candidate protection;
- #132 advanced with stale-authorization invalidation and runtime contract hardening.

Because #131/#132 were originally branched from earlier upstream heads, downstream PRs must be synchronized/reconstructed in dependency order before final validation. Do not claim that the latest #132 head already contains the new #130/#131 fixes merely because the logical stack order is documented.

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

The bounded NHTSA and EEA adapters preserve raw/source-native semantics, exact content-addressed evidence, and fail-closed source semantics. Utility review tightened EEA provenance so a matching digest without a retained snapshot location is insufficient, and duplicate EEA source record IDs fail before duplicate facts can be emitted.

## #127 validation

The bounded multi-source harness retains explicit conflicts and REVIEW outcomes and measures source contribution/corroboration/provenance. Provenance completeness is now scoped only to cases with actual candidate facts. Empty-evidence REVIEW cases remain reviewable but are `N/A` for candidate-to-fusion provenance completeness.

## #128 recurring acquisition

The recurring coordinator uses contracted-source-only operation, existing host/HTTPS/robots/pacing authority, expected media/schema checks, content-hash verification, idempotent unchanged checkpoints, bounded retry/degraded behavior and fail-closed drift states. One-shot authorization is consumed by success/failure and every new authorization attempt invalidates any prior pending token before evaluation, so a denied later attempt cannot leave stale permission reusable.

Source terms/license drift remains a separate incremental follow-up in #164/#165.

## Decisions

- Existing source evidence is reused as long as its version/scope remains adequate for the decision.
- Transport availability, semantic coverage, identity strength, market scope, and reuse/access status are tracked separately.
- A field exposed by a source is not automatically identity proof; source semantics govern its role.
- Missing or conflicting evidence stays explicit. Resolver/evidence thresholds are not tuned merely to improve coverage.
- A source with authoritative semantics but unavailable/contractual access is not disguised as an implementable adapter.

## Validation / blockers

Issue #112 still prevents normal GitHub-hosted execution evidence from being assumed: observed hosted jobs terminate before executing workflow steps (`steps=null`). Therefore the reviewed implementation cannot be called repository-executable PASS or integrated by bypassing CI. No repeated rerun is justified while #112 is unchanged.

After synchronization, validate and integrate strictly in dependency order #129 → #130 → #131 → #132 using the repository-required harness/focused/sequential/CI path and squash merge.
