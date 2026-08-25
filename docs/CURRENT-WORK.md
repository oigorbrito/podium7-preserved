# Current work

Status: active

Outcome: execute post-MVP mission #122 to expand Podium 7's evidence-backed automotive acquisition/enrichment layer using qualified multi-source evidence without changing existing evidence, fusion, ambiguity, identity-resolution, or publication principles.

Current block: #125 — define source-specific semantic and provenance contracts for the already-qualified implementable sources before any new adapter code is written.

Completed research blocks on the active branch:

- #123 reconstructed the existing source baseline and produced `docs/SOURCE-EVIDENCE-GAP-MATRIX-V1.md` without broad historical retesting.
- #124 produced `docs/SOURCE-QUALIFICATION-V1.md` and updated the candidate ledger: NHTSA vPIC and EEA remain `ADAPT`; SENATRAN WSDenatran is `UNDECIDED` pending legitimate authorization/contract access; SENATRAN fleet and CAT/SISCAT remain `REFERENCE`; manufacturer artifacts remain case-bound primary evidence rather than a generic source family.

Boundaries:

- existing evidence/source hierarchy, semantic conservatism, ambiguity handling, fusion/conflict and publication principles require explicit owner authorization to change;
- reconstruct durable source evidence before retesting;
- no Reddit/forums/blogs/opaque aggregators as canonical evidence and no stealth/proxy/CAPTCHA bypass;
- bounded measurements must not be presented as production-wide completeness;
- do not implement WSDenatran or another restricted source through an undocumented/bypass path.

Acceptance for #125: every selected implementable source has an explicit contract defining source/version locator, field semantics, strength/nonclaims, market/year scope, normalization boundaries, conflict/abstention behavior, provenance/raw-hash chain, access/reuse constraints and deterministic fixtures before adapter implementation starts.

Plan: `docs/exec-plans/active/POST-MVP-SOURCE-ACQUISITION-V1.md`.

Issue #112 (`Restore GitHub Actions hosted-runner execution`) remains infrastructure/operations debt. Do not add runner/infrastructure workarounds merely to bypass it.
