# Documentation Authority Matrix

Status: working authority classification for baseline reconstruction

## Legend

- `AUTHORITATIVE`: current source of truth for the named concern;
- `SUPPORTING`: useful reference, not the primary truth;
- `EVIDENCE`: measured or historical proof artifact;
- `HISTORICAL`: useful for traceability, not current authority;
- `SUPERSEDED`: replaced by newer authority;
- `ARCHIVE_CANDIDATE`: keep for traceability, but move out of the active path;
- `MERGE_CANDIDATE`: should be consolidated into another authority document;
- `DELETE_CANDIDATE`: no durable value after consolidation.

## Core authority

| Document | Classification | Purpose | Notes | Action |
| --- | --- | --- | --- | --- |
| `README.md` | AUTHORITATIVE | entry point | keep short and route to authority | UPDATE |
| `docs/PROJECT-CHARTER.md` | AUTHORITATIVE | mission/scope/non-scope | new canonical charter | ADD |
| `docs/ARCHITECTURE.md` | AUTHORITATIVE | current architecture | assembly view only | ADD |
| `docs/REQUIREMENTS.md` | AUTHORITATIVE | requirement baseline | extracted, not invented | ADD |
| `docs/QUALITY-GATES.md` | AUTHORITATIVE | quality model and gates | gate definitions for acceptance | ADD |
| `docs/OPERATIONS.md` | AUTHORITATIVE | install/operate/recover | operational authority | ADD |
| `docs/PROJECT-STATE.md` | AUTHORITATIVE | current state | single truth for current baseline and blockers | ADD |
| `docs/ROADMAP.md` | AUTHORITATIVE | future work | only approved future evolution | ADD |
| `docs/CLOSEOUT-PLAN.md` | AUTHORITATIVE | closure gate model | finite closeout plan | ADD |
| `docs/INDEX.md` | AUTHORITATIVE | doc taxonomy/navigation | must reflect current structure | UPDATE |

## Derived or legacy current-state trackers

| Document | Classification | Purpose | Notes | Action |
| --- | --- | --- | --- | --- |
| `docs/HANDOFF.md` | SUPPORTING | compact resume point | should derive from project-state and closeout-plan | UPDATE |
| `docs/CURRENT-STATE.md` | SUPERSEDED | legacy state snapshot | overlaps with `PROJECT-STATE.md` | MERGE_INTO `docs/PROJECT-STATE.md` |
| `docs/CURRENT-WORK.md` | SUPPORTING | active work tracker | keep only if active work exists | UPDATE |

## Operating contracts and invariants

| Document | Classification | Purpose | Notes | Action |
| --- | --- | --- | --- | --- |
| `docs/DEVELOPMENT-WORKFLOW.md` | AUTHORITATIVE | workflow policy | single source for autonomy, validation, and done | KEEP |
| `docs/INVARIANTS.md` | AUTHORITATIVE | cross-cutting invariants | current product invariants | KEEP |
| `docs/LICENSING-STATUS.md` | AUTHORITATIVE | private/proprietary status | release boundary authority | KEEP |
| `docs/OPERATOR-INSTALLATION-V1.md` | AUTHORITATIVE | validated install runbook | operational authority | KEEP |
| `docs/CATALOG-REVIEW-OPERATOR-V1.md` | AUTHORITATIVE | review operator contract | mutation and safety boundary | KEEP |
| `docs/generated/README.md` | SUPPORTING | generated artifact policy | not current product authority | KEEP |

## Architecture and product contracts

| Document | Classification | Purpose | Notes | Action |
| --- | --- | --- | --- | --- |
| `docs/ARCHITECTURE-PRINCIPLES.md` | SUPPORTING | architecture rationale | supports architecture decisions | KEEP |
| `docs/ADR-0001-MARKET-FIRST-INFRASTRUCTURE.md` | AUTHORITATIVE | decision record | decision-level authority | KEEP |
| `docs/PERSISTENCE-AND-EVIDENCE-STORE.md` | SUPPORTING | persistence design | implementation/design support | KEEP |
| `docs/ENTITY-RESOLUTION-V1.md` | SUPPORTING | resolver design | support, not state | KEEP |
| `docs/DATA-FUSION-AND-CONFLICTS-V1.md` | SUPPORTING | fusion/conflict design | support, not state | KEEP |
| `docs/NORMALIZATION-V1.md` | SUPPORTING | normalization design | support, not state | KEEP |
| `docs/CATALOG-IDENTITY-V2.md` | AUTHORITATIVE | catalog identity contract | product contract authority | KEEP |
| `docs/CATALOG-EVIDENCE-POLICY-V2.md` | AUTHORITATIVE | evidence policy contract | product contract authority | KEEP |
| `docs/CATALOG-JSON-CONTRACT-V2.md` | AUTHORITATIVE | consumer JSON contract | external-facing schema authority | KEEP |
| `docs/CATALOG-CONSUMER-API-V2.md` | AUTHORITATIVE | consumer API contract | external-facing API authority | KEEP |
| `docs/CATALOG-REVIEW-OPERATOR-V1.md` | AUTHORITATIVE | operator CLI contract | review surface authority | KEEP |

## Evidence records

| Document | Classification | Purpose | Notes | Action |
| --- | --- | --- | --- | --- |
| `docs/CATALOG-IDENTITY-BENCHMARK-V1.md` | EVIDENCE | identity benchmark result | keep as proof, not state | KEEP |
| `docs/CATALOG-YEAR-SEMANTICS-CHALLENGE-V1.md` | EVIDENCE | semantics challenge evidence | keep as proof, not state | KEEP |
| `docs/PRODUCTION-*` docs | EVIDENCE | measured replay and quality gates | evidence records, not current authority | KEEP |
| `docs/INMETRO-PBEV-DOCUMENT-PATH-V1.md` | EVIDENCE | source-specific acquisition path evidence | keep as evidence record | KEEP |
| `docs/EEA-*` docs | EVIDENCE | source family and semantic evidence | keep as evidence records | KEEP |
| `docs/NHTSA-VPIC-EVIDENCE-CONTRACT-V1.md` | EVIDENCE | source-specific evidence contract | keep as evidence record | KEEP |
| `docs/PUBLIC-WEB-ACQUISITION-CHARACTERIZATION-V1.md` | EVIDENCE | web acquisition measurement | keep as evidence record | KEEP |
| `docs/BROWSER-ACQUISITION-CHARACTERIZATION-V1.md` | EVIDENCE | browser acquisition measurement | keep as evidence record | KEEP |
| `docs/REPEATABLE-WEB-EXTRACTION-V1.md` | EVIDENCE | extraction benchmark/evidence | keep as evidence record | KEEP |
| `docs/SCIENTIFIC-FOUNDATION.md` | SUPPORTING | scientific references | context for evidence | KEEP |

## Historical and archive candidates

| Document | Classification | Purpose | Notes | Action |
| --- | --- | --- | --- | --- |
| `docs/exec-plans/completed/*` | HISTORICAL | completed execution history | keep for traceability | ARCHIVE |
| `docs/exec-plans/active/README.md` | SUPPORTING | active plan policy | no active plan currently | KEEP |
| `docs/FIRST-REAL-STRUCTURED-INGESTION.md` | HISTORICAL | historical milestone | not current authority | ARCHIVE_CANDIDATE |
| `docs/MVP-EXIT-GATE-V1.md` | HISTORICAL | closed MVP gate | superseded by the closeout plan | ARCHIVE_CANDIDATE |
| `docs/OPERATIONAL-READINESS-V1.md` | HISTORICAL | readiness gate record | evidence of validation, not current authority | ARCHIVE_CANDIDATE |
| `docs/POST-MVP-SOURCE-ACQUISITION-OUTCOME-V1.md` | HISTORICAL | synchronization outcome | closeout history | ARCHIVE_CANDIDATE |

## Disposition rule

If a document is current authority, keep it in the active path. If it is proof, keep it as evidence. If it is no longer current but preserves valuable traceability, archive it. If it only duplicates a newer authority, merge it into the newer authority and reduce the number of active voices.
