# Podium 7 Catalog Identity V2

Status: **Catalog Identity V2 integrated in `main`; V2.1 external-identifier policy and selected year semantics defined here**.

## Canonical identity

A catalog vehicle is separate from the legacy `AutomotiveIdentity` and from physical listings. V2 identity dimensions are make, model/aliases, generation, variant, powertrain, transmission, body style, market, manufacturing-year range, model-year range, engine identifiers and namespaced external identifiers.

Legacy `year_from/year_to` is intentionally not auto-converted because its existing semantics do not distinguish manufacturing year from model year.

For Brazilian vehicle data, the selected product rule follows the Senatran/RENAVAM distinction: `Ano Fabricação` and `Ano Modelo` remain separate dimensions rather than being collapsed into one generic year.

## Resolution policy

The V2 resolver is deterministic and conservative.

1. Explicit contradictions in make, generation, variant, powertrain, transmission, body style, market or non-overlapping year ranges produce `NO_MATCH`.
2. Manufacturing-year and model-year ranges are evaluated separately. Explicit non-overlap in either dimension is a contradiction; missing manufacturing-year evidence by itself is not.
3. When model year is explicit on only one side, structural agreement alone does not justify an automatic match; the pair routes to `REVIEW` unless stronger identity evidence establishes the match.
4. Model/alias labels are compared after case/punctuation normalization and token-order normalization.
5. Partial labels such as `Corolla XEi` vs `Corolla XEi 1.8` route to `REVIEW` rather than automatic merge.
6. External identifiers participate according to the namespace strength policy below; only a shared `STRONG` identifier can produce `MATCH` by itself, and never when explicit identity evidence contradicts.
7. Otherwise automatic match requires explicit equal generation and powertrain; missing trim-defining data routes to `REVIEW`.

The year rule is source-backed by official Senatran/SERPRO field semantics, FIPE's model-year lookup semantics, and manufacturer examples in `CATALOG-YEAR-SEMANTICS-CHALLENGE-V1.md`. The final canonical matching choice is a product decision recorded on 2026-08-23: preserve explicit year distinctions and prefer `REVIEW` over an unsupported automatic merge when model-year evidence is incomplete.

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

## Consumer read API

The transport-neutral read adapter is defined in `CATALOG-CONSUMER-API-V2.md` and implemented in `podium7.catalog_api`.

It provides canonical/historical lookup, explicit redirect status, stable consumer error codes and keyset pagination over canonical IDs. `CatalogStore` exposes only the small canonical-ID page primitive needed by that adapter; pagination policy and error semantics remain outside persistence.

No HTTP framework or audit endpoint is introduced by this gate.

## Stable IDs, corrections and merges

Canonical catalog IDs are opaque (`veh_<uuid>`) and are not derived from mutable attributes. Corrections preserve the ID and append an identity revision. Duplicate merges preserve the old ID as a redirect. Chained merges flatten redirects so historical aliases resolve to the live canonical entity.

## Catalog vs physical vehicle

`PhysicalVehicleListing` is distinct from catalog identity. Listing-specific data such as source, odometer and VIN references a canonical catalog vehicle. Merge operations move listing references to the survivor.

## Evidence, confidence and conflicts

The V2 catalog extension reuses the existing Podium 7 records `CandidateFact`, `CanonicalFact`, `Conflict` and `ProvenanceRecord`, with catalog-specific persistence whose entity references point at canonical V2 vehicle IDs.

A catalog candidate retains raw value, normalized value, unit, evidence ID, extraction method, optional confidence and normalization rule. Raw evidence retains source, retrieval timestamp, locator, acquisition method and raw-content reference. Existing fusion semantics remain unchanged: agreement can canonicalize with provenance; disagreement remains an explicit conflict instead of silently selecting a source by confidence.

## Persistence

The SQLite evolution is additive. V1 tables and `PRAGMA user_version` remain owned by `EvidenceStore`. Catalog schema metadata is tracked separately in `catalog_v2_schema_metadata`, avoiding reinterpretation of legacy identity rows.

The V2.1 namespace-strength policy, selected year semantics, publication evidence policy, V2 JSON compatibility contract and read adapter do not require a catalog persistence schema version change.

## Deliberately not duplicated

V2 does not copy V1 implementations into `domain.py`, `identity.py`, `persistence.py`, `export.py` or `review.py`. The integration is isolated in the catalog modules and composes the existing evidence, fusion and persistence primitives.

## Identity benchmark

`CATALOG-IDENTITY-BENCHMARK-V1.md` defines the source-backed golden/regression slices. The original version `1.0` contains 12 balanced pairs (`4 MATCH`, `4 NO_MATCH`, `4 REVIEW`) anchored to manufacturer sources from Toyota, Ford, Porsche and BMW; the Brazil slice adds a separate 12-case regional regression set.

The year-semantics slice is now a selected-policy regression gate. Version `year-semantics-1.1` contains six source-backed cases and must resolve exactly according to the Senatran-aligned product rule: `2 MATCH`, `3 NO_MATCH`, `1 REVIEW`.

The benchmark evaluator reports false merge rate, missed duplicate rate, match precision/recall, review rate and ambiguous overcommit. These datasets are regression guards, not statistically representative production estimates. Dataset growth should prioritize hard negatives, incomplete cross-source duplicates, market naming differences and trustworthy real external identifiers, including FIPE.

False merges remain the highest-priority error. A separate audit/provenance consumer API should be frozen only when a concrete consumer need exists.
