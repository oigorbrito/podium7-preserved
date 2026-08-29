from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .catalog import CatalogStore
from .catalog_batch_failure import (
    CatalogBatchFailureSnapshot,
    CatalogBatchFailureStore,
)
from .catalog_ingestion import (
    CatalogIngestionAction,
    CatalogIngestionResult,
    ingest_catalog_record,
)
from .domain import RawEvidence, Source


CATALOG_BATCH_REPORT_SCHEMA = "podium7.catalog-batch-ingestion-report.v1"
CATALOG_BATCH_RECORD_ERROR = "CATALOG_BATCH_RECORD_INVALID"


@dataclass(frozen=True)
class CatalogBatchEnvelope:
    record_id: str | None
    vehicle: dict[str, Any]
    source: Source
    evidence: RawEvidence


@dataclass(frozen=True)
class CatalogBatchRecordResult:
    index: int
    record_id: str | None
    ok: bool
    evidence_id: str
    action: CatalogIngestionAction | None = None
    vehicle_id: str | None = None
    review_id: str | None = None
    error_code: str | None = None
    error_message: str | None = None

    def to_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "index": self.index,
            "recordId": self.record_id,
            "ok": self.ok,
            "evidenceId": self.evidence_id,
            "action": None if self.action is None else self.action.value,
            "vehicleId": self.vehicle_id,
            "reviewId": self.review_id,
        }
        if self.error_code is not None:
            payload["error"] = {
                "code": self.error_code,
                "message": self.error_message,
            }
        return payload


@dataclass(frozen=True)
class CatalogBatchReport:
    total: int
    succeeded: int
    created: int
    matched: int
    review: int
    failed: int
    results: tuple[CatalogBatchRecordResult, ...]

    @property
    def ok(self) -> bool:
        return self.failed == 0

    def to_payload(self) -> dict[str, Any]:
        return {
            "schema": CATALOG_BATCH_REPORT_SCHEMA,
            "ok": self.ok,
            "summary": {
                "total": self.total,
                "succeeded": self.succeeded,
                "created": self.created,
                "matched": self.matched,
                "review": self.review,
                "failed": self.failed,
            },
            "records": [result.to_payload() for result in self.results],
        }


def _required_object(payload: Mapping[str, Any], key: str, path: str) -> Mapping[str, Any]:
    value = payload.get(key)
    if not isinstance(value, Mapping):
        raise ValueError(f"{path}.{key} must be an object")
    return value


def _required_text(payload: Mapping[str, Any], key: str, path: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{path}.{key} must be non-empty text")
    return value.strip()


def _reject_unknown(payload: Mapping[str, Any], allowed: set[str], path: str) -> None:
    unknown = sorted(set(payload) - allowed)
    if unknown:
        raise ValueError(f"{path} has unsupported fields: " + ", ".join(unknown))


def _timestamp(value: str, path: str) -> datetime:
    candidate = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise ValueError(f"{path} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{path} must include a timezone")
    return parsed


def catalog_batch_envelope_from_payload(
    payload: Mapping[str, Any],
    *,
    index: int,
) -> CatalogBatchEnvelope:
    if not isinstance(payload, Mapping):
        raise ValueError(f"records[{index}] must be an object")
    path = f"records[{index}]"
    _reject_unknown(payload, {"recordId", "source", "evidence", "vehicle"}, path)

    record_id_raw = payload.get("recordId")
    if record_id_raw is None:
        record_id = None
    elif isinstance(record_id_raw, str) and record_id_raw.strip():
        record_id = record_id_raw.strip()
    else:
        raise ValueError(f"{path}.recordId must be non-empty text when provided")

    source_payload = _required_object(payload, "source", path)
    _reject_unknown(source_payload, {"id", "name", "locator"}, f"{path}.source")
    source = Source(
        id=_required_text(source_payload, "id", f"{path}.source"),
        name=_required_text(source_payload, "name", f"{path}.source"),
        locator=_required_text(source_payload, "locator", f"{path}.source"),
    )

    evidence_payload = _required_object(payload, "evidence", path)
    _reject_unknown(
        evidence_payload,
        {"id", "locator", "retrievedAt", "acquisitionMethod", "rawContentRef"},
        f"{path}.evidence",
    )
    evidence = RawEvidence(
        id=_required_text(evidence_payload, "id", f"{path}.evidence"),
        source_id=source.id,
        locator=_required_text(evidence_payload, "locator", f"{path}.evidence"),
        retrieved_at=_timestamp(
            _required_text(evidence_payload, "retrievedAt", f"{path}.evidence"),
            f"{path}.evidence.retrievedAt",
        ),
        acquisition_method=_required_text(
            evidence_payload,
            "acquisitionMethod",
            f"{path}.evidence",
        ),
        raw_content_ref=_required_text(
            evidence_payload,
            "rawContentRef",
            f"{path}.evidence",
        ),
    )

    vehicle_payload = _required_object(payload, "vehicle", path)
    _required_text(vehicle_payload, "make", f"{path}.vehicle")
    _required_text(vehicle_payload, "model", f"{path}.vehicle")

    return CatalogBatchEnvelope(
        record_id=record_id,
        vehicle=dict(vehicle_payload),
        source=source,
        evidence=evidence,
    )


def parse_catalog_batch_payload(payload: Any) -> tuple[CatalogBatchEnvelope, ...]:
    if not isinstance(payload, Mapping):
        raise ValueError("batch input must be an object")
    _reject_unknown(payload, {"records"}, "$")
    records = payload.get("records")
    if isinstance(records, (str, bytes)) or not isinstance(records, Sequence):
        raise ValueError("$.records must be an array")
    if not records:
        raise ValueError("$.records must contain at least one record")

    envelopes = tuple(
        catalog_batch_envelope_from_payload(record, index=index)
        for index, record in enumerate(records)
    )
    record_ids = [item.record_id for item in envelopes if item.record_id is not None]
    if len(record_ids) != len(set(record_ids)):
        raise ValueError("$.records recordId values must be unique")
    return envelopes


def _success_result(
    index: int,
    envelope: CatalogBatchEnvelope,
    result: CatalogIngestionResult,
) -> CatalogBatchRecordResult:
    return CatalogBatchRecordResult(
        index=index,
        record_id=envelope.record_id,
        ok=True,
        evidence_id=envelope.evidence.id,
        action=result.action,
        vehicle_id=result.vehicle_id,
        review_id=result.review_id,
    )


def _failure_snapshot(
    index: int,
    envelope: CatalogBatchEnvelope,
    error_message: str,
) -> CatalogBatchFailureSnapshot:
    return CatalogBatchFailureSnapshot(
        evidence_id=envelope.evidence.id,
        index=index,
        record_id=envelope.record_id,
        source_id=envelope.source.id,
        source_locator=envelope.source.locator,
        evidence_locator=envelope.evidence.locator,
        raw_content_ref=envelope.evidence.raw_content_ref,
        error_code=CATALOG_BATCH_RECORD_ERROR,
        error_message=error_message,
    )


def ingest_catalog_batch(
    store: CatalogStore,
    envelopes: Sequence[CatalogBatchEnvelope],
) -> CatalogBatchReport:
    results: list[CatalogBatchRecordResult] = []
    created = matched = review = failed = 0
    failure_store = CatalogBatchFailureStore(store)

    for index, envelope in enumerate(envelopes):
        if not isinstance(envelope, CatalogBatchEnvelope):
            raise ValueError("batch envelopes must be CatalogBatchEnvelope instances")
        try:
            result = ingest_catalog_record(
                store,
                envelope.vehicle,
                source=envelope.source,
                evidence=envelope.evidence,
            )
        except ValueError as exc:
            message = str(exc)
            with store.transaction():
                failure_store.save(_failure_snapshot(index, envelope, message))
            failed += 1
            results.append(
                CatalogBatchRecordResult(
                    index=index,
                    record_id=envelope.record_id,
                    ok=False,
                    evidence_id=envelope.evidence.id,
                    error_code=CATALOG_BATCH_RECORD_ERROR,
                    error_message=message,
                )
            )
            continue

        results.append(_success_result(index, envelope, result))
        if result.action is CatalogIngestionAction.CREATED:
            created += 1
        elif result.action is CatalogIngestionAction.MATCHED:
            matched += 1
        elif result.action is CatalogIngestionAction.REVIEW:
            review += 1
        else:
            raise RuntimeError(f"unsupported catalog ingestion action: {result.action!r}")

    succeeded = created + matched + review
    return CatalogBatchReport(
        total=len(envelopes),
        succeeded=succeeded,
        created=created,
        matched=matched,
        review=review,
        failed=failed,
        results=tuple(results),
    )


__all__ = [
    "CATALOG_BATCH_RECORD_ERROR",
    "CATALOG_BATCH_REPORT_SCHEMA",
    "CatalogBatchEnvelope",
    "CatalogBatchRecordResult",
    "CatalogBatchReport",
    "catalog_batch_envelope_from_payload",
    "ingest_catalog_batch",
    "parse_catalog_batch_payload",
]
