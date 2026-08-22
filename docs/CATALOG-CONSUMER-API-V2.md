# Podium 7 Catalog Consumer API V2

Status: **transport-neutral consumer adapter**.

This API sits above `CatalogStore` and the frozen Catalog JSON Contract `2.0`. It defines lookup, redirect, error and pagination semantics without adding an HTTP framework or transport dependency.

## Operations

The public adapter functions are:

```text
lookup_catalog_vehicle(store, vehicle_id, contract_version="2.0")
list_catalog_vehicles(store, limit=50, cursor=None, contract_version="2.0")
```

Both return JSON-compatible dictionaries and do not expose SQLite handles or persistence rows.

## Lookup

### Canonical ID

A successful canonical lookup returns:

```json
{
  "ok": true,
  "requestedId": "veh_...",
  "canonicalId": "veh_...",
  "redirected": false,
  "vehicle": {"contractVersion": "2.0", "entity": {}, "redirectsFrom": []}
}
```

### Historical ID

A historical merged ID remains a valid lookup alias. The response has:

- `requestedId`: the historical input;
- `canonicalId`: the final live ID;
- `redirected: true`;
- `vehicle.entity.id`: the same final canonical ID;
- `vehicle.redirectsFrom`: historical IDs resolved to that canonical entity.

The API never returns a retired historical ID as the canonical entity ID.

## Not found and validation errors

Errors use the envelope:

```json
{
  "ok": false,
  "error": {
    "code": "...",
    "message": "..."
  }
}
```

Stable V2 error codes:

```text
CATALOG_NOT_FOUND
CATALOG_INVALID_ID
CATALOG_INVALID_PAGE_SIZE
CATALOG_INVALID_CURSOR
CATALOG_UNSUPPORTED_CONTRACT_VERSION
```

`CATALOG_NOT_FOUND` means the supplied non-empty ID does not resolve to a live catalog vehicle. Invalid input and unsupported-version conditions are kept distinct from not-found.

A future HTTP adapter may map these codes to transport statuses, but HTTP status codes are not part of this transport-neutral layer.

## Listing and pagination

`list_catalog_vehicles()` uses keyset pagination over canonical catalog IDs.

Rules:

- default page size: `50`;
- maximum page size: `100`;
- valid limit range: `1..100`;
- items are ordered by canonical `entity.id`;
- redirect-only historical IDs are not emitted as separate list items;
- `nextCursor` is either the last canonical ID of the current page when another page exists, or JSON `null` when the page is terminal;
- a cursor is an opaque consumer token even though its current representation is a canonical catalog ID;
- a historical ID may be supplied as a cursor and is resolved to its final canonical ID before pagination;
- a cursor that does not resolve to a live catalog vehicle returns `CATALOG_INVALID_CURSOR`.

The underlying store exposes only a small canonical-ID page primitive; the consumer adapter owns page-size policy, cursor validation and payload export.

## Contract version negotiation

The consumer API defaults to Catalog JSON Contract `2.0`. Unsupported versions produce `CATALOG_UNSUPPORTED_CONTRACT_VERSION` instead of leaking an exporter exception.

The adapter does not silently upgrade consumers to a newer wire contract.

## Non-goals

This layer does not define:

- HTTP routes, headers or status codes;
- authentication/authorization;
- write endpoints;
- search/ranking endpoints;
- provenance/audit bundles.

Those should be added only when there is a concrete consumer need.
