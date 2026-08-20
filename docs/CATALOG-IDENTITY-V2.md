# Podium 7 Catalog Identity V2

Status: **integration branch** (`feat/catalog-identity-v2`).

## Canonical identity

A catalog vehicle is separate from the legacy `AutomotiveIdentity` and from physical listings. V2 identity dimensions are make, model/aliases, generation, variant, powertrain, transmission, body style, market, manufacturing-year range, model-year range, engine identifiers and namespaced external identifiers.

Legacy `year_from/year_to` is intentionally not auto-converted because its existing semantics do not distinguish manufacturing year from model year.

## Resolution policy

The V2 resolver is deterministic and conservative.

1. Explicit contradictions in make, generation, variant, powertrain, transmission, body style, market or non-overlapping year ranges produce `NO_MATCH`.
2. Model/alias labels are compared after case/punctuation normalization and token-order normalization.
3. Partial labels such as `Corolla XEi` vs `Corolla XEi 1.8` route to `REVIEW` rather than automatic merge.
4. Shared namespaced external identifiers can produce `MATCH` when there is no contradictory identity evidence.
5. Otherwise automatic match requires explicit equal generation and powertrain; missing trim-defining data routes to `REVIEW`.

## Stable IDs, corrections and merges

Canonical catalog IDs are opaque (`veh_<uuid>`) and are not derived from mutable attributes. Corrections preserve the ID and append an identity revision. Duplicate merges preserve the old ID as a redirect. Chained merges flatten redirects so historical aliases resolve to the live canonical entity.

## Catalog vs physical vehicle

`PhysicalVehicleListing` is distinct from catalog identity. Listing-specific data such as source, odometer and VIN references a canonical catalog vehicle. Merge operations move listing references to the survivor.

## Evidence, confidence and conflicts

The V2 catalog extension reuses the existing Podium 7 records `CandidateFact`, `CanonicalFact`, `Conflict` and `ProvenanceRecord`, with catalog-specific persistence whose entity references point at canonical V2 vehicle IDs.

A catalog candidate retains raw value, normalized value, unit, evidence ID, extraction method, optional confidence and normalization rule. Raw evidence retains source, retrieval timestamp, locator, acquisition method and raw-content reference. Existing fusion semantics remain unchanged: agreement can canonicalize with provenance; disagreement remains an explicit conflict instead of silently selecting a source by confidence.

## Persistence

The SQLite evolution is additive. V1 tables and `PRAGMA user_version` remain owned by `EvidenceStore`. Catalog schema metadata is tracked separately in `catalog_v2_schema_metadata`, avoiding reinterpretation of legacy identity rows.

## Deliberately not duplicated

V2 does not copy V1 implementations into `domain.py`, `identity.py`, `persistence.py`, `export.py` or `review.py`. The integration is isolated in `podium7.catalog` and composes the existing evidence, fusion and persistence primitives.

## Remaining production gates

- define evidence requirements for creation/correction of externally published identity dimensions;
- define an external-identifier namespace registry and identity strength per namespace;
- freeze the external JSON compatibility policy;
- add API-level lookup/redirect behavior when the consumer API is introduced.
