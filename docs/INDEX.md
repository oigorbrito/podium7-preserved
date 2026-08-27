# Podium 7 documentation index

`docs/` is the repository system of record. This index is the progressive-disclosure entry point after `AGENTS.md` and the compact resume handoff.

## Always-read operating context

- [`HANDOFF.md`](HANDOFF.md) — compact resume point for a new chat/session; refresh live repository state before acting.
- [`CURRENT-STATE.md`](CURRENT-STATE.md) — current factual repository/product state; short, no history dump.
- [`CURRENT-WORK.md`](CURRENT-WORK.md) — the active outcome, boundaries, acceptance criteria, and blockers only.
- [`DEVELOPMENT-WORKFLOW.md`](DEVELOPMENT-WORKFLOW.md) — the single canonical source for autonomy, approvals, Git/PR/CI, validation, self-review, done, and stopping rules.
- [`INVARIANTS.md`](INVARIANTS.md) — product and evidence invariants that every change must preserve.
- [`TECH-DEBT.md`](TECH-DEBT.md) — durable known debt and external blockers.
- [`CANDIDATE-EVALUATION-LEDGER.md`](CANDIDATE-EVALUATION-LEDGER.md) — recovered external candidate/source evaluation evidence, gaps, and retest policy.
- [`exec-plans/README.md`](exec-plans/README.md) — when and how to version execution plans.

## Architecture and scientific foundation

- [`ARCHITECTURE-PRINCIPLES.md`](ARCHITECTURE-PRINCIPLES.md) — architecture principles and decision classification.
- [`ADR-0001-MARKET-FIRST-INFRASTRUCTURE.md`](ADR-0001-MARKET-FIRST-INFRASTRUCTURE.md) — requires mature-market evaluation before non-trivial infrastructure experimentation or construction and documents adopt/adapt/build decisions.
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
- [`CATALOG-REVIEW-OPERATOR-V1.md`](CATALOG-REVIEW-OPERATOR-V1.md) — canonical private operator CLI, existing-database safety boundary, review context, and audited mutation contract.
- [`BOM-PRATICHE-CONTRACT-V2.md`](BOM-PRATICHE-CONTRACT-V2.md)

## Acquisition, extraction, review, export, and operational readiness

- [`FIRST-REAL-STRUCTURED-INGESTION.md`](FIRST-REAL-STRUCTURED-INGESTION.md)
- [`DIRECT-HTTP-ACQUISITION-V1.md`](DIRECT-HTTP-ACQUISITION-V1.md) — bounded fail-closed direct HTTP transport and snapshot contract.
- [`NETWORK-TARGET-BINDING-V1.md`](NETWORK-TARGET-BINDING-V1.md) — DNS-rebinding-resistant acquisition path that binds validated resolution to the actual socket connection while preserving hostname TLS verification.
- [`INMETRO-PBEV-DOCUMENT-PATH-V1.md`](INMETRO-PBEV-DOCUMENT-PATH-V1.md) — source-specific current PBEV PDF acquisition and ruled-table extraction path without widening global HTTP media policy.
- [`PRODUCTION-SOURCE-DISTRIBUTION-V1.md`](PRODUCTION-SOURCE-DISTRIBUTION-V1.md) — bounded regression gate for independently inspected source-family and regional diversity without a production-completeness claim.
- [`PRODUCTION-CORPUS-RUN-V2.md`](PRODUCTION-CORPUS-RUN-V2.md) — expanded source-backed replay through batch ingestion, identity resolution, evidence persistence and consumer reads.
- [`PRODUCTION-CORPUS-RUN-V3.md`](PRODUCTION-CORPUS-RUN-V3.md) — 72-record operating replay composed only from retained versioned source-backed gold sets, adding the selected year-semantics challenge without new source or policy scope.
- [`PRODUCTION-QUALITY-MEASUREMENT-V2.md`](PRODUCTION-QUALITY-MEASUREMENT-V2.md) — identity-safety, review-load and provenance measurement contract for the 72-record / 36-case V3 corpus; executable values remain pending while #112 blocks workflow steps.
- [`MEASUREMENT-ARTIFACT-V1.md`](MEASUREMENT-ARTIFACT-V1.md) — immutable measurement artifact contract for capture-only operational evidence.
- [`PRODUCTION-OPERATIONAL-MEASUREMENT-V1.md`](PRODUCTION-OPERATIONAL-MEASUREMENT-V1.md) — measured action distribution, review load and durable review causes for the expanded source-backed replay.
- [`PRODUCTION-OPERATIONAL-GAP-PRIORITY-V1.md`](PRODUCTION-OPERATIONAL-GAP-PRIORITY-V1.md) — fail-closed prioritization of measured ingestion and review gaps, selecting evidence enrichment before resolver changes.
- [`MEASURED-OPERATIONAL-DISPOSITION-V1.md`](MEASURED-OPERATIONAL-DISPOSITION-V1.md) — assigns measured review gaps to evidence enrichment or durable human review without resolver-policy changes.
- [`PRODUCTION-EVIDENCE-ENRICHMENT-V1.md`](PRODUCTION-EVIDENCE-ENRICHMENT-V1.md) — source-backed review work queue and bounded evidence-enrichment cycle without resolver-policy weakening.
- [`PRODUCTION-EVIDENCE-ENRICHMENT-V2.md`](PRODUCTION-EVIDENCE-ENRICHMENT-V2.md) — strengthens sparse Onix MY26 evidence before ingestion and reduces the bounded replay while keeping enrichment provenance case-bound.
- [`PRODUCTION-EVIDENCE-ENRICHMENT-V3.md`](PRODUCTION-EVIDENCE-ENRICHMENT-V3.md) — uses case-bound Volkswagen MY26 mechanical evidence while retaining the one-sided-model-year abstention.
- [`PRODUCTION-QUALITY-GATE-V1.md`](PRODUCTION-QUALITY-GATE-V1.md) — integrated bounded product-operation gate over end-to-end ingestion, consumer reads, identity precision/recall, and review dispositions.
- [`PRODUCTION-QUALITY-GATE-V2.md`](PRODUCTION-QUALITY-GATE-V2.md) — closes the pre-enrichment bounded operation cycle with measured review priorities.
- [`PRODUCTION-QUALITY-GATE-V3.md`](PRODUCTION-QUALITY-GATE-V3.md) — closes the evidence-enrichment cycle with preserved identity safety metrics.
- [`OPERATIONAL-READINESS-V1.md`](OPERATIONAL-READINESS-V1.md) — deterministic private-operation preflight spanning runtime, harness, packaging, identity benchmark, repository facts, and sequential tests.
- [`MVP-EXIT-GATE-V1.md`](MVP-EXIT-GATE-V1.md) — formal private-MVP exit criteria requiring repository readiness plus independently verified executable green CI.
- [`PUBLIC-WEB-ACQUISITION-CHARACTERIZATION-V1.md`](PUBLIC-WEB-ACQUISITION-CHARACTERIZATION-V1.md) — one live operational compatibility measurement across retained public source URLs.
- [`BROWSER-ACQUISITION-CHARACTERIZATION-V1.md`](BROWSER-ACQUISITION-CHARACTERIZATION-V1.md) — controlled Chromium measurement; generic browser fallback was not selected.
- [`COMPLIANT-ALTERNATIVE-SOURCES-V1.md`](COMPLIANT-ALTERNATIVE-SOURCES-V1.md) — current primary-source evaluation and selected official-source paths.
- [`EEA-SOURCE-FAMILY-V1.md`](EEA-SOURCE-FAMILY-V1.md) — frozen official EEA passenger-car monitoring source family.
- [`EEA-SEMANTIC-EXPANSION-V2.md`](EEA-SEMANTIC-EXPANSION-V2.md) — source-backed fuel semantics plus regulatory identity nonclaims.
- [`OFFICIAL-SOURCE-DISCOVERY-V1.md`](OFFICIAL-SOURCE-DISCOVERY-V1.md) — bounded official-source candidate discovery with explicit non-identity-proof contract.
- [`RECURRING-SOURCE-POLICY-V1.md`](RECURRING-SOURCE-POLICY-V1.md) — fail-closed robots interpretation and per-host pacing gate required before repeated live acquisition.
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
