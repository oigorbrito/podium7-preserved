from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Generic, TypeVar


T = TypeVar("T")


class JobState(str, Enum):
    PENDING = "PENDING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


@dataclass(frozen=True)
class EnrichmentJob:
    id: str
    entity_id: str
    attribute: str
    source_id: str


@dataclass(frozen=True)
class JobResult(Generic[T]):
    state: JobState
    attempts: int
    value: T | None = None
    error: str | None = None


@dataclass
class Checkpoint:
    completed_jobs: set[str] = field(default_factory=set)
    failed_attempts: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")


class RateLimiter:
    def __init__(self, min_interval_seconds: float) -> None:
        if min_interval_seconds < 0:
            raise ValueError("min_interval_seconds cannot be negative")
        self.min_interval_seconds = min_interval_seconds
        self._last_call: dict[str, float] = {}

    def allow(self, source_id: str, now: float) -> bool:
        previous = self._last_call.get(source_id)
        if previous is not None and now - previous < self.min_interval_seconds:
            return False
        self._last_call[source_id] = now
        return True


class AcquisitionCache(Generic[T]):
    def __init__(self) -> None:
        self._items: dict[tuple[str, str], T] = {}

    def get(self, source_id: str, locator: str) -> T | None:
        return self._items.get((source_id, locator))

    def put(self, source_id: str, locator: str, value: T) -> None:
        self._items[(source_id, locator)] = value


def identify_gaps(required_attributes: set[str], available_attributes: set[str]) -> tuple[str, ...]:
    return tuple(sorted(required_attributes - available_attributes))


def plan_jobs(entity_id: str, gaps: tuple[str, ...], source_id: str) -> tuple[EnrichmentJob, ...]:
    return tuple(
        EnrichmentJob(
            id=f"{entity_id}:{source_id}:{attribute}",
            entity_id=entity_id,
            attribute=attribute,
            source_id=source_id,
        )
        for attribute in gaps
    )


def run_job(
    job: EnrichmentJob,
    worker: Callable[[EnrichmentJob], T],
    *,
    checkpoint: Checkpoint,
    retry_policy: RetryPolicy = RetryPolicy(),
) -> JobResult[T]:
    if job.id in checkpoint.completed_jobs:
        return JobResult(JobState.SUCCEEDED, 0, None, None)

    last_error: str | None = None
    for attempt in range(1, retry_policy.max_attempts + 1):
        try:
            value = worker(job)
        except Exception as exc:  # boundary: acquisition/extraction worker failure
            last_error = f"{type(exc).__name__}: {exc}"
            checkpoint.failed_attempts[job.id] = attempt
            continue
        checkpoint.completed_jobs.add(job.id)
        checkpoint.failed_attempts.pop(job.id, None)
        return JobResult(JobState.SUCCEEDED, attempt, value, None)

    return JobResult(JobState.FAILED, retry_policy.max_attempts, None, last_error)
