# Current work

Status: active

Outcome: execute post-MVP mission #122 to expand Podium 7's evidence-backed automotive acquisition/enrichment layer using qualified multi-source evidence without changing existing evidence, fusion, ambiguity, identity-resolution, or publication principles.

Current block: #126 — implement the smallest bounded source adapters/enrichment slices authorized by the source-specific contracts, beginning with NHTSA vPIC VIN-backed evidence and EEA regulatory identity/support evidence.

Completed research/contract blocks on the active branch:

- #123: `docs/SOURCE-EVIDENCE-GAP-MATRIX-V1.md` reconstructs qualified-source coverage and measured evidence gaps without broad historical retesting.
- #124: `docs/SOURCE-QUALIFICATION-V1.md` plus the candidate ledger retain NHTSA/EEA as `ADAPT`, WSDenatran as `UNDECIDED` pending legitimate access, and SENATRAN fleet/CAT plus manufacturer artifacts as bounded reference evidence.
- #125: `docs/NHTSA-VPIC-EVIDENCE-CONTRACT-V1.md` and `docs/EEA-EVIDENCE-CONTRACT-V2.md` define source semantics, nonclaims, provenance and fail-closed behavior before coding.

Boundaries:

- existing evidence/source hierarchy, semantic conservatism, ambiguity handling, fusion/conflict and publication principles require explicit owner authorization to change;
- no Reddit/forums/blogs/opaque aggregators as canonical evidence and no stealth/proxy/CAPTCHA bypass;
- do not implement WSDenatran or another restricted source through an undocumented/bypass path;
- do not promote new `STRONG` identifier namespaces, conflate registration/manufacturing/model year, or infer missing source fields;
- bounded measurements must not be presented as production-wide completeness.

Acceptance for #126: approved sources produce deterministic source-backed candidates/evidence inside their documented scope, with complete provenance, explicit missing/unsupported/error paths, no identity-safety regression, and repository-required executable validation before integration.

Plan: `docs/exec-plans/active/POST-MVP-SOURCE-ACQUISITION-V1.md`.

Issue #112 (`Restore GitHub Actions hosted-runner execution`) remains infrastructure/operations debt. Do not add runner/infrastructure workarounds merely to bypass it.
