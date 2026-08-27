import hashlib
import unittest

from podium7.http_acquisition import DirectHttpAcquisition
from podium7.recurring_acquisition import (
    RecurringAcquisitionCoordinator,
    RecurringRunState,
    RecurringSourceContract,
    SourceTermsPin,
)
from podium7.source_policy import RobotsMode, SourceOperationPolicy


def acquisition(url, *, body=b'{"ok":true}', content_type="application/json", sha256=None, final_url=None):
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


class SourceTermsDriftTests(unittest.TestCase):
    locator = "https://vpic.nhtsa.dot.gov/api/x"

    def coordinator(self, *, terms_body=b"official terms v1"):
        pin = SourceTermsPin(
            locator="https://vpic.nhtsa.dot.gov/terms",
            expected_sha256=hashlib.sha256(terms_body).hexdigest(),
        )
        policy = SourceOperationPolicy(
            source_id="nhtsa_vpic",
            host="vpic.nhtsa.dot.gov",
            user_agent="Podium7/0.1",
            min_interval_seconds=0.0,
            robots_mode=RobotsMode.NOT_APPLICABLE,
        )
        contract = RecurringSourceContract(
            source_id="nhtsa_vpic",
            operation_policy=policy,
            expected_content_type="application/json",
            expected_schema_signature="decode-vin-values:v1",
            terms_pin=pin,
        )
        return RecurringAcquisitionCoordinator({"nhtsa_vpic": contract}), pin

    def authorize(self, coordinator):
        self.assertTrue(coordinator.authorize("nhtsa_vpic", self.locator, now=1.0).allowed)

    def test_matching_terms_allow_normal_success(self):
        coordinator, pin = self.coordinator()
        self.authorize(coordinator)
        result = coordinator.record_success(
            "nhtsa_vpic",
            acquisition(self.locator),
            schema_signature="decode-vin-values:v1",
            terms_acquisition=acquisition(pin.locator, body=b"official terms v1", content_type="text/plain"),
        )
        self.assertEqual(RecurringRunState.ACCEPTED, result.state)
        self.assertTrue(result.mutation_required)
        self.assertEqual(pin.expected_sha256, result.terms_sha256)

    def test_missing_or_changed_terms_require_review_without_mutation(self):
        coordinator, pin = self.coordinator()
        self.authorize(coordinator)
        missing = coordinator.record_success("nhtsa_vpic", acquisition(self.locator), schema_signature="decode-vin-values:v1")
        self.assertEqual(RecurringRunState.REVIEW_REQUIRED, missing.state)
        self.assertEqual("TERMS_EVIDENCE_UNAVAILABLE", missing.reason)
        self.assertFalse(missing.mutation_required)

        self.authorize(coordinator)
        changed = coordinator.record_success(
            "nhtsa_vpic",
            acquisition(self.locator),
            schema_signature="decode-vin-values:v1",
            terms_acquisition=acquisition(pin.locator, body=b"changed terms", content_type="text/plain"),
        )
        self.assertEqual(RecurringRunState.REVIEW_REQUIRED, changed.state)
        self.assertEqual("TERMS_DRIFT", changed.reason)
        self.assertFalse(changed.mutation_required)

    def test_terms_locator_final_locator_and_hash_are_exact(self):
        coordinator, pin = self.coordinator()
        self.authorize(coordinator)
        mismatch = coordinator.record_success(
            "nhtsa_vpic",
            acquisition(self.locator),
            schema_signature="decode-vin-values:v1",
            terms_acquisition=acquisition("https://vpic.nhtsa.dot.gov/other", body=b"official terms v1", content_type="text/plain"),
        )
        self.assertEqual("TERMS_LOCATOR_MISMATCH", mismatch.reason)

        self.authorize(coordinator)
        redirected = coordinator.record_success(
            "nhtsa_vpic",
            acquisition(self.locator),
            schema_signature="decode-vin-values:v1",
            terms_acquisition=acquisition(pin.locator, body=b"official terms v1", content_type="text/plain", final_url="https://vpic.nhtsa.dot.gov/terms-v2"),
        )
        self.assertEqual("TERMS_FINAL_LOCATOR_DRIFT", redirected.reason)

        self.authorize(coordinator)
        bad_hash = coordinator.record_success(
            "nhtsa_vpic",
            acquisition(self.locator),
            schema_signature="decode-vin-values:v1",
            terms_acquisition=acquisition(pin.locator, body=b"official terms v1", content_type="text/plain", sha256="0" * 64),
        )
        self.assertEqual("TERMS_HASH_MISMATCH", bad_hash.reason)

    def test_source_data_drift_has_precedence_over_terms_review(self):
        coordinator, _ = self.coordinator()
        self.authorize(coordinator)
        result = coordinator.record_success(
            "nhtsa_vpic",
            acquisition(self.locator, final_url="https://example.com/api/x"),
            schema_signature="decode-vin-values:v1",
            terms_acquisition=None,
        )
        self.assertEqual(RecurringRunState.DRIFT, result.state)
        self.assertEqual("FINAL_HOST_DRIFT", result.reason)

    def test_pin_validation_is_fail_closed(self):
        with self.assertRaises(ValueError):
            SourceTermsPin(locator="http://example.com/terms", expected_sha256="0" * 64)
        with self.assertRaises(ValueError):
            SourceTermsPin(locator="https://user:pass@example.com/terms", expected_sha256="0" * 64)
        with self.assertRaises(ValueError):
            SourceTermsPin(locator="https://example.com/terms#fragment", expected_sha256="0" * 64)
        with self.assertRaises(ValueError):
            SourceTermsPin(locator="https://example.com/terms", expected_sha256="not-a-digest")


if __name__ == "__main__":
    unittest.main()
