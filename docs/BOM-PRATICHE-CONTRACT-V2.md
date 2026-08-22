# Bom Pratiche consumer contract V2 — draft

Status: **draft; not an external compatibility promise**.

## Identity payload (`2.0`)

`export_catalog_vehicle_payload()` exposes a stable opaque ID plus structured identity fields: make, model, generation, variant, powertrain, transmission, body style, market, separate manufacturing/model-year ranges, aliases, engine identifiers, namespaced external identifiers and superseded IDs in `redirectsFrom`.

Consumers should join on `entity.id`, never on a presentation label. An ID survives descriptive corrections. Historical IDs can resolve to the current canonical ID.

## Semantics

Manufacturing year and model year are separate. Version, powertrain, transmission and body style are separate structured dimensions. External identifiers are `(namespace, value)` pairs, so equal raw values from different systems do not collide.

Catalog Identity Policy V2.1 classifies external-identifier namespaces as `STRONG`, `SUPPORTING` or `REFERENCE_ONLY`. Only `STRONG` may establish an automatic catalog match by itself after contradiction checks. `SUPPORTING` never matches alone. `REFERENCE_ONLY` and unknown namespaces do not participate in automatic matching. FIPE is currently `SUPPORTING`.

This policy changes matching semantics only; it does not change the `2.0` payload shape.

## Consumer rules

- treat `entity.id` as the stable catalog reference;
- resolve historical IDs before joining catalog data;
- do not infer identity from presentation labels alone;
- do not assume that the presence of an external identifier means it is a strong identity key;
- do not treat candidate confidence as an automatic conflict winner;
- surface unresolved conflicts rather than converting them into accepted facts.

## Evidence and conflicts

The V2 persistence layer can associate catalog candidates, canonical facts, provenance and conflicts with the stable catalog ID while reusing the existing Podium 7 evidence records. This draft intentionally does not freeze an external audit-bundle schema yet.

## Remaining gates before Bom Pratiche adoption

1. Define evidence requirements for externally published identity dimensions and administrative overrides.
2. Freeze JSON naming/casing and compatibility policy.
3. Add API-level lookup/redirect behavior, pagination and error semantics.
4. Freeze a separate audit/provenance response contract only when the consumer needs it.
