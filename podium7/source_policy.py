from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

from .autonomy import RateLimiter


class RobotsMode(str, Enum):
    REQUIRED = "REQUIRED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


@dataclass(frozen=True)
class SourceOperationPolicy:
    source_id: str
    host: str
    user_agent: str
    min_interval_seconds: float
    robots_mode: RobotsMode = RobotsMode.REQUIRED

    def __post_init__(self) -> None:
        if not self.source_id.strip() or not self.host.strip() or not self.user_agent.strip():
            raise ValueError("source_id, host, and user_agent are required")
        if self.min_interval_seconds < 0:
            raise ValueError("min_interval_seconds cannot be negative")


@dataclass(frozen=True)
class SourceOperationDecision:
    allowed: bool
    reason: str
    effective_min_interval_seconds: float


class RecurringSourceGate:
    def __init__(self, policy: SourceOperationPolicy) -> None:
        self.policy = policy
        self._rate_limiter = RateLimiter(policy.min_interval_seconds)

    def evaluate(self, locator: str, *, now: float, robots_text: str | None = None) -> SourceOperationDecision:
        parsed = urlparse(locator)
        if parsed.scheme != "https" or parsed.hostname is None:
            return SourceOperationDecision(False, "INVALID_LOCATOR", self.policy.min_interval_seconds)
        if parsed.hostname.casefold() != self.policy.host.casefold():
            return SourceOperationDecision(False, "HOST_MISMATCH", self.policy.min_interval_seconds)

        effective_interval = self.policy.min_interval_seconds
        if self.policy.robots_mode is RobotsMode.REQUIRED:
            if robots_text is None:
                return SourceOperationDecision(False, "ROBOTS_UNAVAILABLE", effective_interval)
            parser = RobotFileParser()
            parser.set_url(f"https://{self.policy.host}/robots.txt")
            parser.parse(robots_text.splitlines())
            if not parser.can_fetch(self.policy.user_agent, locator):
                return SourceOperationDecision(False, "ROBOTS_DISALLOW", effective_interval)
            crawl_delay = parser.crawl_delay(self.policy.user_agent)
            if crawl_delay is not None:
                effective_interval = max(effective_interval, float(crawl_delay))
            request_rate = parser.request_rate(self.policy.user_agent)
            if request_rate is not None and request_rate.requests > 0:
                effective_interval = max(effective_interval, request_rate.seconds / request_rate.requests)

        if effective_interval != self._rate_limiter.min_interval_seconds:
            self._rate_limiter.min_interval_seconds = effective_interval
        if not self._rate_limiter.allow(self.policy.host.casefold(), now):
            return SourceOperationDecision(False, "HOST_PACING", effective_interval)
        return SourceOperationDecision(True, "ALLOW", effective_interval)
