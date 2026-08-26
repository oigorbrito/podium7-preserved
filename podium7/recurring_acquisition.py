from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
from typing import Mapping
from urllib.parse import urlparse

from .http_acquisition import DirectHttpAcquisition
from .source_policy import RecurringSourceGate, SourceOperationDecision, SourceOperationPolicy


class RecurringRunState(str, Enum):
    ACCEPTED = "ACCEPTED"
    UNCHANGED = "UNCHANGED"
    DRIFT = "DRIFT"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    DEGRADED = "DEGRADED"
    RETRYABLE = "RETRYABLE"


@dataclass(frozen=True)
class SourceTermsPin:
    locator: str
    expected_sha256: str

    def __post_init__(self) -> None:
        parsed = urlparse(self.locator)
        if parsed.scheme.casefold() != "https" or not parsed.hostname:
            raise ValueError("terms locator must be an HTTPS URL")
        digest = self.expected_sha256.casefold()
        if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
            raise ValueError("expected_sha256 must be a SHA-256 hex digest")
        object.__setattr__(self, "expected_sha256", digest)


@dataclass(frozen=True)
class RecurringSourceContract:
    source_id: str
    operation_policy: SourceOperationPolicy
    expected_content_type: str
    expected_schema_signature: str
    max_retries: int = 2
    terms_pin: SourceTermsPin | None = None

    def __post_init__(self) -> None:
        if self.source_id != self.operation_policy.source_id:
            raise ValueError("source contract and operation policy source_id must match")
        if not self.expected_content_type or "/" not in self.expected_content_type:
            raise ValueError("expected_content_type is required")
        if not self.expected_schema_signature.strip():
            raise ValueError("expected_schema_signature is required")
        if isinstance(self.max_retries, bool) or not isinstance(self.max_retries, int) or self.max_retries < 0:
            raise ValueError("max_retries must be a non-negative integer")


@dataclass(frozen=True)
class RecurringCheckpoint:
    last_sha: dict[str, str]
    retry_counts: dict[str, int]

    def __post_init__(self) -> None:
        normalized_last_sha: dict[str, str] = {}
        for key, value in self.last_sha.items():
            if not isinstance(key, str) or not key.strip() or not isinstance(value, str):
                raise ValueError("checkpoint last_sha entries must contain source ids and SHA-256 hex digests")
            digest = value.casefold()
            if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
                raise ValueError("checkpoint last_sha entries must contain source ids and SHA-256 hex digests")
            normalized_last_sha[key] = digest
        object.__setattr__(self, "last_sha", normalized_last_sha)
        if any(not isinstance(key, str) or not key.strip() or isinstance(value, bool) or not isinstance(value, int) or value < 0 for key, value in self.retry_counts.items()):
            raise ValueError("checkpoint retry_counts must contain non-negative integers")

    def to_dict(self) -> dict[str, dict[str, object]]:
        return {
            "lastSha": dict(sorted(self.last_sha.items())),
            "retryCounts": dict(sorted(self.retry_counts.items())),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "RecurringCheckpoint":
        if not isinstance(payload, Mapping):
            raise ValueError("checkpoint payload must be an object")
        raw_last = payload.get("lastSha", {})
        raw_retry = payload.get("retryCounts", {})
        if not isinstance(raw_last, Mapping) or not isinstance(raw_retry, Mapping):
            raise ValueError("checkpoint maps are required")
        return cls(last_sha=dict(raw_last), retry_counts=dict(raw_retry))  # type: ignore[arg-type]


@dataclass(frozen=True)
class RecurringRunResult:
    source_id: str
    state: RecurringRunState
    reason: str
    locator: str
    sha256: str | None
    schema_signature: str | None
    retry_count: int
    mutation_required: bool
    terms_locator: str | None = None
    terms_sha256: str | None = None


class RecurringAcquisitionCoordinator:
    def __init__(self, contracts: Mapping[str, RecurringSourceContract], *, checkpoint: RecurringCheckpoint | None = None) -> None:
        if not contracts:
            raise ValueError("at least one recurring source contract is required")
        self._contracts = dict(contracts)
        if set(self._contracts) != {contract.source_id for contract in self._contracts.values()}:
            raise ValueError("contract mapping keys must match source ids")
        self._gates = {source_id: RecurringSourceGate(contract.operation_policy) for source_id, contract in self._contracts.items()}
        checkpoint = checkpoint or RecurringCheckpoint({}, {})
        unknown = (set(checkpoint.last_sha) | set(checkpoint.retry_counts)) - set(self._contracts)
        if unknown:
            raise ValueError("checkpoint references unapproved sources: " + ", ".join(sorted(unknown)))
        self._last_sha = dict(checkpoint.last_sha)
        self._retry_counts = dict(checkpoint.retry_counts)
        self._authorized_locators: dict[str, str] = {}

    def checkpoint(self) -> RecurringCheckpoint:
        return RecurringCheckpoint(dict(self._last_sha), dict(self._retry_counts))

    def authorize(self, source_id: str, locator: str, *, now: float, robots_text: str | None = None) -> SourceOperationDecision:
        gate = self._gates.get(source_id)
        if gate is None:
            return SourceOperationDecision(False, "UNAPPROVED_SOURCE", 0.0)
        decision = gate.evaluate(locator, now=now, robots_text=robots_text)
        if decision.allowed:
            self._authorized_locators[source_id] = locator
        return decision

    def _consume_authorization(self, source_id: str, requested_url: str) -> str | None:
        authorized_locator = self._authorized_locators.pop(source_id, None)
        if authorized_locator is None:
            return "AUTHORIZATION_MISSING"
        if requested_url != authorized_locator:
            return "AUTHORIZED_LOCATOR_MISMATCH"
        return None

    def record_success(
        self,
        source_id: str,
        acquisition: DirectHttpAcquisition,
        *,
        schema_signature: str,
        terms_acquisition: DirectHttpAcquisition | None = None,
    ) -> RecurringRunResult:
        contract = self._contracts.get(source_id)
        if contract is None:
            raise ValueError("source is not approved for recurring acquisition")
        if not isinstance(schema_signature, str) or not schema_signature.strip():
            raise ValueError("schema_signature is required")
        authorization_error = self._consume_authorization(source_id, acquisition.requested_url)
        if authorization_error is not None:
            return RecurringRunResult(source_id, RecurringRunState.DRIFT, authorization_error, acquisition.requested_url, acquisition.sha256, schema_signature, self._retry_counts.get(source_id, 0), False)

        terms_locator = None
        terms_sha256 = None
        if contract.terms_pin is not None:
            terms_locator = contract.terms_pin.locator
            if terms_acquisition is None:
                return RecurringRunResult(source_id, RecurringRunState.REVIEW_REQUIRED, "TERMS_EVIDENCE_UNAVAILABLE", acquisition.final_url, acquisition.sha256, schema_signature, self._retry_counts.get(source_id, 0), False, terms_locator, None)
            if terms_acquisition.requested_url != contract.terms_pin.locator:
                return RecurringRunResult(source_id, RecurringRunState.REVIEW_REQUIRED, "TERMS_LOCATOR_MISMATCH", acquisition.final_url, acquisition.sha256, schema_signature, self._retry_counts.get(source_id, 0), False, terms_acquisition.requested_url, terms_acquisition.sha256)
            if terms_acquisition.final_url != contract.terms_pin.locator:
                return RecurringRunResult(source_id, RecurringRunState.REVIEW_REQUIRED, "TERMS_FINAL_LOCATOR_DRIFT", acquisition.final_url, acquisition.sha256, schema_signature, self._retry_counts.get(source_id, 0), False, terms_acquisition.final_url, terms_acquisition.sha256)
            actual_terms_sha = hashlib.sha256(terms_acquisition.body).hexdigest()
            terms_sha256 = actual_terms_sha
            if actual_terms_sha != terms_acquisition.sha256:
                return RecurringRunResult(source_id, RecurringRunState.REVIEW_REQUIRED, "TERMS_HASH_MISMATCH", acquisition.final_url, acquisition.sha256, schema_signature, self._retry_counts.get(source_id, 0), False, terms_locator, terms_acquisition.sha256)
            if actual_terms_sha != contract.terms_pin.expected_sha256:
                return RecurringRunResult(source_id, RecurringRunState.REVIEW_REQUIRED, "TERMS_DRIFT", acquisition.final_url, acquisition.sha256, schema_signature, self._retry_counts.get(source_id, 0), False, terms_locator, actual_terms_sha)

        final_host = urlparse(acquisition.final_url).hostname
        if final_host is None or final_host.casefold() != contract.operation_policy.host.casefold():
            return RecurringRunResult(source_id, RecurringRunState.DRIFT, "FINAL_HOST_DRIFT", acquisition.final_url, acquisition.sha256, schema_signature, self._retry_counts.get(source_id, 0), False, terms_locator, terms_sha256)
        actual_sha = hashlib.sha256(acquisition.body).hexdigest()
        if actual_sha != acquisition.sha256:
            return RecurringRunResult(source_id, RecurringRunState.DRIFT, "CONTENT_HASH_MISMATCH", acquisition.final_url, acquisition.sha256, schema_signature, self._retry_counts.get(source_id, 0), False, terms_locator, terms_sha256)
        if acquisition.content_type != contract.expected_content_type:
            return RecurringRunResult(source_id, RecurringRunState.DRIFT, "CONTENT_TYPE_DRIFT", acquisition.final_url, acquisition.sha256, schema_signature, self._retry_counts.get(source_id, 0), False, terms_locator, terms_sha256)
        if schema_signature != contract.expected_schema_signature:
            return RecurringRunResult(source_id, RecurringRunState.DRIFT, "SCHEMA_DRIFT", acquisition.final_url, acquisition.sha256, schema_signature, self._retry_counts.get(source_id, 0), False, terms_locator, terms_sha256)

        prior = self._last_sha.get(source_id)
        self._retry_counts[source_id] = 0
        if prior == acquisition.sha256:
            return RecurringRunResult(source_id, RecurringRunState.UNCHANGED, "IDENTICAL_CONTENT", acquisition.final_url, acquisition.sha256, schema_signature, 0, False, terms_locator, terms_sha256)
        self._last_sha[source_id] = acquisition.sha256
        return RecurringRunResult(source_id, RecurringRunState.ACCEPTED, "NEW_VALID_CONTENT", acquisition.final_url, acquisition.sha256, schema_signature, 0, True, terms_locator, terms_sha256)

    def record_failure(self, source_id: str, locator: str, *, reason: str) -> RecurringRunResult:
        contract = self._contracts.get(source_id)
        if contract is None:
            raise ValueError("source is not approved for recurring acquisition")
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("failure reason is required")
        self._authorized_locators.pop(source_id, None)
        count = self._retry_counts.get(source_id, 0) + 1
        self._retry_counts[source_id] = count
        state = RecurringRunState.RETRYABLE if count <= contract.max_retries else RecurringRunState.DEGRADED
        return RecurringRunResult(source_id, state, reason.strip(), locator, None, None, count, False)

    def reset_failures(self, source_id: str) -> None:
        if source_id not in self._contracts:
            raise ValueError("source is not approved for recurring acquisition")
        self._retry_counts[source_id] = 0


__all__ = [
    "RecurringAcquisitionCoordinator",
    "RecurringCheckpoint",
    "RecurringRunResult",
    "RecurringRunState",
    "RecurringSourceContract",
    "SourceTermsPin",
]
