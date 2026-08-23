# Podium 7 documentation index

`docs/` is the repository system of record. This index is the progressive-disclosure entry point after `AGENTS.md`.

## Always-read operating context

- [`CURRENT-STATE.md`](CURRENT-STATE.md) — current factual repository/product state; short, no history dump.
- [`CURRENT-WORK.md`](CURRENT-WORK.md) — the active outcome, boundaries, acceptance criteria, and blockers only.
- [`DEVELOPMENT-WORKFLOW.md`](DEVELOPMENT-WORKFLOW.md) — the single canonical source for autonomy, approvals, Git/PR/CI, validation, self-review, done, and stopping rules.
- [`INVARIANTS.md`](INVARIANTS.md) — product and evidence invariants that every change must preserve.
- [`TECH-DEBT.md`](TECH-DEBT.md) — durable known debt and external blockers.
- [`CANDIDATE-EVALUATION-LEDGER.md`](CANDIDATE-EVALUATION-LEDGER.md) — recovered external candidate/source evaluation evidence, gaps, and retest policy.
- [`exec-plans/README.md`](exec-plans/README.md) — when and how to version execution plans.

## Architecture and scientific foundation

- [`ARCHITECTURE-PRINCIPLES.md`](ARCHITECTURE-PRINCIPLES.md) — architecture principles and decision classification.
- [`SCIENTIFIC-FOUNDATION.md`](SCIENTIFIC-FOUNDATION.md) — scientific baseline and canonical research references.
- [`PERSISTENCE-AND-EVIDENCE-STORE.md`](PERSISTENCE-AND-EVIDENCE-STORE.md) — persistence/provenance design.
- [`ENTITY-RESOLUTION-V1.md`](ENTITY-RESOLUTION-V1.md) — V1 entity-resolution design record.
- [`DATA-FUSION-AND-CONFLICTS-V1.md`](DATA-FUSION-AND-CONFLICTS-V1.md) — fusion/conflict design record.
- [`NORMALIZATION-V1.md`](NORMALIZATION-V1.md) — normalization design record.

## Catalog product contracts

- [`CATALOG-IDENTITY-V2.md`](CATALOG-IDENTITY-V2.md)
- [`CATALOG-EVIDENCE-POLICY-V2.md`](CATALOG-EVIDENCE-POLICY-V2.md)
- [`CATALOG-JSON-CONTRACT-V2.md`](CATALOG-JSON-CONTRACT-V2.md)
- [`CATALOG-CONSUMER-API-V2.md`](CATALOG-CONSUMER-API-V2.md)
- [`CATALOG-IDENTITY-BENCHMARK-V1.md`](CATALOG-IDENTITY-BENCHMARK-V1.md)
- [`CATALOG-YEAR-SEMANTICS-CHALLENGE-V1.md`](CATALOG-YEAR-SEMANTICS-CHALLENGE-V1.md)
- [`CATALOG-BATCH-INGESTION-V1.md`](CATALOG-BATCH-INGESTION-V1.md)
- [`BOM-PRATICHE-CONTRACT-V2.md`](BOM-PRATICHE-CONTRACT-V2.md)

## Acquisition, extraction, review, and export design records

- [`FIRST-REAL-STRUCTURED-INGESTION.md`](FIRST-REAL-STRUCTURED-INGESTION.md)
- [`DIRECT-HTTP-ACQUISITION-V1.md`](DIRECT-HTTP-ACQUISITION-V1.md) — bounded fail-closed direct HTTP transport and snapshot contract.
- [`PUBLIC-WEB-ACQUISITION-CHARACTERIZATION-V1.md`](PUBLIC-WEB-ACQUISITION-CHARACTERIZATION-V1.md) — one live operational compatibility measurement across the retained exact public source URLs.
- [`BROWSER-ACQUISITION-CHARACTERIZATION-V1.md`](BROWSER-ACQUISITION-CHARACTERIZATION-V1.md) — controlled Chromium measurement on the retained Autoevolution URLs refused by direct HTTP; browser fallback was not selected.
- [`REPEATABLE-WEB-EXTRACTION-V1.md`](REPEATABLE-WEB-EXTRACTION-V1.md)
- [`DOCUMENT-EXTRACTION-V1.md`](DOCUMENT-EXTRACTION-V1.md)
- [`SELECTIVE-REVIEW-V1.md`](SELECTIVE-REVIEW-V1.md)
- [`AUTONOMOUS-ENRICHMENT-LOOP-V1.md`](AUTONOMOUS-ENRICHMENT-LOOP-V1.md)
- [`AI-DISCOVERY-V1.md`](AI-DISCOVERY-V1.md)
- [`EXPORT-V1.md`](EXPORT-V1.md)
- [`END-TO-END-ACCEPTANCE-V1.md`](END-TO-END-ACCEPTANCE-V1.md)

## Reference and generated material

- [`references/OPENAI-CODEX-HARNESS.md`](references/OPENAI-CODEX-HARNESS.md) — normative external references used for this harness.
- [`generated/README.md`](generated/README.md) — policy for derived/generated repository facts.
- [`LICENSING-STATUS.md`](LICENSING-STATUS.md) — private/proprietary software status and the explicit gate for any future public-license decision.

Historical design records may describe the work unit in which they were created; they are not current-state trackers unless explicitly named above. Volatile facts come from `python scripts/project_facts.py`.
