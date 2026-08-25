import hashlib
import unittest

from podium7.http_acquisition import DirectHttpAcquisition
from podium7.recurring_acquisition import RecurringAcquisitionCoordinator, RecurringRunState, RecurringSourceContract
from podium7.source_policy import RobotsMode, SourceOperationPolicy


def acquisition(url, body=b'{"ok":true}', content_type="application/json"):
    return DirectHttpAcquisition(
        requested_url=url,
        final_url=url,
        redirect_count=0,
        status=200,
        content_type=content_type,
        charset="utf-8",
        body=body,
        sha256=hashlib.sha256(body).hexdigest(),
    )


class RecurringAcquisitionTests(unittest.TestCase):
    def coordinator(self):
        policy = SourceOperationPolicy(
            source_id="nhtsa_vpic",
            host="vpic.nhtsa.dot.gov",
            user_agent="Podium7/0.1",
            min_interval_seconds=10.0,
            robots_mode=RobotsMode.NOT_APPLICABLE,
        )
        contract = RecurringSourceContract(
            source_id="nhtsa_vpic",
            operation_policy=policy,
            expected_content_type="application/json",
            expected_schema_signature="decode-vin-values:v1",
            max_retries=2,
        )
        return RecurringAcquisitionCoordinator({"nhtsa_vpic": contract})

    def test_unapproved_host_and_pacing_are_enforced_by_existing_gate(self):
        coordinator = self.coordinator()
        denied = coordinator.authorize("nhtsa_vpic", "https://example.com/x", now=1.0)
        self.assertFalse(denied.allowed)
        self.assertEqual("HOST_MISMATCH", denied.reason)
        first = coordinator.authorize("nhtsa_vpic", "https://vpic.nhtsa.dot.gov/api/x", now=10.0)
        self.assertTrue(first.allowed)
        second = coordinator.authorize("nhtsa_vpic", "https://vpic.nhtsa.dot.gov/api/y", now=15.0)
        self.assertFalse(second.allowed)
        self.assertEqual("HOST_PACING", second.reason)

    def test_identical_content_is_idempotent(self):
        coordinator = self.coordinator()
        item = acquisition("https://vpic.nhtsa.dot.gov/api/x")
        first = coordinator.record_success("nhtsa_vpic", item, schema_signature="decode-vin-values:v1")
        second = coordinator.record_success("nhtsa_vpic", item, schema_signature="decode-vin-values:v1")
        self.assertEqual(RecurringRunState.ACCEPTED, first.state)
        self.assertTrue(first.mutation_required)
        self.assertEqual(RecurringRunState.UNCHANGED, second.state)
        self.assertFalse(second.mutation_required)

    def test_schema_and_content_type_drift_fail_closed_without_mutation(self):
        coordinator = self.coordinator()
        schema_drift = coordinator.record_success("nhtsa_vpic", acquisition("https://vpic.nhtsa.dot.gov/api/x"), schema_signature="decode-vin-values:v2")
        self.assertEqual(RecurringRunState.DRIFT, schema_drift.state)
        self.assertFalse(schema_drift.mutation_required)
        media_drift = coordinator.record_success("nhtsa_vpic", acquisition("https://vpic.nhtsa.dot.gov/api/x", content_type="text/html"), schema_signature="decode-vin-values:v1")
        self.assertEqual("CONTENT_TYPE_DRIFT", media_drift.reason)
        self.assertFalse(media_drift.mutation_required)

    def test_failures_have_bounded_retry_then_degraded_state(self):
        coordinator = self.coordinator()
        locator = "https://vpic.nhtsa.dot.gov/api/x"
        first = coordinator.record_failure("nhtsa_vpic", locator, reason="TIMEOUT")
        second = coordinator.record_failure("nhtsa_vpic", locator, reason="TIMEOUT")
        third = coordinator.record_failure("nhtsa_vpic", locator, reason="TIMEOUT")
        self.assertEqual(RecurringRunState.RETRYABLE, first.state)
        self.assertEqual(RecurringRunState.RETRYABLE, second.state)
        self.assertEqual(RecurringRunState.DEGRADED, third.state)
        self.assertEqual(3, third.retry_count)
        self.assertFalse(third.mutation_required)

    def test_success_resets_failure_budget(self):
        coordinator = self.coordinator()
        locator = "https://vpic.nhtsa.dot.gov/api/x"
        coordinator.record_failure("nhtsa_vpic", locator, reason="NETWORK_ERROR")
        result = coordinator.record_success("nhtsa_vpic", acquisition(locator, body=b'{"v":1}'), schema_signature="decode-vin-values:v1")
        self.assertEqual(0, result.retry_count)
        after = coordinator.record_failure("nhtsa_vpic", locator, reason="NETWORK_ERROR")
        self.assertEqual(1, after.retry_count)


if __name__ == "__main__":
    unittest.main()
