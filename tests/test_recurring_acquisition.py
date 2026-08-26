import hashlib
import unittest

from podium7.http_acquisition import DirectHttpAcquisition
from podium7.recurring_acquisition import (
    RecurringAcquisitionCoordinator,
    RecurringCheckpoint,
    RecurringRunState,
    RecurringSourceContract,
)
from podium7.source_policy import RobotsMode, SourceOperationPolicy


def acquisition(url, body=b'{"ok":true}', content_type="application/json", sha256=None, final_url=None):
    return DirectHttpAcquisition(
        requested_url=url,
        final_url=final_url or url,
        redirect_count=0 if final_url in (None, url) else 1,
        status=200,
        content_type=content_type,
        charset="utf-8",
        body=body,
        sha256=sha256 or hashlib.sha256(body).hexdigest(),
    )


class RecurringAcquisitionTests(unittest.TestCase):
    def contract(self):
        policy = SourceOperationPolicy(source_id="nhtsa_vpic", host="vpic.nhtsa.dot.gov", user_agent="Podium7/0.1", min_interval_seconds=10.0, robots_mode=RobotsMode.NOT_APPLICABLE)
        return RecurringSourceContract(source_id="nhtsa_vpic", operation_policy=policy, expected_content_type="application/json", expected_schema_signature="decode-vin-values:v1", max_retries=2)

    def coordinator(self, checkpoint=None):
        return RecurringAcquisitionCoordinator({"nhtsa_vpic": self.contract()}, checkpoint=checkpoint)

    def authorize(self, coordinator, locator, now=10.0):
        decision = coordinator.authorize("nhtsa_vpic", locator, now=now)
        self.assertTrue(decision.allowed)

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

    def test_success_requires_matching_one_shot_authorization(self):
        coordinator = self.coordinator()
        locator = "https://vpic.nhtsa.dot.gov/api/x"
        missing = coordinator.record_success("nhtsa_vpic", acquisition(locator), schema_signature="decode-vin-values:v1")
        self.assertEqual(RecurringRunState.DRIFT, missing.state)
        self.assertEqual("AUTHORIZATION_MISSING", missing.reason)
        self.assertFalse(missing.mutation_required)

        self.authorize(coordinator, locator, now=20.0)
        mismatch = coordinator.record_success(
            "nhtsa_vpic",
            acquisition("https://vpic.nhtsa.dot.gov/api/y"),
            schema_signature="decode-vin-values:v1",
        )
        self.assertEqual(RecurringRunState.DRIFT, mismatch.state)
        self.assertEqual("AUTHORIZED_LOCATOR_MISMATCH", mismatch.reason)
        self.assertFalse(mismatch.mutation_required)

        consumed = coordinator.record_success("nhtsa_vpic", acquisition(locator), schema_signature="decode-vin-values:v1")
        self.assertEqual("AUTHORIZATION_MISSING", consumed.reason)

    def test_identical_content_is_idempotent_across_persisted_checkpoint(self):
        coordinator = self.coordinator()
        locator = "https://vpic.nhtsa.dot.gov/api/x"
        item = acquisition(locator)
        self.authorize(coordinator, locator, now=10.0)
        first = coordinator.record_success("nhtsa_vpic", item, schema_signature="decode-vin-values:v1")
        checkpoint_payload = coordinator.checkpoint().to_dict()
        restored = self.coordinator(RecurringCheckpoint.from_dict(checkpoint_payload))
        self.authorize(restored, locator, now=10.0)
        second = restored.record_success("nhtsa_vpic", item, schema_signature="decode-vin-values:v1")
        self.assertEqual(RecurringRunState.ACCEPTED, first.state)
        self.assertTrue(first.mutation_required)
        self.assertEqual(RecurringRunState.UNCHANGED, second.state)
        self.assertFalse(second.mutation_required)

    def test_checkpoint_rejects_non_hex_sha256_value(self):
        with self.assertRaisesRegex(ValueError, "SHA-256 hex digests"):
            RecurringCheckpoint({"nhtsa_vpic": "z" * 64}, {})

    def test_schema_content_host_and_hash_drift_fail_closed(self):
        coordinator = self.coordinator()
        locator = "https://vpic.nhtsa.dot.gov/api/x"

        self.authorize(coordinator, locator, now=10.0)
        schema_drift = coordinator.record_success("nhtsa_vpic", acquisition(locator), schema_signature="decode-vin-values:v2")
        self.authorize(coordinator, locator, now=20.0)
        media_drift = coordinator.record_success("nhtsa_vpic", acquisition(locator, content_type="text/html"), schema_signature="decode-vin-values:v1")
        self.authorize(coordinator, locator, now=30.0)
        host_drift = coordinator.record_success(
            "nhtsa_vpic",
            acquisition(locator, final_url="https://example.com/api/x"),
            schema_signature="decode-vin-values:v1",
        )
        self.authorize(coordinator, locator, now=40.0)
        hash_drift = coordinator.record_success("nhtsa_vpic", acquisition(locator, sha256="0" * 64), schema_signature="decode-vin-values:v1")
        self.assertEqual("SCHEMA_DRIFT", schema_drift.reason)
        self.assertEqual("CONTENT_TYPE_DRIFT", media_drift.reason)
        self.assertEqual("FINAL_HOST_DRIFT", host_drift.reason)
        self.assertEqual("CONTENT_HASH_MISMATCH", hash_drift.reason)
        for result in (schema_drift, media_drift, host_drift, hash_drift):
            self.assertEqual(RecurringRunState.DRIFT, result.state)
            self.assertFalse(result.mutation_required)

    def test_failures_have_bounded_retry_then_degraded_state(self):
        coordinator = self.coordinator()
        locator = "https://vpic.nhtsa.dot.gov/api/x"
        first = coordinator.record_failure("nhtsa_vpic", locator, reason="TIMEOUT")
        second = coordinator.record_failure("nhtsa_vpic", locator, reason="TIMEOUT")
        checkpoint = coordinator.checkpoint()
        restored = self.coordinator(checkpoint)
        third = restored.record_failure("nhtsa_vpic", locator, reason="TIMEOUT")
        self.assertEqual(RecurringRunState.RETRYABLE, first.state)
        self.assertEqual(RecurringRunState.RETRYABLE, second.state)
        self.assertEqual(RecurringRunState.DEGRADED, third.state)
        self.assertEqual(3, third.retry_count)
        self.assertFalse(third.mutation_required)

    def test_failure_consumes_pending_authorization(self):
        coordinator = self.coordinator()
        locator = "https://vpic.nhtsa.dot.gov/api/x"
        self.authorize(coordinator, locator, now=10.0)
        coordinator.record_failure("nhtsa_vpic", locator, reason="TIMEOUT")
        result = coordinator.record_success("nhtsa_vpic", acquisition(locator), schema_signature="decode-vin-values:v1")
        self.assertEqual("AUTHORIZATION_MISSING", result.reason)

    def test_success_resets_failure_budget(self):
        coordinator = self.coordinator()
        locator = "https://vpic.nhtsa.dot.gov/api/x"
        coordinator.record_failure("nhtsa_vpic", locator, reason="NETWORK_ERROR")
        self.authorize(coordinator, locator, now=10.0)
        result = coordinator.record_success("nhtsa_vpic", acquisition(locator, body=b'{"v":1}'), schema_signature="decode-vin-values:v1")
        self.assertEqual(0, result.retry_count)
        after = coordinator.record_failure("nhtsa_vpic", locator, reason="NETWORK_ERROR")
        self.assertEqual(1, after.retry_count)


if __name__ == "__main__":
    unittest.main()
