# Current work

Status: none

## Current repository state

The bounded post-MVP source-acquisition mission is complete for its current scope. Source qualification/contracts, executable NHTSA/EEA adapters, multi-source validation/conflict observability, recurring-source controls, review-provenance retention, provenance eligibility, provenance-gated catalog coverage measurement, fail-closed operational source attribution, bounded PDF acquisition, and source-terms drift checks are integrated.

Recent integration evidence includes:

- #147 — explicit multi-source conflict disposition;
- #167 — explicit operational provenance eligibility, retaining blocked record sides rather than inferring attribution;
- #171 — deterministic extraction-quality benchmark contract with evidence-bound Inmetro PBEV gold;
- #174 — bounded exact-locator PDF acquisition completed; the Inmetro PBEV gold carries a bound raw SHA-256;
- #178 — prospective explicit review-side provenance retention;
- #196 — catalog identity-field coverage recomputed only on provenance-eligible retained records; historical #176 percentages are superseded as current readiness evidence;
- #142 — operational replay fails closed on ambiguous source attribution and downstream operational/enrichment/review consumers use provenance-eligible replay;
- #165 — fail-closed source terms/reuse-artifact drift gate;
- #207 — bounded ER blocker probes executed on retained automotive corpora; `same-make` shows no measured reduction and `same-make-model` fails blocking-recall/ambiguous-overcommit safety gates, so `CURRENT_BETTER` applies to those probes without claiming global optimality;
- #208 — controlled heterogeneity baseline recorded: representation variation can reduce recall while a regulatory→retail semantic misprojection is a safety regression;
- #213 — bounded test-only transmission-representation candidate measured and integrated as `COMPLEMENTARY`, with no production normalizer authorized;
- #215 — extraction benchmark corrected to fail closed because the bound Inmetro digest is known but exact remote snapshot bytes are not currently reproducibly retrievable.

`docs/TECH-DEBT.md` records acquisition and source-family generalization as `CLOSED / CURRENT BOUNDED PROCESS COMPLETE`.

## Active evaluation work

Two evaluation plans remain active because their acceptance conditions are not yet satisfied:

1. `docs/exec-plans/active/EXTRACTBENCH-EVALUATION-168.md`
   - the benchmark/evidence contract is integrated;
   - the selected first bounded comparison candidate is Camelot `lattice`, but no candidate result is claimed;
   - exact benchmark snapshot bytes are currently `REMOTE_BYTES_UNRESOLVED` under #214, so current-versus-candidate extraction execution remains blocked until a fresh runner can retrieve bytes that verify to the bound SHA;
   - `EXTRACTOR_COMPARISON = EXTRACTOR_COMPARISON_PENDING`;
   - no extractor is declared superior and no replacement is authorized.

2. `docs/exec-plans/active/HETEROGENEITY-STRESS-170.md`
   - the heterogeneity measurement contract and current-resolver controlled baseline are integrated;
   - the bounded transmission-representation probe from #213 is integrated with `HETEROGENEITY_TRANSMISSION_REPRESENTATION_CANDIDATE = COMPLEMENTARY`;
   - `HETEROGENEITY_MITIGATION_COMPARISON = PENDING_BROADER_CANDIDATE_EVIDENCE`;
   - no production normalization, mapping, blocking or matching replacement is authorized.

The ER blocking/matcher evaluation #169 is closed/completed for its bounded probes. `ER_BLOCKER_MATCHER_COMPARISON = CURRENT_BETTER` applies only to the measured retain-all / same-make / same-make-model comparison; a future broader ER comparison requires a new concrete candidate and the same safety gates rather than treating #169 as active work.

## Current evidence boundary

Operational measurements and consumer-readiness evidence derived from the retained catalog corpus are bounded to record sides with defensible provenance. Record sides blocked by missing or ambiguous source attribution remain explicit and are excluded from replay/readiness evidence rather than silently assigned a source.

The current provenance-safe operational slice is not evidence of production-wide completeness. Historical full-corpus counts, review totals, field percentages, or thresholds that depended on positional source attribution are not current acceptance criteria.

Likewise, bounded ER and heterogeneity measurements are not production-scale prevalence or candidate-universe claims. `candidateReductionRatio`, latency and peak-memory comparisons remain unavailable until a real candidate-universe experiment supplies those observations.

The extraction benchmark's bound SHA is not equivalent to remotely retrievable benchmark bytes. Until #214 supplies a durable locator whose retrieved bytes verify to the bound digest, mutable upstream reacquisition must not be substituted for the bound snapshot.

## Next valid triggers

A new implementation slice requires new decision-relevant evidence. Valid triggers include:

- recovery of the exact Inmetro benchmark snapshot bytes plus digest verification and specific reuse confirmation, allowing #214 to provide a durable snapshot locator and #168 to execute the current-versus-candidate extraction comparison;
- a concrete blocker/matcher candidate beyond the completed #169 bounded probes, compared without reducing blocking recall or increasing false merges/ambiguous overcommit;
- broader retained/source-backed paired identity cases that can evaluate a concrete heterogeneity mitigation without increasing false merges or ambiguous overcommit;
- a new measured production/source/evidence gap that justifies reopening acquisition or enrichment work;
- an explicit owner decision where an existing boundary requires owner authorization.

Absent one of those triggers, the correct state is a clean checkpoint rather than speculative feature work.

## Boundaries

- preserve evidence/source hierarchy, semantic conservatism, ambiguity handling, fusion/conflict, identity-resolution and publication principles;
- no stealth/proxy/CAPTCHA bypass or undocumented restricted-source path;
- do not infer missing source fields or conflate manufacture/model year;
- EEA regulatory type/variant/version remains regulatory evidence, not retail-trim identity proof;
- bounded measurements are not production-wide completeness claims;
- source terms/hash equality is drift evidence only and is not legal interpretation or proof of permission.
