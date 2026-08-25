from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping

from .http_acquisition import DirectHttpAcquisition
from .source_policy import RecurringSourceGate, SourceOperationDecision, SourceOperationPolicy


class RecurringRunState(str, Enum):
    ACCEPTED = "ACCEPTED"
    UNCHANGED = "UNCHANGED"
    DRIFT = "DRIFT"
    DEGRADED = "DEGRADED"
    RETRYABLE = "RETRYABLE"


@dataclass(frozen=True)
class RecurringSourceContract:
    source_id: str
    operation_policy: SourceOperationPolicy
    expected_content_type: str
    expected_schema_signature: str
    max_retries: int = 2

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
class RecurringRunResult:
    source_id: str
    state: RecurringRunState
    reason: str
    locator: str
    sha256: str | None
    schema_signature: str | None
    retry_count: int
    mutation_required: bool


class RecurringAcquisitionCoordinator:
    def __init__(self, contracts: Mapping[str, RecurringSourceContract]) -> None:
        if not contracts:
            raise ValueError("at least one recurring source contract is required")
        self._contracts = dict(contracts)
        if set(self._contracts) != {contract.source_id for contract in self._contracts.values()}:
            raise ValueError("contract mapping keys must match source ids")
        self._gates = {source_id: RecurringSourceGate(contract.operation_policy) for source_id, contract in self._contracts.items()}
        self._last_sha: dict[str, str] = {}
        self._retry_counts: dict[str, int] = {}

    def authorize(self, source_id: str, locator: str, *, now: float, robots_text: str | None = None) -> SourceOperationDecision:
        gate = self._gates.get(source_id)
        if gate is None:
            return SourceOperationDecision(False, "UNAPPROVED_SOURCE", 0.0)
        return gate.evaluate(locator, now=now, robots_text=robots_text)

    def record_success(self, source_id: str, acquisition: DirectHttpAcquisition, *, schema_signature: str) -> RecurringRunResult:
        contract = self._contracts.get(source_id)
        if contract is None:
            raise ValueError("source is not approved for recurring acquisition")
        if acquisition.content_type != contract.expected_content_type:
            return RecurringRunResult(source_id, RecurringRunState.DRIFT, "CONTENT_TYPE_DRIFT", acquisition.final_url, acquisition.sha256, schema_signature, self._retry_counts.get(source_id, 0), False)
        if schema_signature != contract.expected_schema_signature:
            return RecurringRunResult(source_id, RecurringRunState.DRIFT, "SCHEMA_DRIFT", acquisition.final_url, acquisition.sha256, schema_signature, self._retry_counts.get(source_id, 0), False)

        prior = self._last_sha.get(source_id)
        self._retry_counts[source_id] = 0
        if prior == acquisition.sha256:
            return RecurringRunResult(source_id, RecurringRunState.UNCHANGED, "IDENTICAL_CONTENT", acquisition.final_url, acquisition.sha256, schema_signature, 0, False)
        self._last_sha[source_id] = acquisition.sha256
        return RecurringRunResult(source_id, RecurringRunState.ACCEPTED, "NEW_VALID_CONTENT", acquisition.final_url, acquisition.sha256, schema_signature, 0, True)

    def record_failure(self, source_id: str, locator: str, *, reason: str) -> RecurringRunResult:
        contract = self._contracts.get(source_id)
        if contract is None:
            raise ValueError("source is not approved for recurring acquisition")
        count = self._retry_counts.get(source_id, 0) + 1
        self._retry_counts[source_id] = count
        if count <= contract.max_retries:
            state = RecurringRunState.RETRYABLE
            mutation_required = False
        else:
            state = RecurringRunState.DEGRADED
            mutation_required = False
        return RecurringRunResult(source_id, state, reason, locator, None, None, count, mutation_required)

    def reset_failures(self, source_id: str) -> None:
        if source_id not in self._contracts:
            raise ValueError("source is not approved for recurring acquisition")
        self._retry_counts[source_id] = 0


__all__ = ["RecurringAcquisitionCoordinator", "RecurringRunResult", "RecurringRunState", "RecurringSourceContract"]
