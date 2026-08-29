# Post-MVP source acquisition execution plan V1

Status: active
Parent mission: #122
Current block: #126

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

1. #123 — reconstruct current source baseline and produce `SOURCE-EVIDENCE-GAP-MATRIX-V1.md`. **PASS on branch; integration pending repository validation availability.**
2. #124 — qualify only the smallest current source set needed to address measured gaps. **PASS.**
3. #125 — define source-specific semantic/provenance contracts before coding adapters. **PASS for NHTSA vPIC and EEA; restricted WSDenatran remains intentionally deferred.**
4. #126 — implement bounded approved adapters with deterministic fail-closed behavior. **Current block.**
5. #127 — validate multi-source fusion, corroboration, conflicts, review load and provenance.
6. #128 — operationalize recurring acquisition safely, including drift/outage handling.

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

## #126 implementation order

1. Inspect the existing NHTSA discovery adapter/domain/evidence primitives and EEA source-family implementation before editing.
2. Prefer additive source-specific parsing/extraction over generic framework changes.
3. Implement the smallest deterministic NHTSA VIN-backed evidence slice justified by frozen inspected fixtures.
4. Implement only the smallest EEA regulatory identity/support enrichment needed to exercise the V2 contract; reuse existing EEA acquisition/parser code rather than duplicate it.
5. Preserve raw/source-native values and explicit unsupported/missing-field issues.
6. Run required harness/focused/sequential validation before integration when executable validation is available.

## Decisions

- Existing source evidence is reused as long as its version/scope remains adequate for the decision.
- Transport availability, semantic coverage, identity strength, market scope, and reuse/access status are tracked separately.
- A field exposed by a source is not automatically identity proof; source semantics govern its role.
- Missing or conflicting evidence stays explicit. Resolver/evidence thresholds are not tuned merely to improve coverage.
- A source with authoritative semantics but unavailable/contractual access is not disguised as an implementable adapter.

## Validation / blockers

The work through #125 is documentation/research/contract-only and does not alter executable behavior. Issue #112 still prevents normal GitHub-hosted execution evidence from being assumed. For #126 code changes, do not claim PASS without the repository-required executable validation path; if execution remains unavailable, complete reviewable implementation as far as possible and record the validation blocker rather than bypassing it.
