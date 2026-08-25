# Podium 7 Architecture Principles

## Decision classification

Every relevant architectural decision MUST be classified as one of:

- `EVIDENCE_BACKED`: directly supported by a paper, benchmark, standard, or primary documentation.
- `HYPOTHESIS`: plausible interpretation not yet proven for Podium 7.
- `LOCALLY_VERIFIED`: established by Podium 7 code, tests, or execution.
- `ENGINEERING_CHOICE`: implementation decision not uniquely determined by the scientific literature.
- `UNKNOWN`: insufficient evidence.

An `ENGINEERING_CHOICE` must never be presented as a scientific conclusion.

## Evidence-backed logical boundaries

The system is organized logically as:

`source input → acquisition → raw evidence → structured extraction → schema alignment → value normalization → entity resolution → fact candidates → data fusion/conflict resolution → canonical automotive knowledge → export`

Provenance, confidence, validation, human review, and observability are cross-cutting concerns.

The following logical separations are `EVIDENCE_BACKED` by the handoff corpus:

- acquisition, extraction, normalization, entity resolution, and fusion are independently observable stages;
- schema mapping, normalization, entity matching, and conflict resolution are distinct integration problems;
- entity resolution is not equivalent to string equality;
- conflict resolution must not silently degrade to last-write-wins;
- provenance is part of the information needed to audit a fact;
- repeated stable extraction should prefer reusable deterministic artifacts over repeated full interpretation.

Logical separation does not imply separate services or processes.

## Preservation rule

`EVIDENCE_BACKED` direction:

`SOURCE → RAW EVIDENCE → EXTRACTED CANDIDATE → NORMALIZED CANDIDATE → RESOLUTION DECISION → CANONICAL FACT`

Intermediate audit information must not be destroyed merely because a canonical value has been produced.

## AI role

`EVIDENCE_BACKED` direction from WebLists and Steiner & Bizer (2026): AI may discover or configure reusable artifacts while deterministic components perform stable repetition.

`HYPOTHESIS`: this pattern will reduce cost and improve repeatability for Podium 7 automotive sources. It remains to be locally measured.

## Minimality rule

Before adding infrastructure such as distributed services, queues, caches, vector databases, knowledge graphs, or agent hierarchies, the implementation must identify:

1. the current problem that requires it;
2. local evidence that the problem exists;
3. why a simpler solution is insufficient.

Without those answers: do not add it.

Non-trivial infrastructure experimentation, adoption, adaptation, or construction is additionally governed by [`ADR-0001-MARKET-FIRST-INFRASTRUCTURE.md`](ADR-0001-MARKET-FIRST-INFRASTRUCTURE.md). That ADR is the canonical record for the requirement to evaluate mature alternatives first and document the resulting adopt/adapt/build decision.

## Work Unit 1 engineering choices

- Python 3 standard library for the first domain model: `ENGINEERING_CHOICE`.
- In-memory immutable dataclasses for domain representation: `ENGINEERING_CHOICE`.
- `unittest` for initial domain tests: `ENGINEERING_CHOICE`.
- No database, crawler, browser agent, LLM orchestration, PDF extraction, scheduler, UI, or distributed architecture: required by the work-unit scope.

These choices are intentionally replaceable and are not scientific conclusions.
