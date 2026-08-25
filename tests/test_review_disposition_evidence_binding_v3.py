from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import unittest

from podium7.review_disposition import evaluate_review_dispositions


ROOT = Path(__file__).resolve().parents[1]
DATASETS = (
    ROOT / "benchmarks" / "catalog_identity_golden_v1.json",
    ROOT / "benchmarks" / "catalog_identity_golden_br_v1.json",
    ROOT / "benchmarks" / "catalog_identity_br_adjacent_incomplete_v1.json",
)
ENRICHMENT_V3 = ROOT / "benchmarks" / "source_backed_enrichment_v3.json"
DISPOSITIONS = ROOT / "benchmarks" / "review_disposition_v2.json"


class ReviewDispositionEvidenceBindingV3Tests(unittest.TestCase):
    def test_stale_evidence_id_is_both_unused_and_current_item_unassessed(self) -> None:
        payload = json.loads(DISPOSITIONS.read_text(encoding="utf-8"))
        decision = payload["decisions"][0]
        side = decision["sides"][0]
        current_evidence_id = decision["evidenceIdsBySide"][side]
        stale_evidence_id = current_evidence_id + ":stale"
        decision["evidenceIdsBySide"][side] = stale_evidence_id

        handle = tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            suffix=".json",
            delete=False,
        )
        try:
            json.dump(payload, handle)
            handle.close()
            report = evaluate_review_dispositions(
                DATASETS,
                ENRICHMENT_V3,
                handle.name,
            )
        finally:
            if not handle.closed:
                handle.close()
            if os.path.exists(handle.name):
                os.remove(handle.name)

        self.assertEqual(report["summary"]["openReviews"], 13)
        self.assertEqual(report["summary"]["durableHumanReview"], 12)
        self.assertEqual(report["summary"]["unassessed"], 1)
        self.assertEqual(report["summary"]["unusedDispositions"], 1)
        self.assertEqual(
            report["unassessedReviewKeys"],
            [
                {
                    "caseId": decision["caseId"],
                    "side": side,
                    "evidenceId": current_evidence_id,
                }
            ],
        )
        self.assertEqual(
            report["unusedDispositionKeys"],
            [
                {
                    "caseId": decision["caseId"],
                    "side": side,
                    "evidenceId": stale_evidence_id,
                }
            ],
        )


if __name__ == "__main__":
    unittest.main()
