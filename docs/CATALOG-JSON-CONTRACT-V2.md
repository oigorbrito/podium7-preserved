# Podium 7 Catalog JSON Contract V2

Status: **wire shape frozen for contract version `2.0`**.

This document freezes the JSON-compatible payload returned by `export_catalog_vehicle_payload()` for contract version `2.0`. It does not define HTTP transport, pagination or endpoint error responses; those belong to the consumer API gate.

## Compatibility rule

`2.0` is the default contract version and must not silently change shape.

The exporter accepts an explicit `contract_version`. Unsupported versions fail explicitly. A future contract may be added alongside `2.0`, but changing/removing/renaming a `2.0` field or changing its JSON type requires a new contract version. The default must not be advanced merely because a newer version exists.

Internal dataclass evolution is not a contract change. The `2.0` serializer uses an explicit field mapping so newly added internal attributes do not appear in the wire payload automatically.

## Top-level object

Exactly these keys are emitted for `2.0`:

```text
contractVersion
entity
redirectsFrom
```

- `contractVersion`: required string, exactly `"2.0"` for this contract.
- `entity`: required object containing the canonical catalog identity.
- `redirectsFrom`: required array of historical catalog IDs that resolve to `entity.id`; empty when none exist.

JSON object key order is not part of the contract.

## Entity object

The `entity` object always contains exactly these keys:

```text
id
make
model
generation
variant
powertrain
transmission
body_style
market
manufacture_year_from
manufacture_year_to
model_year_from
model_year_to
aliases
engine_identifiers
external_identifiers
```

Naming/casing is intentionally frozen as emitted today. Top-level compatibility keys use camelCase; catalog identity field names retain their existing snake_case. Consumers must not infer a casing conversion rule.

### Required non-null strings

```text
id
make
model
```

`id` is the resolved canonical opaque `veh_<uuid>` identifier.

### Required nullable fields

These keys are always present and use JSON `null` when unknown:

```text
generation
variant
powertrain
transmission
body_style
market
manufacture_year_from
manufacture_year_to
model_year_from
model_year_to
```

Year bounds are JSON integers when present. Other fields in this group are strings when present.

### Required arrays

These keys are always present as JSON arrays, including when empty:

```text
aliases
engine_identifiers
external_identifiers
```

`aliases` and `engine_identifiers` contain strings.

Each `external_identifiers` entry is exactly:

```json
{"namespace": "...", "value": "..."}
```

Both fields are required strings. Namespace matching strength (`STRONG`, `SUPPORTING`, `REFERENCE_ONLY`) is internal policy and is not added to the `2.0` wire object.

## Redirect semantics

The caller may export either a live canonical ID or a historical merged ID.

In both cases:

- `entity.id` is the final canonical ID;
- `redirectsFrom` contains historical IDs redirected to that canonical ID;
- chained catalog merges are flattened by catalog persistence before export;
- `redirectsFrom` is deterministically ordered by ID.

A historical ID is therefore an input alias, never an alternate `entity.id` in the payload.

## Backward compatibility

For `2.0`, the following are breaking changes and require a new contract version:

- renaming, removing or recasing a key;
- changing a field between scalar/object/array/nullability categories;
- omitting a key currently guaranteed to be present;
- changing redirect semantics so a historical request returns a historical rather than canonical `entity.id`;
- adding internal model fields directly to the `2.0` entity object.

Presentation formatting, persistence internals, resolver heuristics and evidence policy may evolve without a contract version change when the emitted `2.0` JSON semantics remain unchanged.

## Non-goals

This contract does not yet define:

- HTTP routes or methods;
- lookup/not-found status codes;
- pagination;
- request schemas;
- authentication;
- a provenance/audit response bundle.

Those remain separate consumer/API decisions.
