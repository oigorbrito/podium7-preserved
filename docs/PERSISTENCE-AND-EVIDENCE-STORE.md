# Podium 7 Persistence and Evidence Store

**Work unit:** `PODIUM7_PERSISTENCE_AND_EVIDENCE_STORE_V1`

## Scientific basis

This work unit follows the supplied handoff baseline, especially W3C PROV, MaDI-Bench, and WANDR. No new horizontal research was performed.

## Decision classification

### `EVIDENCE_BACKED`

- Intermediate evidence must remain inspectable after canonicalization.
- Provenance must be explicitly representable.
- Candidate facts, canonical facts, and conflicts are distinct records.
- Reprocessing requires retaining source/evidence and transformation inputs instead of storing only final values.

### `ENGINEERING_CHOICE`

- SQLite is the first persistence implementation.
- The standard-library `sqlite3` driver is used.
- Complex values are encoded as JSON inside SQLite columns.
- Domain objects remain immutable dataclasses; persistence is handled separately by `EvidenceStore`.
- Inserts are append-once by identifier. Duplicate identifiers raise an integrity error rather than silently overwriting prior evidence.

These choices are implementation decisions, not scientific conclusions.

## Persisted responsibilities

`EvidenceStore` persists independently addressable records for:

- sources;
- automotive entities;
- raw evidence;
- candidate facts;
- provenance;
- canonical facts;
- conflicts.

Foreign keys connect evidence to sources and candidates to both entities and evidence. Canonical facts reference separately stored provenance.

## Preservation rule

The intended path remains:

`SOURCE -> RAW EVIDENCE -> CANDIDATE FACT -> CANONICAL DECISION`

Canonicalization does not delete the candidate or its raw evidence. Conflicts are stored explicitly and are not resolved through implicit last-write-wins behavior.

## Reprocessing

The store exposes source evidence and candidate facts independently of canonical output. This allows later normalization, entity-resolution, or fusion implementations to be rerun against already acquired records without discarding the original evidence references.

## Known limits

- This work unit does not acquire real automotive data.
- `raw_content_ref` currently stores a reference to raw content; blob/file content storage policy remains undecided.
- Database migrations/versioning are not introduced yet because no demonstrated requirement currently justifies a migration framework.
- SQLite is not asserted to be the final production database.
- No confidence threshold is introduced.
- No crawler, browser agent, LLM, scheduler, API, or distributed component is introduced.

## Gate status

Implementation provides the structures necessary for:

- `RAW_EVIDENCE_PERSISTED`
- `PROVENANCE_PERSISTED`
- `REPROCESSABLE`

Per project direction on 2026-08-19, this iteration did not add or rerun tests. Therefore `ROUNDTRIP_TEST = PASS` is not claimed by this document.
