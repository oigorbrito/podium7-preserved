# Candidate evaluation ledger

This document is the durable record for external software and data-source evaluation in Podium 7. Its purpose is to preserve prior work, make uncertainty explicit, and prevent broad retesting when usable evidence already exists.

## Evidence policy

- Reconstruct before retesting. Search repository history, PRs, CI artifacts, prior handoffs/logs, and recorded commands/results before running a candidate again.
- Do not repeat a test merely because its conversational summary is missing.
- Retest only the smallest missing slice when one of these conditions applies: no recoverable result; result cannot be tied to an identifiable version/SHA; the original test was incomplete for the decision being made; or a later architecture/environment change specifically invalidates that result.
- Preserve the distinction between `candidate considered` and `candidate validated`. A name in this ledger is not approval.
- Prefer primary/official documentation and reproducible evidence. For research claims, prefer peer-reviewed publications or established laboratory/benchmark work. Community/social discussion is not primary decision evidence.
- New evaluations must record enough context to avoid another reconstruction: candidate/repository, version or SHA, license status, capability under test, command/parameters, environment, result, interpretation, reuse decision, and evidence location.

## Status vocabulary

- `RECOVERED_SUFFICIENT` — evidence is adequate for the decision; do not repeat without a new reason.
- `RECOVERED_INCOMPLETE` — candidate/intent is known, but one or more decision-critical test fields are missing.
- `RESULT_ENV_UNCERTAIN` — a result is known, but exact version/environment/parameters are not yet recovered.
- `NO_EVIDENCE` — no usable prior evidence was recovered after searching durable/project artifacts.
- `OBSOLETE_BY_ARCHITECTURE` — a historical test no longer answers a current product question; do not rerun automatically.

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

The candidate names and evaluation methodology have been recovered, but the original per-candidate execution ledger — exact versions, commands, outputs, and final reuse decisions — has not yet been found in the repository. This gap is documentation/reconstruction work, not permission to rerun the entire historical battery.
