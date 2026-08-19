from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .domain import AutomotiveIdentity, CandidateFact, EntityKind, RawEvidence, Source
from .evidence import content_addressed_ref
from .normalization import normalize_fact
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


def _reject_non_standard_json_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON numeric constant is not allowed: {value}")


def _require_object(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{path} must be an object")
    return value


def _require_list(record: dict[str, Any], key: str, path: str) -> list[Any]:
    if key not in record:
        raise ValueError(f"{path}.{key} is required")
    value = record[key]
    if not isinstance(value, list):
        raise ValueError(f"{path}.{key} must be a list")
    return value


def _require_name(record: dict[str, Any], path: str) -> str:
    value = record.get("name")
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{path}.name must be non-empty text")
    return value


def _require_engine_label(engine: dict[str, Any], path: str) -> str:
    value = engine.get("label")
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{path}.label must be non-empty text")
    return value


def _validate_vehicle_makes_models_payload(payload: Any) -> None:
    root = _require_object(payload, "$")
    makes = _require_list(root, "makes", "$")
    engine_records = 0

    for make_index, make_value in enumerate(makes):
        make_path = f"$.makes[{make_index}]"
        make = _require_object(make_value, make_path)
        _require_name(make, make_path)
        models = _require_list(make, "models", make_path)

        for model_index, model_value in enumerate(models):
            model_path = f"{make_path}.models[{model_index}]"
            model = _require_object(model_value, model_path)
            _require_name(model, model_path)
            generations = _require_list(model, "generations", model_path)

            for generation_index, generation_value in enumerate(generations):
                generation_path = f"{model_path}.generations[{generation_index}]"
                generation = _require_object(generation_value, generation_path)
                _require_name(generation, generation_path)
                engines = _require_list(generation, "engines", generation_path)

                for engine_index, engine_value in enumerate(engines):
                    engine_path = f"{generation_path}.engines[{engine_index}]"
                    engine = _require_object(engine_value, engine_path)
                    _require_engine_label(engine, engine_path)
                    engine_records += 1

    if engine_records == 0:
        raise ValueError("structured snapshot must contain at least one engine record")


def _first_not_none(primary: Any, fallback: Any) -> Any:
    return primary if primary is not None else fallback


def _candidate(
    *,
    entity_id: str,
    evidence_id: str,
    pointer: str,
    attribute: str,
    value: Any,
    unit: str | None = None,
) -> CandidateFact:
    normalized = normalize_fact(attribute, value, unit)
    return CandidateFact(
        id=_stable_id("candidate", f"{pointer}|{attribute}"),
        entity_candidate_id=entity_id,
        attribute=attribute,
        raw_value=value,
        normalized_value=normalized.value,
        unit=normalized.unit,
        evidence_id=evidence_id,
        extraction_method=EXTRACTION_METHOD,
        confidence=None,
        normalization_rule=normalized.rule,
    )


def ingest_vehicle_makes_models_json(
    store: EvidenceStore,
    path: str | Path,
    *,
    acquired_at: datetime | None = None,
) -> IngestionReport:
    source_path = Path(path)
    payload = json.loads(
        source_path.read_text(encoding="utf-8"),
        parse_constant=_reject_non_standard_json_constant,
    )
    _validate_vehicle_makes_models_payload(payload)
    raw_content_ref = content_addressed_ref(source_path)
    acquired_at = acquired_at or datetime.now(timezone.utc)

    make_count = model_count = generation_count = 0
    entity_count = evidence_count = fact_count = 0

    with store.transaction():
        store.save_source(Source(SOURCE_ID, SOURCE_NAME, SOURCE_LOCATOR))

        for make_index, make in enumerate(payload["makes"]):
            make_count += 1
            make_name = make["name"]

            for model_index, model in enumerate(make["models"]):
                model_count += 1
                model_name = model["name"]

                for generation_index, generation in enumerate(model["generations"]):
                    generation_count += 1
                    generation_name = generation["name"]

                    for engine_index, engine in enumerate(generation["engines"]):
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
                                powertrain=engine["label"],
                                year_from=_first_not_none(
                                    generation.get("yearStart"), model.get("yearStart")
                                ),
                                year_to=_first_not_none(
                                    generation.get("yearEnd"), model.get("yearEnd")
                                ),
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
                                raw_content_ref=raw_content_ref,
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
