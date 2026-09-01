import unittest
from datetime import datetime, timezone

from podium7.catalog import CatalogStore
from podium7.catalog_ingestion import CatalogIngestionAction, ingest_catalog_record
from podium7.catalog_review import CatalogReviewQueue
from podium7.domain import RawEvidence, Source


GENERATION_SOURCE = Source(
    id="generation-source",
    name="Generation source",
    locator="https://example.test/generation",
)
CONFIG_SOURCE = Source(
    id="configuration-source",
    name="Configuration source",
    locator="https://example.test/configuration",
)


def _evidence(source: Source, suffix: str) -> RawEvidence:
    return RawEvidence(
        id=f"evidence-{suffix}",
        source_id=source.id,
        locator=f"{source.locator}/{suffix}",
        retrieved_at=datetime(2026, 8, 31, 12, 0, tzinfo=timezone.utc),
        acquisition_method="multisource-split-replay-experiment",
        raw_content_ref=f"fixture:{suffix}",
    )


def _generation_observation() -> dict[str, object]:
    return {
        "make": "Volkswagen",
        "model": "T-Cross",
        "generation": "2019 Brazil generation",
        "market": "BR",
    }


def _configuration_observation() -> dict[str, object]:
    return {
        "make": "Volkswagen",
        "model": "T-Cross",
        "variant": "Highline 250 TSI",
        "powertrain": "250 TSI flex",
        "transmission": "6-speed automatic",
        "market": "BR",
    }


def _run(order: tuple[str, str]) -> tuple[tuple[str, ...], tuple[object, ...]]:
    store = CatalogStore()
    actions: list[str] = []

    for item in order:
        if item == "generation":
            result = ingest_catalog_record(
                store,
                _generation_observation(),
                source=GENERATION_SOURCE,
                evidence=_evidence(GENERATION_SOURCE, "generation"),
            )
        elif item == "configuration":
            result = ingest_catalog_record(
                store,
                _configuration_observation(),
                source=CONFIG_SOURCE,
                evidence=_evidence(CONFIG_SOURCE, "configuration"),
            )
        else:
            raise AssertionError(item)
        actions.append(result.action.value)

    vehicle_ids = store.catalog_vehicle_ids_page(limit=10)
    identities = tuple(store.get_catalog_vehicle(vehicle_id) for vehicle_id in vehicle_ids)
    return tuple(actions), identities


class MultiSourceSplitReplayExperimentTests(unittest.TestCase):
    def test_naive_source_split_is_order_sensitive_under_current_ingestion(self) -> None:
        generation_first_actions, generation_first_identities = _run(
            ("generation", "configuration")
        )
        configuration_first_actions, configuration_first_identities = _run(
            ("configuration", "generation")
        )

        self.assertEqual(
            generation_first_actions,
            (CatalogIngestionAction.CREATED.value, CatalogIngestionAction.REVIEW.value),
        )
        self.assertEqual(
            configuration_first_actions,
            (CatalogIngestionAction.CREATED.value, CatalogIngestionAction.REVIEW.value),
        )
        self.assertEqual(len(generation_first_identities), 1)
        self.assertEqual(len(configuration_first_identities), 1)
        self.assertNotEqual(generation_first_identities, configuration_first_identities)

        generation_first = generation_first_identities[0]
        configuration_first = configuration_first_identities[0]
        self.assertEqual(generation_first.generation, "2019 Brazil generation")
        self.assertIsNone(generation_first.variant)
        self.assertIsNone(configuration_first.generation)
        self.assertEqual(configuration_first.variant, "Highline 250 TSI")

    def test_split_preserves_review_provenance_but_not_composite_attachment(self) -> None:
        store = CatalogStore()
        first = ingest_catalog_record(
            store,
            _generation_observation(),
            source=GENERATION_SOURCE,
            evidence=_evidence(GENERATION_SOURCE, "generation"),
        )
        second = ingest_catalog_record(
            store,
            _configuration_observation(),
            source=CONFIG_SOURCE,
            evidence=_evidence(CONFIG_SOURCE, "configuration"),
        )

        self.assertEqual(first.action, CatalogIngestionAction.CREATED)
        self.assertEqual(second.action, CatalogIngestionAction.REVIEW)
        self.assertIsNotNone(first.vehicle_id)
        self.assertIsNone(second.vehicle_id)
        self.assertIsNotNone(second.review_id)

        candidates = store.catalog_candidates_for_entity(first.vehicle_id)
        self.assertTrue(candidates)
        self.assertEqual(
            {candidate.evidence_id for candidate in candidates},
            {"evidence-generation"},
        )
        self.assertIsNotNone(store.get_raw_evidence("evidence-configuration"))
        self.assertNotIn(
            "evidence-configuration",
            {candidate.evidence_id for candidate in candidates},
        )

        review_bindings = CatalogReviewQueue(store).review_field_bindings(second.review_id)
        self.assertTrue(review_bindings)
        self.assertEqual(
            {binding["rawEvidenceId"] for binding in review_bindings},
            {"evidence-configuration"},
        )
        self.assertEqual(
            {binding["sourceId"] for binding in review_bindings},
            {CONFIG_SOURCE.id},
        )
        self.assertEqual(
            {binding["fieldName"] for binding in review_bindings},
            set(_configuration_observation()),
        )


if __name__ == "__main__":
    unittest.main()
