import hashlib
import json
import unittest
from pathlib import Path


class InmetroPdfExtractionGoldTests(unittest.TestCase):
    def test_gold_subset_is_bound_to_retrievable_repository_bytes(self):
        path = Path("benchmarks/inmetro_pbev_pdf_extraction_v1.json")
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual("RAW_SNAPSHOT_BOUND", payload["status"])
        expected_sha = "cb8ab26789b75a596f75ebf5f6454f30950d31ff8fff1de99ad56a502679db2b"
        self.assertEqual(expected_sha, payload["source"]["rawContentSha256"])
        self.assertEqual("REPOSITORY_FIXTURE", payload["source"]["snapshotRetrievability"])
        fixture = Path(payload["source"]["snapshotLocator"])
        self.assertTrue(fixture.is_file())
        self.assertEqual(expected_sha, hashlib.sha256(fixture.read_bytes()).hexdigest())
        self.assertEqual(615533, fixture.stat().st_size)
        self.assertEqual(3, len(payload["cases"]))
        self.assertTrue(payload["source"]["documentLocator"].startswith("https://www.gov.br/inmetro/"))

    def test_bound_fixture_metadata_matches_gold(self):
        gold = json.loads(Path("benchmarks/inmetro_pbev_pdf_extraction_v1.json").read_text(encoding="utf-8"))
        fixture = Path(gold["source"]["snapshotLocator"])
        metadata_path = fixture.with_suffix(".json")
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        self.assertEqual(fixture.as_posix(), metadata["fixturePath"])
        self.assertEqual(gold["source"]["rawContentSha256"], metadata["sha256"])
        self.assertEqual(fixture.stat().st_size, metadata["bytes"])
        self.assertEqual(gold["source"]["documentLocator"], metadata["documentLocator"])

    def test_gold_subset_uses_only_explicitly_inspected_fields(self):
        path = Path("benchmarks/inmetro_pbev_pdf_extraction_v1.json")
        payload = json.loads(path.read_text(encoding="utf-8"))
        allowed = set(payload["fields"])
        for case in payload["cases"]:
            self.assertEqual(allowed, set(case["expected"]))
            self.assertTrue(case["evidenceLocator"].startswith("documentPage=1"))


if __name__ == "__main__":
    unittest.main()
