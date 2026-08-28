from __future__ import annotations

import json
from pathlib import Path
import unittest

from podium7.v3_side_provenance_export import (
    build_v3_side_provenance_export,
    export_v3_side_provenance_json,
)


ROOT = Path(__file__).resolve().parents[1]


class V3SideProvenanceExportTests(unittest.TestCase):
    def test_export_is_structurally_bounded_and_deterministic(self) -> None:
        export = build_v3_side_provenance_export()
        payload = json.loads(export_v3_side_provenance_json())
        again = json.loads(export_v3_side_provenance_json())

        self.assertEqual(export, payload)
        self.assertEqual(payload, again)
        self.assertEqual(payload["schema"], "podium7.v3-side-provenance-export.v1")
        self.assertEqual(payload["counts"], {
            "totalCases": 36,
            "totalSides": 72,
            "replayableSides": 12,
            "blockedSides": 60,
        })
        self.assertEqual(len(payload["blockedSides"]), 60)
        self.assertEqual(len({item["caseId"] for item in payload["blockedSides"]}), 30)
        self.assertEqual(payload["counts"]["totalCases"] * 2, payload["counts"]["totalSides"])

    def test_export_does_not_invent_attribution(self) -> None:
        payload = build_v3_side_provenance_export()
        for blocked_side in payload["blockedSides"]:
            self.assertIn(blocked_side["classification"], {
                "EXPLICITLY_RECONSTRUCTABLE",
                "AMBIGUOUS_MULTI_SOURCE",
                "MISSING_RETAINED_EVIDENCE",
                "CONTRADICTORY_EVIDENCE",
                "OTHER_BLOCKED",
            })
            for binding in blocked_side["fieldBindings"]:
                self.assertIn(binding["bindingStatus"], {
                    "EXPLICIT",
                    "MULTIPLE_EXPLICIT_SOURCES",
                    "NO_EXPLICIT_BINDING",
                    "MISSING_EVIDENCE_REFERENCE",
                    "CONTRADICTORY",
                })
                if binding["bindingStatus"] == "NO_EXPLICIT_BINDING":
                    self.assertEqual(binding["sourceIds"], [])
                    self.assertEqual(binding["candidateRefs"], [])

    def test_reorder_of_source_ids_does_not_change_semantics(self) -> None:
        baseline = build_v3_side_provenance_export()
        shuffled_path = ROOT / "benchmarks" / "catalog_identity_br_adjacent_incomplete_v1.json"
        payload = json.loads(shuffled_path.read_text(encoding="utf-8"))
        payload["cases"][0]["sourceIds"] = list(reversed(payload["cases"][0]["sourceIds"]))
        temp = ROOT / ".tmp_v3_reordered.json"
        try:
            temp.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            export = build_v3_side_provenance_export(
                (
                    ROOT / "benchmarks" / "catalog_identity_golden_v1.json",
                    ROOT / "benchmarks" / "catalog_identity_golden_br_v1.json",
                    ROOT / "benchmarks" / "catalog_identity_br_adjacent_incomplete_v1.json",
                    temp,
                )
            )
        finally:
            if temp.exists():
                temp.unlink()

        self.assertEqual(
            baseline["counts"],
            export["counts"],
        )

    def test_malformed_missing_references_fail_closed(self) -> None:
        payload = json.loads((ROOT / "benchmarks" / "source_backed_enrichment_v3.json").read_text(encoding="utf-8"))
        payload["observations"][0]["sourceId"] = ""
        temp = ROOT / ".tmp_v3_bad_enrichment.json"
        try:
            temp.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            with self.assertRaises(ValueError):
                build_v3_side_provenance_export(enrichment_path=temp)
        finally:
            if temp.exists():
                temp.unlink()


if __name__ == "__main__":
    unittest.main()
