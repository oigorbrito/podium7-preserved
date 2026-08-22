# Podium 7 Catalog Identity V2

Status: **Catalog Identity V2 integrated in `main`; V2.1 external-identifier policy defined here**.

## Canonical identity

A catalog vehicle is separate from the legacy `AutomotiveIdentity` and from physical listings. V2 identity dimensions are make, model/aliases, generation, variant, powertrain, transmission, body style, market, manufacturing-year range, model-year range, engine identifiers and namespaced external identifiers.

Legacy `year_from/year_to` is intentionally not auto-converted because its existing semantics do not distinguish manufacturing year from model year.

## Resolution policy

The V2 resolver is deterministic and conservative.

1. Explicit contradictions in make, generation, variant, powertrain, transmission, body style, market or non-overlapping year ranges produce `NO_MATCH`.
2. Model/alias labels are compared after case/punctuation normalization and token-order normalization.
3. Partial labels such as `Corolla XEi` vs `Corolla XEi 1.8` route to `REVIEW` rather than automatic merge.
4. External identifiers participate according to the namespace strength policy below; only a shared `STRONG` identifier can produce `MATCH` by itself, and never when explicit identity evidence contradicts.
5. Otherwise automatic match requires explicit equal generation and powertrain; missing trim-defining data routes to `REVIEW`.

## External-identifier namespace registry — V2.1

Each external identifier remains a `(namespace, value)` pair. Namespace lookup is normalized case-insensitively and with surrounding whitespace removed.

The resolver recognizes three strengths:

- `STRONG`: a shared namespace + value may produce automatic `MATCH` after all explicit contradiction checks pass.
- `SUPPORTING`: may support structural identity evidence but never produces `MATCH` by itself. If both sides carry registered supporting identifiers that do not agree, resolution remains `REVIEW` rather than forcing a merge or a contradiction.
- `REFERENCE_ONLY`: available for lookup/interoperability/provenance but excluded from automatic matching decisions.

Unknown namespaces default safely to `REFERENCE_ONLY`; sharing an unknown identifier therefore cannot create an automatic match. A caller may supply an explicit registry to the resolver for additional namespaces without changing the default policy.

Current default registry:

```text
fipe = SUPPORTING
```

FIPE is intentionally not `STRONG`: the code is treated as supporting catalog evidence rather than universal canonical configuration identity. Promoting it to `STRONG` requires a separate documented product decision.

A disagreement between identifiers is not treated as an automatic `NO_MATCH` unless another explicit identity dimension already contradicts. This preserves the false-merge-first posture and routes uncertain cases to review.

## Publication evidence gate

The minimum evidence policy for externally publishable catalog changes is defined in `CATALOG-EVIDENCE-POLICY-V2.md`.

Normal creation/correction requires `EVIDENCE_BACKED` plus at least one evidence reference; corrections also require a reason. Administrative override is explicit `ENGINEERING_CHOICE` and requires both actor and reason. The policy also distinguishes semantic identity changes from informational edits so that formatting/reference-only changes are not silently treated as new identity.

This gate is policy-only at this stage: it does not alter the SQLite schema or freeze an audit/provenance response format.

## External JSON contract

The catalog identity wire shape for contract version `2.0` is frozen in `CATALOG-JSON-CONTRACT-V2.md`.

The exporter uses an explicit serializer rather than exposing `CatalogVehicleIdentity` through `asdict()`. This prevents internal model evolution from silently changing the external payload. `2.0` remains the default, unknown contract versions fail explicitly, nullable identity dimensions remain present as `null`, collections remain arrays, and historical IDs export the final canonical `entity.id` plus `redirectsFrom`.

The existing naming is preserved for compatibility: top-level compatibility keys are camelCase while entity identity fields retain their established snake_case. Any incompatible shape change requires a new contract version.

## Stable IDs, corrections and merges

Canonical catalog IDs are opaque (`veh_<uuid>`) and are not derived from mutable attributes. Corrections preserve the ID and append an identity revision. Duplicate merges preserve the old ID as a redirect. Chained merges flatten redirects so historical aliases resolve to the live canonical entity.

## Catalog vs physical vehicle

`PhysicalVehicleListing` is distinct from catalog identity. Listing-specific data such as source, odometer and VIN references a canonical catalog vehicle. Merge operations move listing references to the survivor.

## Evidence, confidence and conflicts

The V2 catalog extension reuses the existing Podium 7 records `CandidateFact`, `CanonicalFact`, `Conflict` and `ProvenanceRecord`, with catalog-specific persistence whose entity references point at canonical V2 vehicle IDs.

A catalog candidate retains raw value, normalized value, unit, evidence ID, extraction method, optional confidence and normalization rule. Raw evidence retains source, retrieval timestamp, locator, acquisition method and raw-content reference. Existing fusion semantics remain unchanged: agreement can canonicalize with provenance; disagreement remains an explicit conflict instead of silently selecting a source by confidence.

## Persistence

The SQLite evolution is additive. V1 tables and `PRAGMA user_version` remain owned by `EvidenceStore`. Catalog schema metadata is tracked separately in `catalog_v2_schema_metadata`, avoiding reinterpretation of legacy identity rows.

The V2.1 namespace-strength policy, publication evidence policy and V2 JSON compatibility contract do not require a catalog persistence schema change.

## Deliberately not duplicated

V2 does not copy V1 implementations into `domain.py`, `identity.py`, `persistence.py`, `export.py` or `review.py`. The integration is isolated in `podium7.catalog` and composes the existing evidence, fusion and persistence primitives.

## Remaining production gates

- add API-level lookup/redirect behavior when the consumer API is introduced;
- freeze a separate audit/provenance response contract only when a consumer need exists.
