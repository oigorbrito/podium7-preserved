# Bom Pratiche consumer contract V2 — draft transport

Status: **identity JSON wire shape `2.0` frozen; consumer API/transport still draft**.

## Identity payload (`2.0`)

`export_catalog_vehicle_payload()` exposes a stable opaque ID plus structured identity fields: make, model, generation, variant, powertrain, transmission, body style, market, separate manufacturing/model-year ranges, aliases, engine identifiers, namespaced external identifiers and superseded IDs in `redirectsFrom`.

The exact field names, nullability, array shapes, redirect semantics and versioning rules are frozen in `CATALOG-JSON-CONTRACT-V2.md`. The `2.0` serializer is explicit and does not automatically expose newly added internal dataclass fields.

Consumers should join on `entity.id`, never on a presentation label. An ID survives descriptive corrections. Historical IDs resolve to the current canonical ID and are reported in `redirectsFrom`.

## Semantics

Manufacturing year and model year are separate. Version, powertrain, transmission and body style are separate structured dimensions. External identifiers are `(namespace, value)` pairs, so equal raw values from different systems do not collide.

Catalog Identity Policy V2.1 classifies external-identifier namespaces as `STRONG`, `SUPPORTING` or `REFERENCE_ONLY`. Only `STRONG` may establish an automatic catalog match by itself after contradiction checks. `SUPPORTING` never matches alone. `REFERENCE_ONLY` and unknown namespaces do not participate in automatic matching. FIPE is currently `SUPPORTING`.

The internal publication evidence policy requires normal externally publishable creation/correction to be `EVIDENCE_BACKED` with at least one evidence reference. Corrections require a reason. Administrative overrides are explicitly `ENGINEERING_CHOICE` and require actor + reason. This policy does not change the `2.0` payload shape.

## Consumer rules

- treat `entity.id` as the stable catalog reference;
- resolve historical IDs before joining catalog data;
- do not infer identity from presentation labels alone;
- do not assume that the presence of an external identifier means it is a strong identity key;
- do not infer a casing conversion rule: `2.0` field names are exact contract names;
- do not treat candidate confidence as an automatic conflict winner;
- surface unresolved conflicts rather than converting them into accepted facts.

## Evidence and conflicts

The V2 persistence layer can associate catalog candidates, canonical facts, provenance and conflicts with the stable catalog ID while reusing the existing Podium 7 evidence records. The consumer contract intentionally does not freeze an external audit-bundle schema yet.

## Remaining gates before Bom Pratiche adoption

1. Add API-level lookup/redirect behavior, pagination and error semantics.
2. Freeze a separate audit/provenance response contract only when the consumer needs it.
