# Candidate evaluation ledger

This document is the durable record for external software and data-source evaluation in Podium 7. Its purpose is to preserve prior work, make uncertainty explicit, and prevent broad retesting when usable evidence already exists.

## Evidence policy

- Reconstruct before retesting. Search repository history, PRs, CI artifacts, prior handoffs/logs, and recorded commands/results before running a candidate again.
- Do not repeat a test merely because its conversational summary is missing.
- Retest only the smallest missing slice when one of these conditions applies: no recoverable result; result cannot be tied to an identifiable version/SHA; the original test was incomplete for the decision being made; or a later architecture/environment change specifically invalidates that result.
- Before any historical retest, tell the user what would be rerun, why the previous evidence is insufficient, and the expected scope. A single narrowly scoped retest may proceed after that notice as routine work. A broader batch, repeated suite, or any retest involving many cases must receive explicit user approval before execution.
- Preserve the distinction between `candidate considered` and `candidate validated`. A name in this ledger is not approval.
- Prefer primary/official documentation and reproducible evidence. For research claims, prefer peer-reviewed publications or established laboratory/benchmark work. Community/social discussion is not primary decision evidence.
- New evaluations must record enough context to avoid another reconstruction: candidate/repository, version or SHA, license status, capability under test, command/parameters, environment, result, interpretation, reuse decision, and evidence location.

## Status vocabulary

- `RECOVERED_SUFFICIENT` — evidence is adequate for the decision; do not repeat without a new reason.
- `RECOVERED_INCOMPLETE` — candidate/intent is known, but one or more decision-critical test fields are missing.
- `RESULT_ENV_UNCERTAIN` — a result is known, but exact version/environment/parameters are not yet recovered.
- `NO_EVIDENCE` — no usable prior evidence was recovered after searching durable/project artifacts.
- `OBSOLETE_BY_ARCHITECTURE` — a historical test no longer answers a current product question; do not rerun automatically.
- `ARCHIVED_UNRECOVERABLE` — exact historical execution detail was not recovered after the available durable evidence was reconciled, and no current decision depends on reconstructing it. If the capability becomes active again, evaluate the then-current candidate/version rather than rerunning an old battery merely to fill history.

## Confirmed historical research corpus — `RECOVERED_SUFFICIENT`

The project owner confirmed that the following works were part of the earlier research/testing discussion. The original scientific handoff preserves their decision-relevant benchmark measurements and project interpretations, and the primary publication pages were rechecked on 2026-08-22. Exact versions/venues and measured claims are now recorded in `SCIENTIFIC-FOUNDATION.md`.

| Work / benchmark / standard | Recovered role | Reconstruction status |
|---|---|---|
| SODIUM / SODIUM-Bench | agentic data integration / benchmark evidence | `RECOVERED_SUFFICIENT` |
| WebLists / BardeenAgent | repeatable web extraction / agent-to-program evidence | `RECOVERED_SUFFICIENT` |
| WideSearch | broad web collection / agent benchmark evidence | `RECOVERED_SUFFICIENT` |
| WANDR | web data retrieval / precision-recall-completeness evidence | `RECOVERED_SUFFICIENT` |
| WebDS | web data-science task benchmark evidence | `RECOVERED_SUFFICIENT` |
| MaDI-Bench | end-to-end data integration benchmark evidence | `RECOVERED_SUFFICIENT` |
| Automatic End-to-End Data Integration using LLMs | LLM-configured deterministic integration pipeline evidence | `RECOVERED_SUFFICIENT` |
| KnowledgeNet | knowledge-base population benchmark evidence | `RECOVERED_SUFFICIENT` |
| ComEM | entity matching benchmark evidence | `RECOVERED_SUFFICIENT` |
| ALER | active-learning entity-resolution evidence | `RECOVERED_SUFFICIENT` |
| PARSE | structured extraction / schema optimization evidence | `RECOVERED_SUFFICIENT` |
| DTBench | document-to-table extraction benchmark evidence | `RECOVERED_SUFFICIENT` |
| W3C PROV / PROV-O | provenance model / normative standard | `RECOVERED_SUFFICIENT` |

This reconstruction verifies what those references support. It does not convert their published numbers into Podium 7 local benchmark results.

## Historical software candidates — current decision closed

The historical handoffs name the following external software candidates, but the original per-candidate commands, exact tested versions and final donor-map decisions were not recovered from the available Git history, PRs, CI evidence or handoffs.

That missing history is **not an active product blocker**. The current repository has no runtime dependencies in `pyproject.toml`, and the capabilities these candidates were meant to explore are now represented by repository-native deterministic components and tests: repeatable web extraction, document extraction, validated AI-discovery artifacts, and conservative entity resolution. No current architecture decision depends on selecting one of these packages.

| Candidate | Historical evaluation area | Current reconstruction status | Current action |
|---|---|---|---|
| Crawl4AI | web acquisition/extraction | `OBSOLETE_BY_ARCHITECTURE` | no historical retest; re-evaluate only if a new crawler capability requires it |
| Stagehand | web/browser automation | `OBSOLETE_BY_ARCHITECTURE` | no historical retest; re-evaluate only if browser automation becomes required |
| Browser Use | browser automation | `OBSOLETE_BY_ARCHITECTURE` | no historical retest; current research already shows navigation benchmarks are insufficient for Podium 7 acceptance |
| Firecrawl | web acquisition/extraction | `OBSOLETE_BY_ARCHITECTURE` | no historical retest; re-evaluate only for a new active capability |
| ScrapeGraphAI | web extraction | `OBSOLETE_BY_ARCHITECTURE` | no historical retest; current repeatable extractor does not depend on it |
| Docling | document extraction | `OBSOLETE_BY_ARCHITECTURE` | no historical retest; current document extraction path is repository-native |
| Splink | entity resolution | `OBSOLETE_BY_ARCHITECTURE` | no historical retest; current Catalog Identity resolver is repository-native and benchmarked separately |

The unrecovered exact historical execution records are retained conceptually as `ARCHIVED_UNRECOVERABLE`; they must not be reverse-engineered into invented PASS/FAIL or ADOPT/REJECT decisions.

## Automotive data/source candidates

One source-selection decision is fully recoverable because it became executable repository evidence.

| Candidate/source family | Status | Recovered evidence / disposition |
|---|---|---|
| `vehicle-makes-models` | `RECOVERED_SUFFICIENT` | selected for first real structured ingestion; upstream `gor3a/vehicle-makes-models`, `data/json/artega.json`, source blob `560e795a8a0a9e97d20b7b201b3537962c7d6824`, acquired 2026-08-19; upstream data license recorded as ODbL v1.0; pinned snapshot and attribution are in `data/raw/vehicle-makes-models/` |
| `car-data-specifications` | `ARCHIVED_UNRECOVERABLE` | historical candidate details not recovered; no active selection decision depends on it |
| `automobile-models-and-specs` | `ARCHIVED_UNRECOVERABLE` | historical candidate details not recovered; no active selection decision depends on it |
| `open-vehicle-db` | `ARCHIVED_UNRECOVERABLE` | historical candidate details not recovered; no active selection decision depends on it |
| `vehiclesdb` | `ARCHIVED_UNRECOVERABLE` | historical candidate details not recovered; no active selection decision depends on it |
| FIPE data | `ARCHIVED_UNRECOVERABLE` for the historical source-comparison run | later Catalog Identity semantics treat FIPE identifiers separately; historical source-evaluation commands are not required for the current resolver |
| EVDB | `ARCHIVED_UNRECOVERABLE` | historical candidate details not recovered; evaluate current source/terms only if selected for a future ingestion slice |
| vehicle-specification APIs | `ARCHIVED_UNRECOVERABLE` | original providers/versions were not recovered; future use requires a fresh provider/terms decision |
| NHTSA/vPIC-derived data | `ARCHIVED_UNRECOVERABLE` | historical exact source/version not recovered; future use requires a current source-specific evaluation |

## Recovered partial results and their current disposition

- **Autoevolution:** the historical handoff records a validated snapshot/source and a failed live-download attempt. The current repository resolves the decision-relevant part by pinning evidence and using deterministic extraction over a known Autoevolution-derived Artega GT snapshot. `REPEATABLE-WEB-EXTRACTION-V1.md` records required fields, repeated-run equality, normalization and changed-structure failure behavior. General live Autoevolution acquisition remains unclaimed, but it is not required by the current architecture.
- **Ford Mustang Dark Horse:** the recovered artifact was TXT, not PDF. The current document-extraction work unit is deliberately format-agnostic at the evidence boundary and preserves the factual snapshot; no PDF-specific claim is required.

## Required evaluation record for future candidates

For every new or repeated external-candidate evaluation, append a row or linked record containing:

| Field | Required content |
|---|---|
| Capability | What product capability is being evaluated |
| Candidate | Repository/service/source name and URL or durable identifier |
| Version | Commit SHA, tag, release, API version, or snapshot timestamp |
| License/terms | SPDX/license/terms status relevant to intended use |
| Hypothesis | What the test is intended to establish |
| Parameters | Commands, fixtures, inputs, flags, thresholds, and relevant configuration |
| Environment | Runtime/OS/dependencies needed to interpret the result |
| Result | PASS/FAIL/SKIP/partial plus measured output |
| Interpretation | What the result does and does not prove |
| Decision | `ADOPT`, `ADAPT`, `REFERENCE`, `REJECT`, or `UNDECIDED` |
| Evidence | Git path, commit, PR, CI artifact, benchmark, or durable external source |

## Reconstruction outcome

`SCIENTIFIC_CORPUS = RECOVERED_SUFFICIENT`

`PRIMARY_BENCHMARK_DETAILS = RECOVERED_SUFFICIENT`

`FIRST_SELECTED_STRUCTURED_SOURCE = RECOVERED_SUFFICIENT`

`HISTORICAL_SOFTWARE_TEST_LEDGER = ARCHIVED_UNRECOVERABLE / NOT CURRENTLY DECISION_CRITICAL`

`WHOLESALE_HISTORICAL_RETEST_REQUIRED = NO`

There is no remaining research-reconstruction blocker for current Podium 7 development. If a future work unit makes one of the archived candidates or sources decision-critical again, that work unit must evaluate the current version/source with a narrowly scoped, durably recorded test rather than replaying the old comparison battery.
