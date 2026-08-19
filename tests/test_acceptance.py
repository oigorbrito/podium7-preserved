import json
import unittest
from pathlib import Path

from podium7.acceptance import run_acceptance_slice
from podium7.identity import MatchOutcome


class AcceptanceTests(unittest.TestCase):
    def test_real_multi_source_vertical_slice(self):
        report = run_acceptance_slice(
            Path("data/raw/vehicle-makes-models/artega.json"),
            Path("data/raw/web/autoevolution-artega-gt-2010.txt"),
        )
        self.assertEqual(report.identity_outcome, MatchOutcome.MATCH)
        self.assertEqual(report.sources, 2)
        self.assertEqual(report.raw_evidence, 3)
        self.assertEqual(report.canonical_facts, 12)
        self.assertEqual(report.conflicts, 0)
        exported = json.loads(report.exported_json)
        self.assertEqual(exported["entity"]["make"], "Artega")
        self.assertEqual(exported["quality"]["canonicalFactCount"], 12)


if __name__ == "__main__":
    unittest.main()
