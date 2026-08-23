import unittest
from datetime import timezone

from podium7.catalog import CatalogStore, CatalogVehicleIdentity, ExternalIdentifier
from podium7.catalog_batch import (
    CATALOG_BATCH_RECORD_ERROR,
    CATALOG_BATCH_REPORT_SCHEMA,
    CatalogBatchEnvelope,
    CatalogBatchReport,
    ingest_catalog_batch,
    parse_catalog_batch_payload,
)
from podium7.catalog_review import CatalogReviewQueue
from podium7.domain import RawEvidence, Source


def vehicle(
    *,
    make: str = "Toyota",
    model: str = "Corolla Cross",
    generation: str = "2020 global generation",
    variant: str | None = "XRX Hybrid",
    powertrain: str | None = "1.8 hybrid flex",
    transmission: str | None = "Hybrid Transaxle CVT",
    body_style: str | None = "SUV",
    market: str | None = "BR",
) -> dict[str, object]:
    payload: dict[str, object] = {
        "make": make,
        "model": model,
        "generation": generation,
        "powertrain": powertrain,
        "transmission": transmission,
        "body_style": body_style,
        "market": market,
        "model_year_from": 2025,
        "model_year_to": 2025,
    }
    if variant is not None:
        payload["variant"] = variant
    return {key: value for key, value in payload.items() if value is not None}


def record(
    record_id: str | None = "r1",
    evidence_id: str = "e1",
    *,
    vehicle_payload: dict[str, object] | None = None,
    source_id: str = "source-1",
    source_name: str = "Source One",
    source_locator: str = "https://example.test/source",
    evidence_locator: str | None = None,
    retrieved_at: str = "2026-08-22T20:00:00Z",
) -> dict[str, object]:
    payload: dict[str, object] = {
        "source": {
            "id": source_id,
            "name": source_name,
            "locator": source_locator,
        },
        "evidence": {
            "id": evidence_id,
            "locator": evidence_locator or f"https://example.test/evidence/{evidence_id}",
            "retrievedAt": retrieved_at,
            "acquisitionMethod": "test-fixture",
            "rawContentRef": f"sha256:{evidence_id}",
        },
        "vehicle": vehicle_payload or vehicle(),
    }
    if record_id is not None:
        payload["recordId"] = record_id
    return payload


def envelopes(*items: dict[str, object]) -> tuple[CatalogBatchEnvelope, ...]:
    return parse_catalog_batch_payload({"records": list(items)})


class CatalogBatchIngestionTests(unittest.TestCase):
    def test_01_batch_root_must_be_object(self) -> None:
        with self.assertRaisesRegex(ValueError, "batch input must be an object"):
            parse_catalog_batch_payload([])

    def test_02_records_are_required(self) -> None:
        with self.assertRaisesRegex(ValueError, "records must be an array"):
            parse_catalog_batch_payload({})

    def test_03_records_must_be_array(self) -> None:
        with self.assertRaisesRegex(ValueError, "records must be an array"):
            parse_catalog_batch_payload({"records": "x"})

    def test_04_records_must_not_be_empty(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least one"):
            parse_catalog_batch_payload({"records": []})

    def test_05_batch_rejects_unknown_root_fields(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported fields"):
            parse_catalog_batch_payload({"records": [record()], "extra": True})

    def test_06_record_must_be_object(self) -> None:
        with self.assertRaisesRegex(ValueError, r"records\[0\] must be an object"):
            parse_catalog_batch_payload({"records": [1]})

    def test_07_record_rejects_unknown_fields(self) -> None:
        item = record()
        item["extra"] = True
        with self.assertRaisesRegex(ValueError, "unsupported fields"):
            parse_catalog_batch_payload({"records": [item]})

    def test_08_record_id_must_be_text(self) -> None:
        item = record()
        item["recordId"] = 7
        with self.assertRaisesRegex(ValueError, "recordId"):
            parse_catalog_batch_payload({"records": [item]})

    def test_09_duplicate_record_ids_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "recordId values must be unique"):
            parse_catalog_batch_payload(
                {"records": [record("same", "e1"), record("same", "e2")]}
            )

    def test_10_record_id_is_optional(self) -> None:
        parsed = envelopes(record(None, "e1"))
        self.assertIsNone(parsed[0].record_id)

    def test_11_source_must_be_object(self) -> None:
        item = record()
        item["source"] = "bad"
        with self.assertRaisesRegex(ValueError, "source must be an object"):
            parse_catalog_batch_payload({"records": [item]})

    def test_12_source_fields_are_required(self) -> None:
        item = record()
        del item["source"]["name"]
        with self.assertRaisesRegex(ValueError, "source.name"):
            parse_catalog_batch_payload({"records": [item]})

    def test_13_source_rejects_unknown_fields(self) -> None:
        item = record()
        item["source"]["extra"] = "x"
        with self.assertRaisesRegex(ValueError, "source has unsupported fields"):
            parse_catalog_batch_payload({"records": [item]})

    def test_14_evidence_must_be_object(self) -> None:
        item = record()
        item["evidence"] = []
        with self.assertRaisesRegex(ValueError, "evidence must be an object"):
            parse_catalog_batch_payload({"records": [item]})

    def test_15_evidence_fields_are_required(self) -> None:
        item = record()
        del item["evidence"]["id"]
        with self.assertRaisesRegex(ValueError, "evidence.id"):
            parse_catalog_batch_payload({"records": [item]})

    def test_16_evidence_requires_timezone(self) -> None:
        item = record(retrieved_at="2026-08-22T20:00:00")
        with self.assertRaisesRegex(ValueError, "include a timezone"):
            parse_catalog_batch_payload({"records": [item]})

    def test_17_evidence_accepts_zulu_timestamp(self) -> None:
        parsed = envelopes(record(retrieved_at="2026-08-22T20:00:00Z"))
        self.assertEqual(parsed[0].evidence.retrieved_at.utcoffset(), timezone.utc.utcoffset(None))

    def test_18_evidence_rejects_unknown_fields(self) -> None:
        item = record()
        item["evidence"]["extra"] = "x"
        with self.assertRaisesRegex(ValueError, "evidence has unsupported fields"):
            parse_catalog_batch_payload({"records": [item]})

    def test_19_vehicle_must_be_object(self) -> None:
        item = record()
        item["vehicle"] = "bad"
        with self.assertRaisesRegex(ValueError, "vehicle must be an object"):
            parse_catalog_batch_payload({"records": [item]})

    def test_20_vehicle_requires_make_and_model(self) -> None:
        missing_make = record(vehicle_payload={"model": "Corolla"})
        missing_model = record(vehicle_payload={"make": "Toyota"})
        with self.assertRaisesRegex(ValueError, "vehicle.make"):
            parse_catalog_batch_payload({"records": [missing_make]})
        with self.assertRaisesRegex(ValueError, "vehicle.model"):
            parse_catalog_batch_payload({"records": [missing_model]})

    def test_21_parser_builds_domain_source_and_evidence(self) -> None:
        parsed = envelopes(record())
        self.assertIsInstance(parsed[0].source, Source)
        self.assertIsInstance(parsed[0].evidence, RawEvidence)
        self.assertEqual(parsed[0].evidence.source_id, parsed[0].source.id)

    def test_22_direct_empty_batch_returns_zero_report(self) -> None:
        report = ingest_catalog_batch(CatalogStore(), ())
        self.assertEqual(report, CatalogBatchReport(0, 0, 0, 0, 0, 0, ()))
        self.assertTrue(report.ok)

    def test_23_new_record_is_created(self) -> None:
        store = CatalogStore()
        report = ingest_catalog_batch(store, envelopes(record()))
        self.assertEqual(report.created, 1)
        self.assertEqual(report.results[0].action.value, "CREATED")
        self.assertIsNotNone(report.results[0].vehicle_id)

    def test_24_later_duplicate_matches_earlier_batch_record(self) -> None:
        store = CatalogStore()
        report = ingest_catalog_batch(
            store,
            envelopes(record("r1", "e1"), record("r2", "e2")),
        )
        self.assertEqual((report.created, report.matched), (1, 1))
        self.assertEqual(report.results[0].vehicle_id, report.results[1].vehicle_id)
        self.assertEqual(len(store.catalog_vehicle_ids_page(limit=10)), 1)

    def test_25_distinct_variant_creates_second_identity(self) -> None:
        store = CatalogStore()
        distinct = vehicle(variant="XRX", powertrain="2.0 flex", transmission="Direct Shift CVT")
        report = ingest_catalog_batch(
            store,
            envelopes(record("r1", "e1"), record("r2", "e2", vehicle_payload=distinct)),
        )
        self.assertEqual(report.created, 2)
        self.assertEqual(len(store.catalog_vehicle_ids_page(limit=10)), 2)

    def test_26_incomplete_overlap_goes_to_durable_review(self) -> None:
        store = CatalogStore()
        existing = store.create_catalog_vehicle(
            CatalogVehicleIdentity(
                make="Toyota",
                model="Corolla Cross",
                generation="2020 global generation",
                variant="XRX Hybrid",
                powertrain="1.8 hybrid flex",
                transmission="Hybrid Transaxle CVT",
                body_style="SUV",
                market="BR",
                model_year_from=2025,
                model_year_to=2025,
            )
        )
        incoming = vehicle(variant=None)
        report = ingest_catalog_batch(store, envelopes(record(vehicle_payload=incoming)))
        self.assertEqual(report.review, 1)
        self.assertIsNotNone(report.results[0].review_id)
        task = CatalogReviewQueue(store).get(report.results[0].review_id)
        self.assertEqual(task.candidate_vehicle_ids, (existing,))

    def test_27_review_counts_as_success(self) -> None:
        store = CatalogStore()
        store.create_catalog_vehicle(
            CatalogVehicleIdentity(
                make="Toyota",
                model="Corolla Cross",
                generation="2020 global generation",
                variant="XRX Hybrid",
                powertrain="1.8 hybrid flex",
                transmission="Hybrid Transaxle CVT",
                body_style="SUV",
                market="BR",
            )
        )
        report = ingest_catalog_batch(
            store,
            envelopes(record(vehicle_payload=vehicle(variant=None))),
        )
        self.assertEqual((report.succeeded, report.failed), (1, 0))
        self.assertTrue(report.ok)

    def test_28_invalid_record_does_not_stop_later_records(self) -> None:
        store = CatalogStore()
        invalid = vehicle()
        invalid["unsupported"] = "x"
        report = ingest_catalog_batch(
            store,
            envelopes(
                record("bad", "e1", vehicle_payload=invalid),
                record("good", "e2", vehicle_payload=vehicle(model="RAV4")),
            ),
        )
        self.assertEqual((report.failed, report.created), (1, 1))
        self.assertFalse(report.results[0].ok)
        self.assertTrue(report.results[1].ok)

    def test_29_success_before_failure_is_preserved(self) -> None:
        store = CatalogStore()
        invalid = vehicle()
        invalid["unsupported"] = "x"
        report = ingest_catalog_batch(
            store,
            envelopes(
                record("good", "e1"),
                record("bad", "e2", vehicle_payload=invalid),
            ),
        )
        self.assertEqual((report.created, report.failed), (1, 1))
        self.assertEqual(len(store.catalog_vehicle_ids_page(limit=10)), 1)

    def test_30_failed_record_has_stable_error_code(self) -> None:
        store = CatalogStore()
        invalid = vehicle()
        invalid["unsupported"] = "x"
        report = ingest_catalog_batch(store, envelopes(record(vehicle_payload=invalid)))
        self.assertEqual(report.results[0].error_code, CATALOG_BATCH_RECORD_ERROR)
        self.assertIsNotNone(report.results[0].error_message)

    def test_31_source_metadata_conflict_is_record_failure(self) -> None:
        store = CatalogStore()
        report = ingest_catalog_batch(
            store,
            envelopes(
                record("r1", "e1", source_name="Source One"),
                record("r2", "e2", source_name="Changed Source Name"),
                record("r3", "e3", vehicle_payload=vehicle(model="RAV4")),
            ),
        )
        self.assertEqual(report.failed, 1)
        self.assertTrue(report.results[2].ok)

    def test_32_evidence_metadata_conflict_is_record_failure(self) -> None:
        store = CatalogStore()
        report = ingest_catalog_batch(
            store,
            envelopes(
                record("r1", "same-evidence"),
                record(
                    "r2",
                    "same-evidence",
                    evidence_locator="https://example.test/changed",
                ),
            ),
        )
        self.assertEqual((report.created, report.failed), (1, 1))

    def test_33_exact_evidence_retry_is_idempotent(self) -> None:
        store = CatalogStore()
        same = record("r1", "same-evidence")
        second = dict(same)
        second["recordId"] = "r2"
        report = ingest_catalog_batch(store, envelopes(same, second))
        self.assertEqual((report.created, report.matched, report.failed), (1, 1, 0))
        vehicle_id = report.results[0].vehicle_id
        candidates = store.catalog_candidates_for_entity(vehicle_id)
        self.assertEqual(len({candidate.id for candidate in candidates}), len(candidates))

    def test_34_report_payload_has_stable_schema_and_summary(self) -> None:
        report = ingest_catalog_batch(CatalogStore(), envelopes(record()))
        payload = report.to_payload()
        self.assertEqual(payload["schema"], CATALOG_BATCH_REPORT_SCHEMA)
        self.assertEqual(payload["summary"]["total"], 1)
        self.assertEqual(payload["summary"]["succeeded"], 1)

    def test_35_record_payload_preserves_trace_fields(self) -> None:
        report = ingest_catalog_batch(CatalogStore(), envelopes(record("trace-7", "e7")))
        payload = report.to_payload()["records"][0]
        self.assertEqual(payload["recordId"], "trace-7")
        self.assertEqual(payload["evidenceId"], "e7")
        self.assertEqual(payload["index"], 0)

    def test_36_report_ok_is_false_when_any_record_fails(self) -> None:
        invalid = vehicle()
        invalid["unsupported"] = "x"
        report = ingest_catalog_batch(
            CatalogStore(),
            envelopes(record("good", "e1"), record("bad", "e2", vehicle_payload=invalid)),
        )
        self.assertFalse(report.ok)
        self.assertFalse(report.to_payload()["ok"])

    def test_37_results_preserve_input_order(self) -> None:
        report = ingest_catalog_batch(
            CatalogStore(),
            envelopes(
                record("first", "e1", vehicle_payload=vehicle(model="A")),
                record("second", "e2", vehicle_payload=vehicle(model="B")),
                record("third", "e3", vehicle_payload=vehicle(model="C")),
            ),
        )
        self.assertEqual(
            [item.record_id for item in report.results],
            ["first", "second", "third"],
        )
        self.assertEqual([item.index for item in report.results], [0, 1, 2])

    def test_38_aliases_and_external_ids_flow_through_batch(self) -> None:
        store = CatalogStore()
        incoming = vehicle()
        incoming["aliases"] = ["CorollaCross"]
        incoming["external_identifiers"] = [{"namespace": "fipe", "value": "123456-7"}]
        report = ingest_catalog_batch(store, envelopes(record(vehicle_payload=incoming)))
        identity = store.get_catalog_vehicle(report.results[0].vehicle_id)
        self.assertEqual(identity.aliases, ("CorollaCross",))
        self.assertEqual(
            identity.external_identifiers,
            (ExternalIdentifier("fipe", "123456-7"),),
        )

    def test_39_model_year_fields_flow_through_batch(self) -> None:
        store = CatalogStore()
        report = ingest_catalog_batch(store, envelopes(record()))
        identity = store.get_catalog_vehicle(report.results[0].vehicle_id)
        self.assertEqual((identity.model_year_from, identity.model_year_to), (2025, 2025))

    def test_40_multiple_existing_matches_produce_one_review_task(self) -> None:
        store = CatalogStore()
        identity = CatalogVehicleIdentity(
            make="Toyota",
            model="Corolla Cross",
            generation="2020 global generation",
            variant="XRX Hybrid",
            powertrain="1.8 hybrid flex",
            transmission="Hybrid Transaxle CVT",
            body_style="SUV",
            market="BR",
            model_year_from=2025,
            model_year_to=2025,
        )
        store.create_catalog_vehicle(identity)
        store.create_catalog_vehicle(identity)
        report = ingest_catalog_batch(store, envelopes(record()))
        self.assertEqual(report.review, 1)
        self.assertEqual(CatalogReviewQueue(store).count_open(), 1)
        self.assertIsNotNone(report.results[0].review_id)


if __name__ == "__main__":
    unittest.main()
