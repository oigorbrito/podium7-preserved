import unittest

from podium7.source_policy import RecurringSourceGate, RobotsMode, SourceOperationPolicy


class SourcePolicyTests(unittest.TestCase):
    def policy(self, **overrides):
        values = dict(source_id="example", host="example.com", user_agent="Podium7Bot", min_interval_seconds=2.0)
        values.update(overrides)
        return SourceOperationPolicy(**values)

    def test_requires_robots_when_configured(self):
        gate = RecurringSourceGate(self.policy())
        decision = gate.evaluate("https://example.com/cars", now=0)
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "ROBOTS_UNAVAILABLE")

    def test_respects_robots_disallow(self):
        gate = RecurringSourceGate(self.policy())
        robots = "User-agent: Podium7Bot\nDisallow: /private\n"
        decision = gate.evaluate("https://example.com/private/car", now=0, robots_text=robots)
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "ROBOTS_DISALLOW")

    def test_robots_crawl_delay_strengthens_host_pacing(self):
        gate = RecurringSourceGate(self.policy())
        robots = "User-agent: Podium7Bot\nAllow: /\nCrawl-delay: 5\n"
        first = gate.evaluate("https://example.com/a", now=0, robots_text=robots)
        second = gate.evaluate("https://example.com/b", now=4, robots_text=robots)
        third = gate.evaluate("https://example.com/c", now=5, robots_text=robots)
        self.assertTrue(first.allowed)
        self.assertEqual(first.effective_min_interval_seconds, 5.0)
        self.assertEqual(second.reason, "HOST_PACING")
        self.assertTrue(third.allowed)

    def test_request_rate_strengthens_host_pacing(self):
        gate = RecurringSourceGate(self.policy(min_interval_seconds=1.0))
        robots = "User-agent: Podium7Bot\nAllow: /\nRequest-rate: 2/10\n"
        first = gate.evaluate("https://example.com/a", now=0, robots_text=robots)
        second = gate.evaluate("https://example.com/b", now=4.9, robots_text=robots)
        self.assertTrue(first.allowed)
        self.assertEqual(first.effective_min_interval_seconds, 5.0)
        self.assertEqual(second.reason, "HOST_PACING")

    def test_not_applicable_mode_still_paces(self):
        gate = RecurringSourceGate(self.policy(robots_mode=RobotsMode.NOT_APPLICABLE))
        self.assertTrue(gate.evaluate("https://example.com/a", now=0).allowed)
        self.assertEqual(gate.evaluate("https://example.com/b", now=1).reason, "HOST_PACING")

    def test_rejects_wrong_host_and_non_https(self):
        gate = RecurringSourceGate(self.policy())
        self.assertEqual(gate.evaluate("http://example.com/a", now=0, robots_text="").reason, "INVALID_LOCATOR")
        self.assertEqual(gate.evaluate("https://other.example/a", now=0, robots_text="").reason, "HOST_MISMATCH")


if __name__ == "__main__":
    unittest.main()
