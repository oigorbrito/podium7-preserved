# Catalog V2 Export Evidence Traceability V1

Status: implementation prepared; executable validation pending

Issue: #154
Parent: #140
Related measurement: #141 / #152

## Purpose

Make the externally consumable Catalog V2 lookup/list payload traceable to the persisted evidence that produced the canonical vehicle without requiring consumers to know the database schema.

This closes the documented `consumer/export → canonical evidence` traceability requirement. It is additive to the existing Catalog V2 contract and does not change identity semantics.

## Export surface

Each exported vehicle includes deterministic `evidenceTrace` entries derived only from persisted Catalog V2 candidate facts.

Each entry exposes:

- `candidateFactId`;
- `attribute`;
- `evidenceId`;
- `sourceId`;
- `evidenceLocator`;
- `sourceLocator`;
- `rawContentRef`;
- `extractionMethod`;
- `normalizationRule`.

The trace intentionally does not duplicate raw/normalized candidate values or raw evidence bytes. Those remain internal persisted evidence, while identifiers and locators provide an auditable path back to them.

## Fail-closed behavior

Export refuses to silently omit broken provenance. If a persisted candidate references missing raw evidence, or raw evidence references a missing source, export raises instead of publishing an apparently complete vehicle without its evidence chain.

A historical/redirected catalog ID resolves to its canonical ID before the trace is collected, so historical IDs expose the same canonical provenance.

## Ordering

Trace entries are sorted by attribute, candidate fact ID, evidence ID, and source ID. Output does not depend on SQLite row order.

## Nonchanges

- no resolver-policy change;
- no evidence-strength change;
- no fusion/conflict change;
- no source-policy change;
- no publication-policy change;
- no raw evidence content is exposed;
- no missing provenance is inferred or reconstructed.

## Validation state

Focused tests cover lookup, list, deterministic ordering, redirect-to-canonical behavior, and deliberate broken evidence/source links. Repository-required executable validation remains mandatory before integration; issue #112 is the known hosted-runner blocker.
