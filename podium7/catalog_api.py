from __future__ import annotations

from enum import Enum
from typing import Any

from .catalog import (
    CATALOG_CONTRACT_DEFAULT_VERSION,
    CATALOG_CONTRACT_SUPPORTED_VERSIONS,
    CatalogStore,
    export_catalog_vehicle_payload,
)


CATALOG_API_DEFAULT_PAGE_SIZE = 50
CATALOG_API_MAX_PAGE_SIZE = 100


class CatalogApiErrorCode(str, Enum):
    NOT_FOUND = "CATALOG_NOT_FOUND"
    INVALID_ID = "CATALOG_INVALID_ID"
    INVALID_PAGE_SIZE = "CATALOG_INVALID_PAGE_SIZE"
    INVALID_CURSOR = "CATALOG_INVALID_CURSOR"
    UNSUPPORTED_CONTRACT_VERSION = "CATALOG_UNSUPPORTED_CONTRACT_VERSION"


def _error(
    code: CatalogApiErrorCode,
    message: str,
    **details: Any,
) -> dict[str, Any]:
    return {
        "ok": False,
        "error": {
            "code": code.value,
            "message": message,
            **details,
        },
    }


def _contract_error(contract_version: str) -> dict[str, Any] | None:
    if contract_version in CATALOG_CONTRACT_SUPPORTED_VERSIONS:
        return None
    return _error(
        CatalogApiErrorCode.UNSUPPORTED_CONTRACT_VERSION,
        "unsupported catalog contract version",
        contractVersion=contract_version,
    )


def lookup_catalog_vehicle(
    store: CatalogStore,
    vehicle_id: str,
    *,
    contract_version: str = CATALOG_CONTRACT_DEFAULT_VERSION,
) -> dict[str, Any]:
    contract_error = _contract_error(contract_version)
    if contract_error is not None:
        return contract_error
    if not isinstance(vehicle_id, str) or not vehicle_id.strip():
        return _error(
            CatalogApiErrorCode.INVALID_ID,
            "catalog vehicle id must be non-empty text",
        )

    canonical = store.resolve_catalog_id(vehicle_id)
    if store.get_catalog_vehicle(canonical) is None:
        return _error(
            CatalogApiErrorCode.NOT_FOUND,
            "catalog vehicle not found",
            requestedId=vehicle_id,
        )

    return {
        "ok": True,
        "requestedId": vehicle_id,
        "canonicalId": canonical,
        "redirected": canonical != vehicle_id,
        "vehicle": export_catalog_vehicle_payload(
            store,
            vehicle_id,
            contract_version=contract_version,
        ),
    }


def list_catalog_vehicles(
    store: CatalogStore,
    *,
    limit: int = CATALOG_API_DEFAULT_PAGE_SIZE,
    cursor: str | None = None,
    contract_version: str = CATALOG_CONTRACT_DEFAULT_VERSION,
) -> dict[str, Any]:
    contract_error = _contract_error(contract_version)
    if contract_error is not None:
        return contract_error
    if (
        isinstance(limit, bool)
        or not isinstance(limit, int)
        or not 1 <= limit <= CATALOG_API_MAX_PAGE_SIZE
    ):
        return _error(
            CatalogApiErrorCode.INVALID_PAGE_SIZE,
            f"limit must be an integer between 1 and {CATALOG_API_MAX_PAGE_SIZE}",
        )

    after_id: str | None = None
    if cursor is not None:
        if not isinstance(cursor, str) or not cursor.strip():
            return _error(
                CatalogApiErrorCode.INVALID_CURSOR,
                "cursor must be a canonical or historical catalog id",
            )
        after_id = store.resolve_catalog_id(cursor)
        if store.get_catalog_vehicle(after_id) is None:
            return _error(
                CatalogApiErrorCode.INVALID_CURSOR,
                "cursor does not resolve to a catalog vehicle",
                cursor=cursor,
            )

    ids = store.catalog_vehicle_ids_page(after_id=after_id, limit=limit + 1)
    has_more = len(ids) > limit
    page_ids = ids[:limit]
    next_cursor = page_ids[-1] if has_more and page_ids else None

    return {
        "ok": True,
        "items": [
            export_catalog_vehicle_payload(
                store,
                vehicle_id,
                contract_version=contract_version,
            )
            for vehicle_id in page_ids
        ],
        "nextCursor": next_cursor,
    }


__all__ = [
    "CATALOG_API_DEFAULT_PAGE_SIZE",
    "CATALOG_API_MAX_PAGE_SIZE",
    "CatalogApiErrorCode",
    "list_catalog_vehicles",
    "lookup_catalog_vehicle",
]
