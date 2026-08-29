import json
import unittest
from pathlib import Path


class InmetroPdfExtractionGoldTests(unittest.TestCase):
    def test_gold_subset_is_hash_bound_but_remote_bytes_remain_unresolved(self):
        path = Path("benchmarks/inmetro_pbev_pdf_extraction_v1.json")
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual("RAW_SNAPSHOT_BOUND", payload["status"])
        self.assertEqual(
            "cb8ab26789b75a596f75ebf5f6454f30950d31ff8fff1de99ad56a502679db2b",
            payload["source"]["rawContentSha256"],
        )
        self.assertEqual("REMOTE_BYTES_UNRESOLVED", payload["source"]["snapshotRetrievability"])
        self.assertIsNone(payload["source"]["snapshotLocator"])
        self.assertEqual(3, len(payload["cases"]))
        self.assertTrue(payload["source"]["documentLocator"].startswith("https://www.gov.br/inmetro/"))

    def test_gold_subset_uses_only_explicitly_inspected_fields(self):
        path = Path("benchmarks/inmetro_pbev_pdf_extraction_v1.json")
        payload = json.loads(path.read_text(encoding="utf-8"))
        allowed = set(payload["fields"])
        for case in payload["cases"]:
            self.assertEqual(allowed, set(case["expected"]))
            self.assertTrue(case["evidenceLocator"].startswith("documentPage=1"))


if __name__ == "__main__":
    unittest.main()
