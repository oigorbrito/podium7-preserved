# Current work

Status: blocked

## Current disposition

The repository-wide post-MVP functional audit #236 completed its code/operational review with:

`POST_MVP_FUNCTIONAL_AUDIT = PENDING_EXTERNAL_EVIDENCE`

No known reproducible code/operational defect remains from the audited path. This is not a `100% functional post-MVP` claim because external evidence/scientific gates remain unresolved.

## Audit hardening integrated

The audit fixed concrete defects without weakening evidence, resolver, provenance, fusion, ambiguity or publication rules, including:

- bounded PDF acquisition now uses validated-IP socket binding;
- arbitrary HTTP snapshot CLI and public-web benchmark default transport use the bound network path;
- bound HTTP Host authority handles IPv6 and scheme-specific default ports correctly;
- domain JSON values must round-trip without silent Python-to-JSON coercion;
- unresolved/review conflicts cannot carry a selected candidate;
- live handoff/state/work documents and active checkout URLs reflect the current repository/CI state.

Repository CI remains the official gate and includes secret hygiene, harness validation, runtime health, package build/install, isolated tests on the configured current and minimum-supported runtimes, and validation artifacts where configured.

## Blocking external-evidence/scientific work

1. #214 — make the exact historical Inmetro PBEV benchmark PDF bytes reproducibly retrievable and SHA-verified. Mutable upstream reacquisition must not substitute for the bound historical digest.
2. #168 — execute the bounded PDF-to-structured benchmark after #214 provides the exact source-bound bytes.
3. #232 — establish evidence-bound semantics for current PBEV quantitative columns before extending the public enrichment vocabulary or exposing those facts to BPT2.

#214 is the direct blocker for #168. #232 remains an independent evidence-bound quantitative semantics track. Where one external dependency blocks progress, continue any independent evidence-scoped work that does not weaken source binding.

## Current evidence boundary

Operational measurements and consumer-readiness evidence derived from the retained catalog corpus remain bounded to record sides with defensible provenance. Record sides blocked by missing or ambiguous source attribution remain explicit and excluded rather than silently assigned a source.

Bounded benchmark results are not production-wide completeness claims. Quantitative equality does not drive identity resolution. Manufacture year and model year remain distinct. Ambiguous identity remains `REVIEW`.

## Boundaries

- preserve evidence/source hierarchy, semantic conservatism, ambiguity handling, fusion/conflict, identity-resolution and publication principles;
- no stealth/proxy/CAPTCHA bypass or undocumented restricted-source path;
- do not infer missing source fields or conflate manufacture/model year;
- EEA regulatory type/variant/version remains regulatory evidence, not retail-trim identity proof;
- bounded measurements are not production-wide completeness claims;
- source terms/hash equality is drift evidence only and is not legal interpretation or proof of permission;
- before non-trivial infrastructure experimentation or construction, apply ADR-0001 and evaluate mature market alternatives first.
