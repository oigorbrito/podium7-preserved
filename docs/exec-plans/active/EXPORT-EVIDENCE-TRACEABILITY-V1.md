# Export Evidence Traceability V1 — execution plan

Issue: #154
Parent mission: #139
Parent product block: #140

## Outcome

Expose auditable persisted evidence references on the external Catalog V2 consumer payload so exported canonical vehicles remain traceable to candidate facts, raw evidence, and sources.

## Acceptance

- preserve existing Catalog V2 identity and redirect fields;
- add deterministic evidence trace entries from persisted candidate facts;
- validate candidate → evidence → source links at export time;
- lookup and list expose the same trace contract;
- redirect lookup resolves to canonical provenance;
- broken persisted links fail closed;
- raw evidence content is not exported;
- no identity/resolver/evidence/fusion/source/publication policy changes.

## Validation

1. focused `tests/test_catalog_export_evidence_trace.py`;
2. repository harness;
3. sequential tests before integration;
4. PR CI as final executable evidence.

Issue #112 remains an external GitHub-hosted runner blocker. No CI PASS may be claimed from implementation review alone.
