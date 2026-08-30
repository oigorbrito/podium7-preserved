# Current work

Status: active

## Active mission

Issue #236 — `Post-MVP functional audit for production readiness` — is the current repository-wide implementation/readiness gate.

The audit reviews the integrated product path rather than issue closure alone: runtime/CLI, acquisition/network boundaries, evidence/provenance, normalization/extraction/resolution/fusion/review, SQLite persistence/transactions/reopen behavior, consumer/export/versioning contracts, deterministic replay/benchmarks, exception boundaries, dead/stale pathways, packaging/installability, supported runtime, and repository CI.

Concrete audit defects are fixed in focused follow-up PRs and require the normal exact-head GitHub Actions gate before squash merge. Evidence/resolver/provenance/fusion/ambiguity/publication rules must not be weakened to obtain a PASS.

## Current integrated baseline

The private technical MVP is complete. Subsequent post-MVP source acquisition, multi-source evidence controls, provenance-safe operational replay, identity-safety benchmarking, durable review/conflict behavior, quantitative-enrichment contract/baseline work, and bounded source-acquisition controls are substantially integrated.

Recent audit hardening includes:

- #237/#238 — bounded PDF acquisition moved to the validated-IP network binding path, closing the documented DNS validation-to-connect rebinding gap without changing source/evidence/publication semantics.

Hosted GitHub Actions is operational again and is the official merge validation gate. Historical #112 runner/account blockage must not be treated as current work.

## Remaining external-evidence/scientific gates

These remain open independently of the functional-code audit:

1. #214 — make the exact historical Inmetro PBEV benchmark PDF bytes reproducibly retrievable and SHA-verified. Mutable upstream reacquisition must not substitute for the bound historical digest.
2. #168 — execute the bounded PDF-to-structured current-versus-candidate extraction benchmark once the exact source-bound bytes required by #214 are available.
3. #232 — establish evidence-bound semantics for current PBEV quantitative columns before extending the public enrichment vocabulary or exposing those facts to BPT2.

These gates are not permission to infer missing source data, silently rebind evidence, or convert unavailable evidence into a code PASS.

## Current evidence boundary

Operational measurements and consumer-readiness evidence derived from the retained catalog corpus remain bounded to record sides with defensible provenance. Record sides blocked by missing or ambiguous source attribution remain explicit and excluded rather than silently assigned a source.

Bounded benchmark results are not production-wide completeness claims. Quantitative equality does not drive identity resolution. Manufacture year and model year remain distinct. Ambiguous identity remains `REVIEW`.

## Completion condition

#236 must record an explicit final disposition:

`POST_MVP_FUNCTIONAL_AUDIT = PASS | FAIL | PENDING_EXTERNAL_EVIDENCE`

A functional PASS means the implemented Podium behavior is operationally coherent and validated within documented contracts. It does not claim universal automotive-data completeness or waive #214/#168/#232 evidence requirements.

## Boundaries

- preserve evidence/source hierarchy, semantic conservatism, ambiguity handling, fusion/conflict, identity-resolution and publication principles;
- no stealth/proxy/CAPTCHA bypass or undocumented restricted-source path;
- do not infer missing source fields or conflate manufacture/model year;
- EEA regulatory type/variant/version remains regulatory evidence, not retail-trim identity proof;
- bounded measurements are not production-wide completeness claims;
- source terms/hash equality is drift evidence only and is not legal interpretation or proof of permission;
- before non-trivial infrastructure experimentation or construction, apply ADR-0001 and evaluate mature market alternatives first.
