import tempfile
import unittest
from pathlib import Path

from podium7.web_acquisition import (
    AcquisitionIssueCode,
    FrozenAcquisitionEntry,
    FrozenAcquisitionManifest,
    evaluate_current_web_acquisition,
    evaluate_frozen_web_acquisition,
    git_blob_sha1,
    load_current_web_acquisition_manifest,
)


ROOT = Path(__file__).resolve().parents[1]


def entry(
    case_id: str,
    snapshot: str,
    expected_sha1: str | None,
    *,
    family: str = "test_family",
    source_url: str = "https://example.test/vehicle",
) -> FrozenAcquisitionEntry:
    return FrozenAcquisitionEntry(
        source_family=family,
        dataset_version="test-1.0",
        case_id=case_id,
        source_url=source_url,
        snapshot=snapshot,
        expected_git_blob_sha1=expected_sha1,
    )


class WebAcquisitionEvidenceTests(unittest.TestCase):
    def test_current_manifest_is_derived_from_both_existing_benchmarks(self):
        manifest = load_current_web_acquisition_manifest(ROOT)
        self.assertEqual(len(manifest.entries), 16)
        self.assertEqual(
            {item.source_family for item in manifest.entries},
            {"autoevolution", "fueleconomy_gov"},
        )
        self.assertEqual(manifest.orphan_pins, ())

    def test_current_cross_family_acquisition_evidence_is_complete(self):
        report = evaluate_current_web_acquisition(ROOT)
        metrics = report.to_dict()
        self.assertTrue(report.ok)
        self.assertEqual(metrics["status"], "PASS")
        self.assertEqual(metrics["sourceFamilyCount"], 2)
        self.assertEqual(metrics["caseCount"], 16)
        self.assertEqual(metrics["uniqueSourceUrlCount"], 13)
        self.assertEqual(metrics["declaredSnapshotCount"], 16)
        self.assertEqual(metrics["verifiedSnapshotCount"], 16)
        self.assertEqual(metrics["issueCount"], 0)
        self.assertGreater(metrics["verifiedBytes"], 0)

    def test_current_evidence_uses_sha256_content_references(self):
        report = evaluate_current_web_acquisition(ROOT)
        self.assertTrue(report.ok)
        for item in report.evidence:
            self.assertTrue(item.content_ref.startswith("sha256:"))
            self.assertIn("@", item.content_ref)

    def test_shared_source_url_is_allowed_when_snapshots_are_distinct(self):
        manifest = load_current_web_acquisition_manifest(ROOT)
        tcross = [item for item in manifest.entries if "vw-tcross" in item.case_id]
        self.assertEqual(len(tcross), 2)
        self.assertEqual(tcross[0].source_url, tcross[1].source_url)
        self.assertNotEqual(tcross[0].snapshot, tcross[1].snapshot)
        self.assertTrue(evaluate_current_web_acquisition(ROOT).ok)

    def test_mutated_snapshot_fails_against_pinned_blob_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            snapshot = root / "snapshot.txt"
            snapshot.write_bytes(b"alpha")
            pinned = git_blob_sha1(b"alpha")
            manifest = FrozenAcquisitionManifest((entry("case", "snapshot.txt", pinned),))
            self.assertTrue(evaluate_frozen_web_acquisition(manifest, root).ok)

            snapshot.write_bytes(b"beta")
            report = evaluate_frozen_web_acquisition(manifest, root)
            self.assertFalse(report.ok)
            self.assertIn(AcquisitionIssueCode.HASH_MISMATCH, {issue.code for issue in report.issues})

    def test_missing_snapshot_is_explicit_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = FrozenAcquisitionManifest((entry("case", "missing.txt", "0" * 40),))
            report = evaluate_frozen_web_acquisition(manifest, tmp)
            self.assertEqual({issue.code for issue in report.issues}, {AcquisitionIssueCode.MISSING_SNAPSHOT})

    def test_empty_snapshot_is_explicit_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "empty.txt").write_bytes(b"")
            manifest = FrozenAcquisitionManifest((entry("case", "empty.txt", git_blob_sha1(b"")),))
            report = evaluate_frozen_web_acquisition(manifest, root)
            self.assertEqual({issue.code for issue in report.issues}, {AcquisitionIssueCode.EMPTY_SNAPSHOT})

    def test_non_https_source_locator_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "snapshot.txt").write_bytes(b"data")
            manifest = FrozenAcquisitionManifest(
                (entry("case", "snapshot.txt", git_blob_sha1(b"data"), source_url="http://example.test/vehicle"),)
            )
            report = evaluate_frozen_web_acquisition(manifest, root)
            self.assertIn(AcquisitionIssueCode.INVALID_SOURCE_URL, {issue.code for issue in report.issues})

    def test_duplicate_case_identity_and_snapshot_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "snapshot.txt").write_bytes(b"data")
            pinned = git_blob_sha1(b"data")
            manifest = FrozenAcquisitionManifest(
                (
                    entry("case", "snapshot.txt", pinned),
                    entry("case", "snapshot.txt", pinned),
                )
            )
            report = evaluate_frozen_web_acquisition(manifest, root)
            codes = {issue.code for issue in report.issues}
            self.assertIn(AcquisitionIssueCode.DUPLICATE_CASE_ID, codes)
            self.assertIn(AcquisitionIssueCode.DUPLICATE_SNAPSHOT, codes)

    def test_missing_and_orphan_pins_are_explicit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "snapshot.txt").write_bytes(b"data")
            manifest = FrozenAcquisitionManifest(
                (entry("case", "snapshot.txt", None),),
                orphan_pins=("unused.txt",),
            )
            report = evaluate_frozen_web_acquisition(manifest, root)
            codes = {issue.code for issue in report.issues}
            self.assertIn(AcquisitionIssueCode.MISSING_PIN, codes)
            self.assertIn(AcquisitionIssueCode.ORPHAN_PIN, codes)


if __name__ == "__main__":
    unittest.main()
