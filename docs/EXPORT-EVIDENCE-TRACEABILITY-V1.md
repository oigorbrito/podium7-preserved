# Catalog V2 Export Evidence Traceability V1

Status: implementation prepared; executable validation pending

Issue: #154
Parent: #140
Related measurement: #141 / #152

## Purpose

Provide an externally consumable provenance bundle for a Catalog V2 vehicle without requiring consumers to know the database schema, while preserving the frozen Catalog JSON Contract `2.0` unchanged.

## Contract correction

The initial implementation attempted to inject `evidenceTrace` directly into the standard Catalog V2 lookup/list vehicle payload. That conflicts with `CATALOG-JSON-CONTRACT-V2.md`, which freezes the `2.0` top-level vehicle shape to exactly `contractVersion`, `entity`, and `redirectsFrom`, and with `CATALOG-CONSUMER-API-V2.md`, which treats provenance/audit bundles as a separate decision.

The corrected design therefore keeps standard `lookup_catalog_vehicle()` and `list_catalog_vehicles()` unchanged and introduces a separate opt-in bundle:

`podium7.catalog-evidence-trace-bundle.v1`

The bundle contains:

- `schema` — exact bundle schema identifier;
- `vehicle` — an unchanged frozen Catalog JSON Contract `2.0` payload; and
- `evidenceTrace` — deterministic persisted candidate → raw evidence → source references.

## Evidence trace surface

Each trace entry exposes:

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

The provenance bundle refuses to silently omit broken provenance. If a persisted candidate references missing raw evidence, raw evidence references a missing source, or a vehicle has no persisted candidate evidence, bundle creation fails closed.

This failure does not retroactively change the frozen Catalog V2 lookup/list behavior. Standard `2.0` payloads retain their existing compatibility contract; consumers explicitly requesting the provenance bundle accept its stronger provenance precondition.

A historical/redirected catalog ID resolves to its canonical ID before the trace is collected, so historical IDs expose the same canonical provenance.

## Ordering

Trace entries are sorted by attribute, candidate fact ID, evidence ID, and source ID. Output does not depend on SQLite row order.

## Utility disposition

`EXPORT_EVIDENCE_TRACEABILITY_UTILITY = INTEGRATE_AFTER_SYNC_AND_VALIDATION`

This capability is complementary to the internal provenance audit (#152/#153). The audit answers whether persisted links are complete across the operating store; the opt-in export bundle gives an external consumer an auditable path for one canonical vehicle without exposing raw evidence bytes or changing the frozen `2.0` wire shape.

The original direct injection into `2.0` is `REJECTED` because it would silently change a frozen contract. The corrected opt-in bundle is the candidate for integration after executable validation.

## Nonchanges

- no change to frozen Catalog JSON Contract `2.0`;
- no change to standard lookup/list response semantics;
- no resolver-policy change;
- no evidence-strength change;
- no fusion/conflict change;
- no source-policy change;
- no publication-policy change;
- no raw evidence content is exposed;
- no missing provenance is inferred or reconstructed.

## Validation state

Focused tests require the standard `2.0` lookup/list vehicle shape to remain unchanged, verify deterministic bundle ordering and redirect-to-canonical behavior, and exercise deliberate broken evidence/source links plus missing candidate evidence. Repository-required executable validation remains mandatory before integration; issue #112 is the known hosted-runner blocker.
