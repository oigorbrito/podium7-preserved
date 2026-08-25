# Current work

Status: active

Outcome: execute post-MVP mission #122 to expand Podium 7's evidence-backed automotive acquisition/enrichment layer using qualified multi-source evidence without changing existing evidence, fusion, ambiguity, identity-resolution, or publication principles.

Current integration scope: #123–#125 — source baseline/gap matrix, targeted primary-source qualification, and source-specific NHTSA/EEA semantic/provenance contracts. Executable adapter work belongs to #126 on a separate branch/PR.

Completed research/contract blocks on this branch:

- #123: `docs/SOURCE-EVIDENCE-GAP-MATRIX-V1.md` reconstructs qualified-source coverage and measured evidence gaps without broad historical retesting.
- #124: `docs/SOURCE-QUALIFICATION-V1.md` plus the candidate ledger retain NHTSA/EEA as `ADAPT`, WSDenatran as `UNDECIDED` pending legitimate access, and SENATRAN fleet/CAT plus manufacturer artifacts as bounded reference evidence.
- #125: `docs/NHTSA-VPIC-EVIDENCE-CONTRACT-V1.md` and `docs/EEA-EVIDENCE-CONTRACT-V2.md` define source semantics, nonclaims, provenance and fail-closed behavior before coding.

Next executable block: #126 — implement the smallest bounded source adapters/enrichment slices authorized by those contracts, beginning with NHTSA vPIC VIN-backed evidence and EEA regulatory identity/support evidence.

Boundaries:

- existing evidence/source hierarchy, semantic conservatism, ambiguity handling, fusion/conflict and publication principles require explicit owner authorization to change;
- no Reddit/forums/blogs/opaque aggregators as canonical evidence and no stealth/proxy/CAPTCHA bypass;
- do not implement WSDenatran or another restricted source through an undocumented/bypass path;
- do not promote new `STRONG` identifier namespaces, conflate registration/manufacturing/model year, or infer missing source fields;
- bounded measurements must not be presented as production-wide completeness.

Acceptance for this integration scope: durable gap/qualification/contract artifacts are internally consistent, indexed, preserve the existing principles, and are validated under the repository workflow. #126 has separate executable acceptance requiring deterministic fixtures/tests and repository-required execution evidence.

Plan: `docs/exec-plans/active/POST-MVP-SOURCE-ACQUISITION-V1.md`.

Issue #112 (`Restore GitHub Actions hosted-runner execution`) remains infrastructure/operations debt. Do not add runner/infrastructure workarounds merely to bypass it.
