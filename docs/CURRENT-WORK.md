# Current work

Status: active

Parent mission: #139 — production-scale evidence-backed catalog operation.

Current block: #141 — measure identity quality and review load on the expanded source-backed operating corpus.

Dependency: #140 / Production Corpus Run V3 defines the 72-record / 36-case corpus. This block reuses the existing repository quality and operational measurement paths; it does not introduce new sources, regions, semantic rules or resolver changes.

Acceptance for this block:

- measure auto-match precision/recall, false merges, missed matches and ambiguous overcommit on the 36 identity cases;
- measure CREATED/MATCHED/REVIEW/failure distribution and durable review causes on the 72 operational observations;
- verify source/evidence locators and benchmark provenance remain complete;
- preserve fail-closed review semantics and all evidence/fusion/publication rules regardless of measured values;
- do not create follow-up source/region/semantic/resolver issues until executable results establish a concrete need;
- do not invent per-dimension source contribution: the current gold schema binds `sourceIds` at case level, not field level.

Plan: `docs/exec-plans/active/PRODUCTION-QUALITY-MEASUREMENT-V2.md`.

Issue #112 remains external GitHub Actions debt. Numerical results and PASS status remain pending until code actually executes.
