# Podium 7 invariants

This is the canonical source for cross-cutting product invariants. Specialized contracts may add stricter local rules but must not contradict these.

## Identity and reconciliation

- False merges are more harmful than missed duplicates.
- Ambiguous identity evidence must remain reviewable; do not choose an arbitrary canonical target when multiple plausible matches remain.
- Stable canonical vehicle IDs must survive corrections; merges preserve historical IDs through redirects.
- Explicit contradictions are evaluated before positive external-ID evidence can produce a match.
- External identifiers retain namespace-specific strength; supporting/reference IDs do not become automatic identity proof.

Mechanical coverage: catalog identity policy tests, golden benchmarks, ingestion/review tests, and `scripts/check_harness.py` requiring the canonical contract set.

## Evidence and provenance

- Provenance is data, not logging decoration.
- A canonical/publication decision that claims evidence backing must reference persisted evidence.
- Source/evidence identifiers are immutable with respect to their recorded metadata; conflicting reuse is rejected.
- Intermediate candidate observations remain inspectable after a canonical value exists.
- `DecisionStatus` semantics must be preserved: hypotheses/unknowns are not presented as evidence-backed facts.

Mechanical coverage: evidence-policy tests, persistence tests, ingestion tests, review tests.

## Contracts and evolution

- Catalog Identity V2 evolves additively unless a proven product need requires a breaking change.
- Frozen consumer/JSON contracts do not silently change shape; incompatible changes require explicit contract versioning.
- Resolver-policy changes require benchmark/regression evidence; expected benchmark labels are product decisions, not generated from the resolver under test.

Mechanical coverage: JSON-contract/API tests, benchmark tests, schema-version checks.

## Architecture

- Acquisition, evidence, extraction/normalization, identity resolution, fusion/conflict, canonical persistence, review, and export remain logically observable responsibilities.
- Do not add infrastructure merely because it may be useful later; identify the present problem and why a simpler solution is insufficient.

Architecture rationale lives in [`ARCHITECTURE-PRINCIPLES.md`](ARCHITECTURE-PRINCIPLES.md) and [`SCIENTIFIC-FOUNDATION.md`](SCIENTIFIC-FOUNDATION.md).

## Release boundary

- Development may continue while license status is `UNKNOWN`.
- Public/package release is blocked until licensing is explicitly resolved by the owner and `scripts/check_release_readiness.py` passes.

Mechanical coverage: release-readiness tests/script.
