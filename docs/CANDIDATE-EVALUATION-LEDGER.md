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

## Confirmed historical research corpus

During the 2026-08-22 reconstruction, the project owner confirmed that all of the following names had been cited and used in the earlier Podium 7 research/testing discussion. This confirmation establishes **historical inclusion in the research corpus only**. It does not, by itself, revalidate any reported metric, reproduce an experiment, or establish that Podium 7 adopted a particular architecture because of that work.

| Work / benchmark / standard | Historical role recovered |
|---|---|
| SODIUM / SODIUM-Bench | agentic data integration / benchmark evidence |
| WebLists / BardeenAgent | repeatable web extraction / agent-to-program evidence |
| WideSearch | broad web collection / agent benchmark evidence |
| WANDR | web data retrieval / precision-recall-completeness evidence |
| WebDS | web data-science task benchmark evidence |
| MaDI-Bench | end-to-end data integration benchmark evidence |
| Automatic End-to-End Data Integration using LLMs | LLM-configured deterministic integration pipeline evidence |
| KnowledgeNet | knowledge-base population benchmark evidence |
| ComEM | entity matching benchmark evidence |
| ALER | active-learning entity-resolution evidence |
| PARSE | structured extraction / schema optimization evidence |
| DTBench | document-to-table extraction benchmark evidence |
| W3C PROV / PROV-O | provenance model / normative standard |

The historical handoff also states that practical experiments and measured benchmarks were weighted more heavily for operational engineering choices than purely theoretical work when both addressed the same question. Exact paper versions, links, measured values, experimental conditions, and the precise decision each source supported still need durable reconstruction before being quoted as project-native evidence.

## Recovered software candidate inventory

The following names were recovered from historical project handoffs as candidates that had been considered. No repository-native evidence has yet been recovered that establishes an `ADOPT`, `ADAPT`, `REFERENCE`, or `REJECT` decision for these entries.

| Candidate | Intended evaluation area | Current status | Missing evidence before any reuse decision |
|---|---|---|---|
| Crawl4AI | web acquisition/extraction | `RECOVERED_INCOMPLETE` | exact repo/version, commands, result, reuse decision |
| Stagehand | web/browser automation | `RECOVERED_INCOMPLETE` | exact repo/version, commands, result, reuse decision |
| Browser Use | browser automation | `RECOVERED_INCOMPLETE` | exact repo/version, commands, result, reuse decision |
| Firecrawl | web acquisition/extraction | `RECOVERED_INCOMPLETE` | exact repo/version, commands, result, reuse decision |
| ScrapeGraphAI | web extraction | `RECOVERED_INCOMPLETE` | exact repo/version, commands, result, reuse decision |
| Docling | document extraction | `RECOVERED_INCOMPLETE` | exact repo/version, commands, result, reuse decision |
| Splink | entity resolution | `RECOVERED_INCOMPLETE` | exact repo/version, commands, result, reuse decision |

## Recovered automotive data/source candidates

These source families were also recovered as having been considered. Their presence here does not establish authority, completeness, licensing suitability, or selection.

| Candidate/source family | Current status | Missing evidence |
|---|---|---|
| `vehicle-makes-models` | `RECOVERED_INCOMPLETE` | exact repository/version, license, tests, decision |
| `car-data-specifications` | `RECOVERED_INCOMPLETE` | exact repository/version, license, tests, decision |
| `automobile-models-and-specs` | `RECOVERED_INCOMPLETE` | exact repository/version, license, tests, decision |
| `open-vehicle-db` | `RECOVERED_INCOMPLETE` | exact repository/version, license, tests, decision |
| `vehiclesdb` | `RECOVERED_INCOMPLETE` | exact repository/version, license, tests, decision |
| FIPE data | `RECOVERED_INCOMPLETE` | original candidate-evaluation commands/decision; later product semantics are documented separately |
| EVDB | `RECOVERED_INCOMPLETE` | exact source/version, license/terms, tests, decision |
| vehicle-specification APIs | `RECOVERED_INCOMPLETE` | exact providers/versions, terms, tests, decision |
| NHTSA/vPIC-derived data | `RECOVERED_INCOMPLETE` | exact source/version, tests, decision |

## Recovered partial results

These facts were present in historical project handoffs and should not be silently reinterpreted:

- Autoevolution: a snapshot/source was reported as externally validated; a live download attempt had failed. Exact version/parameters remain unrecovered, so this is `RESULT_ENV_UNCERTAIN` rather than a general PASS/FAIL for Autoevolution.
- Ford Mustang Dark Horse: the recorded source artifact was TXT, not PDF.

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

## Current gap

The candidate names, evaluation methodology, and historical research corpus have now been recovered at the inventory level, but the original per-candidate execution ledger — exact versions, commands, outputs, and final reuse decisions — has not yet been found in the repository. Exact source links, paper versions, measured values, and experiment conditions for the confirmed research corpus also remain to be reconstructed before they are treated as durable project evidence. These gaps are documentation/reconstruction work, not permission to rerun the entire historical battery.
