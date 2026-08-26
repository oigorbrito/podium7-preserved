# Current work

Status: active

Parent mission: #139 — production-scale evidence-backed catalog operation.

Current block: #144 — add explicit field-level source provenance to catalog benchmarks.

Documentation basis: #141 / `PRODUCTION-QUALITY-MEASUREMENT-V2.md` records that the current gold schema only binds `sourceIds` at case level, which prevents defensible source-contribution-by-dimension metrics without inventing provenance.

Acceptance for this block:

- add optional explicit `fieldSourceIds.left/right.<field>` attribution while keeping current benchmark files valid;
- fail closed on unknown sources/fields, absent-field attribution, duplicate IDs, malformed mappings and empty source lists;
- expose explicit attribution in loaded benchmark/report data;
- measure source contribution by dimension only from explicit attribution;
- separately measure attributed versus unattributed field coverage so missing metadata stays visible;
- do not infer provenance from case-level `sourceIds`, source prose, rationale or lexical semantics;
- do not change resolver/evidence/fusion/publication policy;
- do not retroactively backfill historical benchmark provenance without retained inspectable evidence.

Plan: `docs/exec-plans/active/FIELD-SOURCE-PROVENANCE-V1.md`.

Dependency stack: #140 → #141 → #144. Issue #112 remains external GitHub Actions debt, so executable PASS remains pending until code actually runs.
