from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .domain import AutomotiveIdentity, CandidateFact, EntityKind, RawEvidence, Source
from .persistence import EvidenceStore

SOURCE_ID = "vehicle-makes-models"
SOURCE_NAME = "gor3a/vehicle-makes-models"
SOURCE_LOCATOR = "https://github.com/gor3a/vehicle-makes-models"
EXTRACTION_METHOD = "structured-json-v1"


@dataclass(frozen=True)
class IngestionReport:
    source_id: str
    makes: int
    models: int
    generations: int
    automotive_entities: int
    raw_evidence: int
    candidate_facts: int

    @property
    def real_automotive_records(self) -> int:
        return self.automotive_entities


def _stable_id(prefix: str, material: str) -> str:
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()[:24]
    return f"{prefix}:{digest}"


def _candidate(
    *,
    entity_id: str,
    evidence_id: str,
    pointer: str,
    attribute: str,
    value: Any,
    unit: str | None = None,
) -> CandidateFact:
    return CandidateFact(
        id=_stable_id("candidate", f"{pointer}|{attribute}"),
        entity_candidate_id=entity_id,
        attribute=attribute,
        raw_value=value,
        # Work Unit 4 owns semantic normalization. Until then the structured
        # source value is carried through unchanged and no rule is claimed.
        normalized_value=value,
        unit=unit,
        evidence_id=evidence_id,
        extraction_method=EXTRACTION_METHOD,
        confidence=None,
        normalization_rule=None,
    )


def ingest_vehicle_makes_models_json(
    store: EvidenceStore,
    path: str | Path,
    *,
    acquired_at: datetime | None = None,
) -> IngestionReport:
    """Ingest one structured make snapshot from vehicle-makes-models.

    The source JSON is preserved separately from extracted entities/facts. This
    importer intentionally performs no semantic normalization, entity matching,
    or fusion; those remain later pipeline stages.
    """

    source_path = Path(path)
    payload = json.loads(source_path.read_text(encoding="utf-8"))
    acquired_at = acquired_at or datetime.now(timezone.utc)

    store.save_source(Source(SOURCE_ID, SOURCE_NAME, SOURCE_LOCATOR))

    make_count = model_count = generation_count = 0
    entity_count = evidence_count = fact_count = 0

    for make_index, make in enumerate(payload.get("makes", [])):
        make_count += 1
        make_name = make["name"]

        for model_index, model in enumerate(make.get("models", [])):
            model_count += 1
            model_name = model["name"]

            for generation_index, generation in enumerate(model.get("generations", [])):
                generation_count += 1
                generation_name = generation["name"]

                for engine_index, engine in enumerate(generation.get("engines", [])):
                    pointer = (
                        f"/makes/{make_index}/models/{model_index}"
                        f"/generations/{generation_index}/engines/{engine_index}"
                    )
                    remote_locator = (
                        "https://github.com/gor3a/vehicle-makes-models/blob/main/"
                        f"data/json/{source_path.name}#{pointer}"
                    )
                    entity_id = _stable_id("entity", remote_locator)
                    evidence_id = _stable_id("evidence", remote_locator)

                    store.save_entity(
                        entity_id,
                        AutomotiveIdentity(
                            kind=EntityKind.POWERTRAIN,
                            make=make_name,
                            model=model_name,
                            generation=generation_name,
                            powertrain=engine.get("label"),
                            year_from=generation.get("yearStart") or model.get("yearStart"),
                            year_to=generation.get("yearEnd") or model.get("yearEnd"),
                            external_identifiers=(remote_locator,),
                        ),
                    )
                    entity_count += 1

                    store.save_raw_evidence(
                        RawEvidence(
                            id=evidence_id,
                            source_id=SOURCE_ID,
                            locator=remote_locator,
                            retrieved_at=acquired_at,
                            acquisition_method="pinned-github-json-snapshot",
                            raw_content_ref=str(source_path),
                        )
                    )
                    evidence_count += 1

                    fields: tuple[tuple[str, str, str | None], ...] = (
                        ("fuel_type", "fuelType", None),
                        ("cylinders", "cylinders", None),
                        ("displacement", "displacementCc", "cc"),
                        ("power", "powerHp", "hp"),
                        ("torque", "torqueNm", "Nm"),
                        ("transmission", "transmission", None),
                        ("drivetrain", "drivetrain", None),
                        ("zero_to_hundred", "zeroToHundredKmhS", "s"),
                        ("top_speed", "topSpeedKmh", "km/h"),
                        ("fuel_economy_combined", "fuelEconomyCombinedL100", "L/100km"),
                        ("length", "lengthMm", "mm"),
                        ("width", "widthMm", "mm"),
                        ("height", "heightMm", "mm"),
                        ("wheelbase", "wheelbaseMm", "mm"),
                        ("curb_weight", "curbWeightKg", "kg"),
                    )

                    for attribute, source_key, unit in fields:
                        value = engine.get(source_key)
                        if value is None:
                            continue
                        store.save_candidate_fact(
                            _candidate(
                                entity_id=entity_id,
                                evidence_id=evidence_id,
                                pointer=pointer,
                                attribute=attribute,
                                value=value,
                                unit=unit,
                            )
                        )
                        fact_count += 1

                    body_type = generation.get("bodyType")
                    if body_type is not None:
                        store.save_candidate_fact(
                            _candidate(
                                entity_id=entity_id,
                                evidence_id=evidence_id,
                                pointer=pointer,
                                attribute="body_type",
                                value=body_type,
                            )
                        )
                        fact_count += 1

    return IngestionReport(
        source_id=SOURCE_ID,
        makes=make_count,
        models=model_count,
        generations=generation_count,
        automotive_entities=entity_count,
        raw_evidence=evidence_count,
        candidate_facts=fact_count,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ingest a vehicle-makes-models JSON snapshot")
    parser.add_argument("source", type=Path)
    parser.add_argument("--database", type=Path, default=Path("podium7.sqlite"))
    args = parser.parse_args(argv)

    with EvidenceStore(args.database) as store:
        report = ingest_vehicle_makes_models_json(store, args.source)
        counts = store.snapshot_counts()

    print(json.dumps({"ingestion": report.__dict__, "store": counts}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
