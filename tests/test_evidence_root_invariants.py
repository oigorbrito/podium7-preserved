from datetime import datetime, timezone
import unittest

from podium7.domain import RawEvidence, Source


class EvidenceRootInvariantTests(unittest.TestCase):
    def test_source_requires_non_empty_identity_name_and_locator(self):
        invalid_sources = (
            ("", "Example", "https://example.test"),
            ("source-1", "", "https://example.test"),
            ("source-1", "Example", ""),
        )
        for source_id, name, locator in invalid_sources:
            with self.subTest(source_id=source_id, name=name, locator=locator):
                with self.assertRaises(ValueError):
                    Source(source_id, name, locator)

    def test_raw_evidence_requires_non_empty_fields_and_timezone(self):
        valid = {
            "id": "evidence-1",
            "source_id": "source-1",
            "locator": "https://example.test/evidence",
            "retrieved_at": datetime(2026, 8, 19, tzinfo=timezone.utc),
            "acquisition_method": "structured-import",
            "raw_content_ref": "sha256:abc@fixture",
        }
        for field in ("id", "source_id", "locator", "acquisition_method", "raw_content_ref"):
            invalid = dict(valid)
            invalid[field] = ""
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    RawEvidence(**invalid)

        naive = dict(valid)
        naive["retrieved_at"] = datetime(2026, 8, 19)
        with self.assertRaises(ValueError):
            RawEvidence(**naive)


if __name__ == "__main__":
    unittest.main()
