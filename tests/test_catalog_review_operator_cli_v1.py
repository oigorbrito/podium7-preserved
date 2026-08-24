from __future__ import annotations

from contextlib import redirect_stdout
from datetime import datetime, timezone
from io import StringIO
import json
import os
import tempfile
import unittest

from podium7.__main__ import main
from podium7.catalog import CatalogStore, CatalogVehicleIdentity
from podium7.catalog_ingestion import CatalogIngestionAction, ingest_catalog_record
from podium7.catalog_review import CatalogReviewQueue, CatalogReviewState
from podium7.domain import RawEvidence, Source


SOURCE = Source(
    id="operator-source",
    name="Operator source",
    locator="https://example.test/operator",
)


def full_identity() -> CatalogVehicleIdentity:
    return CatalogVehicleIdentity(
        make="Ford",
        model="Mustang",
        generation="7th generation",
        variant="Dark Horse",
        powertrain="5.0 V8",
        body_style="coupe",
        market="US",
        model_year_from=2024,
        model_year_to=2024,
    )


def evidence(identifier: str) -> RawEvidence:
    return RawEvidence(
        id=identifier,
        source_id=SOURCE.id,
        locator=f"https://example.test/operator/{identifier}",
        retrieved_at=datetime(2026, 8, 24, 12, 0, tzinfo=timezone.utc),
        acquisition_method="test-fixture",
        raw_content_ref=f"sha256:{identifier}",
    )


class CatalogReviewOperatorCliV1Tests(unittest.TestCase):
    def setUp(self) -> None:
        handle = tempfile.NamedTemporaryFile(delete=False)
        self.database = handle.name
        handle.close()
        self.addCleanup(self._cleanup)

    def _cleanup(self) -> None:
        if os.path.exists(self.database):
            os.remove(self.database)

    def _seed_review(self, identifier: str = "operator-review") -> tuple[str, str]:
        with CatalogStore(self.database) as store:
            candidate = store.create_catalog_vehicle(full_identity())
            record = {
                "make": "Ford",
                "model": "Mustang",
                "generation": "7th generation",
                "powertrain": "5.0 V8",
                "body_style": "coupe",
                "market": "US",
                "model_year_from": 2024,
                "model_year_to": 2024,
            }
            result = ingest_catalog_record(
                store,
                record,
                source=SOURCE,
                evidence=evidence(identifier),
            )
            self.assertIs(result.action, CatalogIngestionAction.REVIEW)
            assert result.review_id is not None
            return result.review_id, candidate

    def _run(self, argv: list[str]) -> tuple[int, dict[str, object]]:
        output = StringIO()
        with redirect_stdout(output):
            code = main(argv)
        return code, json.loads(output.getvalue())

    def test_list_and_show_expose_review_candidate_and_evidence_context(self) -> None:
        review_id, candidate = self._seed_review()

        code, listed = self._run([
            "review",
            "list",
            "--database",
            self.database,
        ])
        self.assertEqual(code, 0)
        self.assertEqual(listed["status"], "PASS")
        self.assertEqual(listed["count"], 1)
        self.assertEqual(listed["items"][0]["id"], review_id)
        self.assertEqual(listed["items"][0]["candidateVehicleIds"], [candidate])
        self.assertNotIn("candidateEntities", listed["items"][0])
        self.assertNotIn("evidence", listed["items"][0])

        code, shown = self._run([
            "review",
            "show",
            review_id,
            "--database",
            self.database,
        ])
        self.assertEqual(code, 0)
        self.assertEqual(shown["item"]["id"], review_id)
        self.assertEqual(shown["item"]["state"], "OPEN")
        self.assertEqual(len(shown["item"]["candidateEntities"]), 1)
        self.assertEqual(shown["item"]["candidateEntities"][0]["id"], candidate)
        self.assertEqual(shown["item"]["candidateEntities"][0]["variant"], "Dark Horse")
        self.assertEqual(shown["item"]["evidence"]["id"], "operator-review")
        self.assertEqual(shown["item"]["evidence"]["sourceId"], SOURCE.id)
        self.assertEqual(shown["item"]["evidence"]["source"]["locator"], SOURCE.locator)
        self.assertEqual(
            shown["item"]["evidence"]["rawContentRef"],
            "sha256:operator-review",
        )

    def test_match_reuses_safe_domain_resolution_and_audit_fields(self) -> None:
        review_id, candidate = self._seed_review()

        code, payload = self._run([
            "review",
            "match",
            review_id,
            candidate,
            "--database",
            self.database,
            "--actor",
            "operator-1",
            "--reason",
            "verified against retained source evidence",
        ])

        self.assertEqual(code, 0)
        self.assertEqual(payload["status"], "PASS")
        self.assertEqual(payload["item"]["state"], "RESOLVED")
        self.assertEqual(payload["item"]["resolutionAction"], "MATCHED")
        self.assertEqual(payload["item"]["resolvedBy"], "operator-1")
        with CatalogStore(self.database) as store:
            task = CatalogReviewQueue(store).get(review_id)
            assert task is not None
            self.assertIs(task.state, CatalogReviewState.RESOLVED)
            self.assertEqual(task.resolution_vehicle_id, candidate)

    def test_create_reuses_evidence_backed_creation_path(self) -> None:
        review_id, _ = self._seed_review()
        with CatalogStore(self.database) as store:
            before = len(store.catalog_vehicle_ids_page(limit=100))

        code, payload = self._run([
            "review",
            "create",
            review_id,
            "--database",
            self.database,
            "--actor",
            "operator-2",
            "--reason",
            "review confirmed distinct configuration",
        ])

        self.assertEqual(code, 0)
        self.assertEqual(payload["item"]["resolutionAction"], "CREATED")
        created_vehicle = payload["item"]["resolutionVehicleId"]
        with CatalogStore(self.database) as store:
            after = len(store.catalog_vehicle_ids_page(limit=100))
            self.assertEqual(after, before + 1)
            self.assertIsNotNone(store.get_catalog_vehicle(created_vehicle))

    def test_review_commands_reject_empty_existing_file_without_initializing_it(self) -> None:
        before_size = os.path.getsize(self.database)

        code, payload = self._run([
            "review",
            "list",
            "--database",
            self.database,
        ])

        self.assertEqual(code, 1)
        self.assertEqual(payload["status"], "FAIL")
        self.assertIn("Podium catalog review schema", payload["error"])
        self.assertEqual(os.path.getsize(self.database), before_size)

    def test_review_commands_fail_closed_for_missing_database_or_invalid_candidate(self) -> None:
        missing = self.database + ".missing"
        code, payload = self._run([
            "review",
            "list",
            "--database",
            missing,
        ])
        self.assertEqual(code, 1)
        self.assertEqual(payload["status"], "FAIL")
        self.assertIn("existing file", payload["error"])
        self.assertFalse(os.path.exists(missing))

        review_id, _ = self._seed_review("operator-review-invalid")
        code, payload = self._run([
            "review",
            "match",
            review_id,
            "veh_not_a_candidate",
            "--database",
            self.database,
            "--actor",
            "operator-3",
            "--reason",
            "invalid selection probe",
        ])
        self.assertEqual(code, 1)
        self.assertEqual(payload["status"], "FAIL")
        self.assertIn("not a candidate", payload["error"])


if __name__ == "__main__":
    unittest.main()
