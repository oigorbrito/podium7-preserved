from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
import json
import re
import uuid
from typing import Any

from .domain import CandidateFact, CanonicalFact, Conflict
from .persistence import EvidenceStore


CATALOG_SCHEMA_VERSION = 1


class CatalogMatchOutcome(str, Enum):
    MATCH = "MATCH"
    NO_MATCH = "NO_MATCH"
    REVIEW = "REVIEW"


@dataclass(frozen=True, order=True)
class ExternalIdentifier:
    namespace: str
    value: str

    def __post_init__(self) -> None:
        if not self.namespace.strip() or not self.value.strip():
            raise ValueError("external identifier namespace and value are required")

    @property
    def key(self) -> tuple[str, str]:
        return self.namespace.casefold().strip(), self.value.casefold().strip()


@dataclass(frozen=True)
class CatalogVehicleIdentity:
    make: str
    model: str
    generation: str | None = None
    variant: str | None = None
    powertrain: str | None = None
    transmission: str | None = None
    body_style: str | None = None
    market: str | None = None
    manufacture_year_from: int | None = None
    manufacture_year_to: int | None = None
    model_year_from: int | None = None
    model_year_to: int | None = None
    aliases: tuple[str, ...] = ()
    engine_identifiers: tuple[str, ...] = ()
    external_identifiers: tuple[ExternalIdentifier, ...] = ()

    def __post_init__(self) -> None:
        if not self.make.strip() or not self.model.strip():
            raise ValueError("catalog make and model are required")
        for field in ("generation", "variant", "powertrain", "transmission", "body_style", "market"):
            value = getattr(self, field)
            if value is not None and not value.strip():
                raise ValueError(f"{field} must be non-empty when provided")
        for start, end, label in (
            (self.manufacture_year_from, self.manufacture_year_to, "manufacture year"),
            (self.model_year_from, self.model_year_to, "model year"),
        ):
            for value in (start, end):
                if value is not None and (not isinstance(value, int) or isinstance(value, bool)):
                    raise ValueError(f"{label} must be an integer")
            if start is not None and end is not None and start > end:
                raise ValueError(f"{label} start cannot exceed end")
        if any(not value.strip() for value in self.aliases + self.engine_identifiers):
            raise ValueError("aliases and engine identifiers must be non-empty")
        if len(set(self.aliases)) != len(self.aliases):
            raise ValueError("aliases must be unique")
        keys = [value.key for value in self.external_identifiers]
        if len(set(keys)) != len(keys):
            raise ValueError("external identifiers must be unique by namespace and value")


@dataclass(frozen=True)
class CatalogResolutionDecision:
    outcome: CatalogMatchOutcome
    reason: str


@dataclass(frozen=True)
class PhysicalVehicleListing:
    listing_id: str
    catalog_vehicle_id: str
    source_id: str
    odometer_km: int | None = None
    vin: str | None = None

    def __post_init__(self) -> None:
        if not self.listing_id.strip() or not self.catalog_vehicle_id.strip() or not self.source_id.strip():
            raise ValueError("listing id, catalog vehicle id and source id are required")
        if self.odometer_km is not None and (
            not isinstance(self.odometer_km, int)
            or isinstance(self.odometer_km, bool)
            or self.odometer_km < 0
        ):
            raise ValueError("odometer_km must be a non-negative integer")
        if self.vin is not None and not self.vin.strip():
            raise ValueError("vin must be non-empty when provided")


def _tokens(value: str | None) -> tuple[str, ...] | None:
    if value is None:
        return None
    tokens = re.findall(r"[a-z0-9]+", value.casefold())
    return tuple(sorted(tokens)) or None


def _labels(identity: CatalogVehicleIdentity) -> set[tuple[str, ...]]:
    labels = {_tokens(identity.model)}
    labels.update(_tokens(alias) for alias in identity.aliases)
    return {label for label in labels if label is not None}


def _optional_equal(a: str | None, b: str | None) -> bool | None:
    if a is None or b is None:
        return None
    return _tokens(a) == _tokens(b)


def _ranges_overlap(
    a_from: int | None,
    a_to: int | None,
    b_from: int | None,
    b_to: int | None,
) -> bool | None:
    if None in (a_from, a_to, b_from, b_to):
        return None
    return max(a_from, b_from) <= min(a_to, b_to)


def resolve_catalog_pair(
    a: CatalogVehicleIdentity,
    b: CatalogVehicleIdentity,
) -> CatalogResolutionDecision:
    if _tokens(a.make) != _tokens(b.make):
        return CatalogResolutionDecision(CatalogMatchOutcome.NO_MATCH, "make differs")

    labels_a, labels_b = _labels(a), _labels(b)
    if not labels_a.intersection(labels_b):
        partial = any(
            set(x).issubset(set(y)) or set(y).issubset(set(x))
            for x in labels_a
            for y in labels_b
        )
        if partial:
            return CatalogResolutionDecision(
                CatalogMatchOutcome.REVIEW,
                "model labels partially overlap",
            )
        return CatalogResolutionDecision(CatalogMatchOutcome.NO_MATCH, "model/alias differs")

    for field in ("generation", "variant", "powertrain", "transmission", "body_style", "market"):
        if _optional_equal(getattr(a, field), getattr(b, field)) is False:
            return CatalogResolutionDecision(CatalogMatchOutcome.NO_MATCH, f"{field} differs")

    for prefix in ("manufacture_year", "model_year"):
        overlap = _ranges_overlap(
            getattr(a, f"{prefix}_from"),
            getattr(a, f"{prefix}_to"),
            getattr(b, f"{prefix}_from"),
            getattr(b, f"{prefix}_to"),
        )
        if overlap is False:
            return CatalogResolutionDecision(
                CatalogMatchOutcome.NO_MATCH,
                f"{prefix} ranges do not overlap",
            )

    ids_a = {item.key for item in a.external_identifiers}
    ids_b = {item.key for item in b.external_identifiers}
    if ids_a.intersection(ids_b):
        return CatalogResolutionDecision(
            CatalogMatchOutcome.MATCH,
            "shared namespaced external identifier",
        )
    if ids_a and ids_b:
        return CatalogResolutionDecision(
            CatalogMatchOutcome.REVIEW,
            "external identifiers do not establish a shared identity",
        )

    if (
        a.generation is not None
        and b.generation is not None
        and a.powertrain is not None
        and b.powertrain is not None
    ):
        missing_trim = any(
            (getattr(a, field) is None) != (getattr(b, field) is None)
            for field in ("variant", "transmission", "body_style")
        )
        if missing_trim:
            return CatalogResolutionDecision(
                CatalogMatchOutcome.REVIEW,
                "trim-defining evidence is incomplete",
            )
        return CatalogResolutionDecision(
            CatalogMatchOutcome.MATCH,
            "same model, generation and powertrain without contradiction",
        )

    return CatalogResolutionDecision(
        CatalogMatchOutcome.REVIEW,
        "insufficient deterministic identity evidence",
    )


def _identity_json(identity: CatalogVehicleIdentity) -> str:
    return json.dumps(
        asdict(identity),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _identity_from_json(payload: str) -> CatalogVehicleIdentity:
    data = json.loads(payload)
    data["aliases"] = tuple(data.get("aliases", ()))
    data["engine_identifiers"] = tuple(data.get("engine_identifiers", ()))
    data["external_identifiers"] = tuple(
        ExternalIdentifier(**item) for item in data.get("external_identifiers", ())
    )
    return CatalogVehicleIdentity(**data)


class CatalogStore(EvidenceStore):
    """Additive V2 catalog persistence over the V1 evidence store."""

    def __init__(self, database: str = ":memory:") -> None:
        super().__init__(database)
        self._initialize_catalog_schema()

    @property
    def catalog_schema_version(self) -> int:
        row = self._connection.execute(
            "SELECT version FROM catalog_v2_schema_metadata WHERE component = 'catalog'"
        ).fetchone()
        return int(row[0])

    def _initialize_catalog_schema(self) -> None:
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS catalog_v2_schema_metadata (
                component TEXT PRIMARY KEY,
                version INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS catalog_v2_vehicles (
                id TEXT PRIMARY KEY,
                identity_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS catalog_v2_identity_revisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id TEXT NOT NULL REFERENCES catalog_v2_vehicles(id),
                identity_json TEXT NOT NULL,
                reason TEXT NOT NULL,
                recorded_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS catalog_v2_redirects (
                old_id TEXT PRIMARY KEY,
                canonical_id TEXT NOT NULL REFERENCES catalog_v2_vehicles(id),
                merged_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS catalog_v2_physical_listings (
                listing_id TEXT PRIMARY KEY,
                catalog_vehicle_id TEXT NOT NULL REFERENCES catalog_v2_vehicles(id),
                source_id TEXT NOT NULL REFERENCES sources(id),
                odometer_km INTEGER,
                vin TEXT
            );
            CREATE TABLE IF NOT EXISTS catalog_v2_candidate_facts (
                id TEXT PRIMARY KEY,
                entity_id TEXT NOT NULL REFERENCES catalog_v2_vehicles(id),
                attribute TEXT NOT NULL,
                raw_value_json TEXT NOT NULL,
                normalized_value_json TEXT NOT NULL,
                unit TEXT,
                evidence_id TEXT NOT NULL REFERENCES raw_evidence(id),
                extraction_method TEXT NOT NULL,
                confidence REAL,
                normalization_rule TEXT
            );
            CREATE TABLE IF NOT EXISTS catalog_v2_provenance (
                id TEXT PRIMARY KEY,
                entity_id TEXT NOT NULL REFERENCES catalog_v2_vehicles(id),
                activity_id TEXT NOT NULL,
                agent_id TEXT,
                was_derived_from_json TEXT NOT NULL,
                was_generated_by TEXT,
                was_associated_with TEXT
            );
            CREATE TABLE IF NOT EXISTS catalog_v2_canonical_facts (
                id TEXT PRIMARY KEY,
                entity_id TEXT NOT NULL REFERENCES catalog_v2_vehicles(id),
                attribute TEXT NOT NULL,
                accepted_value_json TEXT NOT NULL,
                candidate_references_json TEXT NOT NULL,
                fusion_decision TEXT NOT NULL,
                provenance_id TEXT NOT NULL REFERENCES catalog_v2_provenance(id)
            );
            CREATE TABLE IF NOT EXISTS catalog_v2_conflicts (
                id TEXT PRIMARY KEY,
                entity_id TEXT NOT NULL REFERENCES catalog_v2_vehicles(id),
                attribute TEXT NOT NULL,
                candidate_references_json TEXT NOT NULL,
                reason TEXT NOT NULL,
                resolution_state TEXT NOT NULL,
                selected_candidate_id TEXT
            );
            """
        )
        row = self._connection.execute(
            "SELECT version FROM catalog_v2_schema_metadata WHERE component = 'catalog'"
        ).fetchone()
        if row is None:
            self._connection.execute(
                "INSERT INTO catalog_v2_schema_metadata(component, version) VALUES ('catalog', ?)",
                (CATALOG_SCHEMA_VERSION,),
            )
        elif int(row[0]) > CATALOG_SCHEMA_VERSION:
            raise ValueError(f"unsupported catalog schema version {row[0]}")
        self._connection.commit()

    def create_catalog_vehicle(self, identity: CatalogVehicleIdentity) -> str:
        vehicle_id = "veh_" + uuid.uuid4().hex
        now = datetime.now(timezone.utc).isoformat()
        self._insert_once(
            "INSERT INTO catalog_v2_vehicles(id, identity_json, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (vehicle_id, _identity_json(identity), now, now),
        )
        return vehicle_id

    def resolve_catalog_id(self, vehicle_id: str) -> str:
        seen: set[str] = set()
        current = vehicle_id
        while True:
            if current in seen:
                raise RuntimeError("catalog redirect cycle detected")
            seen.add(current)
            row = self._connection.execute(
                "SELECT canonical_id FROM catalog_v2_redirects WHERE old_id = ?",
                (current,),
            ).fetchone()
            if row is None:
                return current
            current = row[0]

    def get_catalog_vehicle(self, vehicle_id: str) -> CatalogVehicleIdentity | None:
        canonical = self.resolve_catalog_id(vehicle_id)
        row = self._connection.execute(
            "SELECT identity_json FROM catalog_v2_vehicles WHERE id = ?",
            (canonical,),
        ).fetchone()
        return None if row is None else _identity_from_json(row[0])

    def correct_catalog_vehicle(
        self,
        vehicle_id: str,
        identity: CatalogVehicleIdentity,
        reason: str,
    ) -> str:
        canonical = self.resolve_catalog_id(vehicle_id)
        if not reason.strip():
            raise ValueError("correction reason is required")
        row = self._connection.execute(
            "SELECT identity_json FROM catalog_v2_vehicles WHERE id = ?",
            (canonical,),
        ).fetchone()
        if row is None:
            raise ValueError("catalog vehicle does not exist")
        now = datetime.now(timezone.utc).isoformat()
        with self.transaction():
            self._insert_once(
                "INSERT INTO catalog_v2_identity_revisions(vehicle_id, identity_json, reason, recorded_at) VALUES (?, ?, ?, ?)",
                (canonical, row[0], reason, now),
            )
            self._connection.execute(
                "UPDATE catalog_v2_vehicles SET identity_json = ?, updated_at = ? WHERE id = ?",
                (_identity_json(identity), now, canonical),
            )
        return canonical

    def merge_catalog_vehicle_ids(self, survivor_id: str, duplicate_id: str) -> str:
        survivor = self.resolve_catalog_id(survivor_id)
        duplicate = self.resolve_catalog_id(duplicate_id)
        if survivor == duplicate:
            return survivor
        if self.get_catalog_vehicle(survivor) is None or self.get_catalog_vehicle(duplicate) is None:
            raise ValueError("both catalog vehicles must exist")
        now = datetime.now(timezone.utc).isoformat()
        with self.transaction():
            for table, column in (
                ("catalog_v2_identity_revisions", "vehicle_id"),
                ("catalog_v2_physical_listings", "catalog_vehicle_id"),
                ("catalog_v2_candidate_facts", "entity_id"),
                ("catalog_v2_provenance", "entity_id"),
                ("catalog_v2_canonical_facts", "entity_id"),
                ("catalog_v2_conflicts", "entity_id"),
            ):
                self._connection.execute(
                    f"UPDATE {table} SET {column} = ? WHERE {column} = ?",
                    (survivor, duplicate),
                )
            self._connection.execute(
                "UPDATE catalog_v2_redirects SET canonical_id = ? WHERE canonical_id = ?",
                (survivor, duplicate),
            )
            self._insert_once(
                "INSERT INTO catalog_v2_redirects(old_id, canonical_id, merged_at) VALUES (?, ?, ?)",
                (duplicate, survivor, now),
            )
            self._connection.execute(
                "DELETE FROM catalog_v2_vehicles WHERE id = ?",
                (duplicate,),
            )
        return survivor

    def save_physical_listing(self, listing: PhysicalVehicleListing) -> None:
        self._insert_once(
            "INSERT INTO catalog_v2_physical_listings(listing_id, catalog_vehicle_id, source_id, odometer_km, vin) VALUES (?, ?, ?, ?, ?)",
            (
                listing.listing_id,
                self.resolve_catalog_id(listing.catalog_vehicle_id),
                listing.source_id,
                listing.odometer_km,
                listing.vin,
            ),
        )

    def get_physical_listing(self, listing_id: str) -> PhysicalVehicleListing | None:
        row = self._connection.execute(
            "SELECT * FROM catalog_v2_physical_listings WHERE listing_id = ?",
            (listing_id,),
        ).fetchone()
        if row is None:
            return None
        return PhysicalVehicleListing(
            row["listing_id"],
            row["catalog_vehicle_id"],
            row["source_id"],
            row["odometer_km"],
            row["vin"],
        )

    def save_catalog_candidate_fact(self, fact: CandidateFact) -> None:
        self._insert_once(
            """INSERT INTO catalog_v2_candidate_facts(
                id, entity_id, attribute, raw_value_json, normalized_value_json, unit,
                evidence_id, extraction_method, confidence, normalization_rule
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                fact.id,
                self.resolve_catalog_id(fact.entity_candidate_id),
                fact.attribute,
                self._json(fact.raw_value),
                self._json(fact.normalized_value),
                fact.unit,
                fact.evidence_id,
                fact.extraction_method,
                fact.confidence,
                fact.normalization_rule,
            ),
        )

    def catalog_candidates_for_entity(self, vehicle_id: str) -> list[CandidateFact]:
        canonical = self.resolve_catalog_id(vehicle_id)
        rows = self._connection.execute(
            "SELECT * FROM catalog_v2_candidate_facts WHERE entity_id = ? ORDER BY id",
            (canonical,),
        ).fetchall()
        return [
            CandidateFact(
                id=row["id"],
                entity_candidate_id=canonical,
                attribute=row["attribute"],
                raw_value=json.loads(row["raw_value_json"]),
                normalized_value=json.loads(row["normalized_value_json"]),
                unit=row["unit"],
                evidence_id=row["evidence_id"],
                extraction_method=row["extraction_method"],
                confidence=row["confidence"],
                normalization_rule=row["normalization_rule"],
            )
            for row in rows
        ]

    def _require_catalog_candidate_references(
        self,
        vehicle_id: str,
        references: tuple[str, ...],
        attribute: str,
    ) -> str:
        canonical = self.resolve_catalog_id(vehicle_id)
        if not references:
            raise ValueError("catalog candidate references are required")
        if len(set(references)) != len(references):
            raise ValueError("catalog candidate references must be unique")
        placeholders = ",".join("?" for _ in references)
        rows = self._connection.execute(
            f"SELECT id, entity_id, attribute FROM catalog_v2_candidate_facts WHERE id IN ({placeholders})",
            references,
        ).fetchall()
        existing = {row["id"] for row in rows}
        missing = [reference for reference in references if reference not in existing]
        if missing:
            raise ValueError(
                "missing catalog candidate references: " + ", ".join(missing)
            )
        wrong_entity = [row["id"] for row in rows if row["entity_id"] != canonical]
        if wrong_entity:
            raise ValueError(
                "catalog candidate references belong to another vehicle: "
                + ", ".join(wrong_entity)
            )
        wrong_attribute = [row["id"] for row in rows if row["attribute"] != attribute]
        if wrong_attribute:
            raise ValueError(
                f"catalog candidate references do not match attribute {attribute!r}: "
                + ", ".join(wrong_attribute)
            )
        return canonical

    def save_catalog_canonical_fact(self, fact: CanonicalFact, provenance_id: str) -> None:
        refs = tuple(fact.candidate_references)
        canonical = self._require_catalog_candidate_references(
            fact.entity_id,
            refs,
            fact.attribute,
        )
        provenance = fact.provenance
        if self.resolve_catalog_id(provenance.entity_id) != canonical:
            raise ValueError("catalog canonical provenance belongs to another vehicle")
        with self.transaction():
            self._insert_once(
                """INSERT INTO catalog_v2_provenance(
                    id, entity_id, activity_id, agent_id, was_derived_from_json,
                    was_generated_by, was_associated_with
                ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    provenance_id,
                    canonical,
                    provenance.activity_id,
                    provenance.agent_id,
                    self._json(provenance.was_derived_from),
                    provenance.was_generated_by,
                    provenance.was_associated_with,
                ),
            )
            self._insert_once(
                """INSERT INTO catalog_v2_canonical_facts(
                    id, entity_id, attribute, accepted_value_json, candidate_references_json,
                    fusion_decision, provenance_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    fact.id,
                    canonical,
                    fact.attribute,
                    self._json(fact.accepted_value),
                    self._json(refs),
                    fact.fusion_decision,
                    provenance_id,
                ),
            )

    def save_catalog_conflict(self, vehicle_id: str, conflict: Conflict) -> None:
        refs = tuple(conflict.candidate_references)
        canonical = self._require_catalog_candidate_references(
            vehicle_id,
            refs,
            conflict.attribute,
        )
        self._insert_once(
            """INSERT INTO catalog_v2_conflicts(
                id, entity_id, attribute, candidate_references_json, reason,
                resolution_state, selected_candidate_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                conflict.id,
                canonical,
                conflict.attribute,
                self._json(refs),
                conflict.reason,
                conflict.resolution_state.value,
                conflict.selected_candidate_id,
            ),
        )

    def redirects_to(self, vehicle_id: str) -> list[str]:
        canonical = self.resolve_catalog_id(vehicle_id)
        rows = self._connection.execute(
            "SELECT old_id FROM catalog_v2_redirects WHERE canonical_id = ? ORDER BY old_id",
            (canonical,),
        ).fetchall()
        return [row[0] for row in rows]


def export_catalog_vehicle_payload(
    store: CatalogStore,
    vehicle_id: str,
) -> dict[str, Any]:
    canonical = store.resolve_catalog_id(vehicle_id)
    identity = store.get_catalog_vehicle(canonical)
    if identity is None:
        raise ValueError("catalog vehicle does not exist")
    data = asdict(identity)
    data["external_identifiers"] = [
        asdict(item) for item in identity.external_identifiers
    ]
    return {
        "contractVersion": "2.0",
        "entity": {"id": canonical, **data},
        "redirectsFrom": store.redirects_to(canonical),
    }


__all__ = [
    "CATALOG_SCHEMA_VERSION",
    "CatalogMatchOutcome",
    "CatalogResolutionDecision",
    "CatalogStore",
    "CatalogVehicleIdentity",
    "ExternalIdentifier",
    "PhysicalVehicleListing",
    "export_catalog_vehicle_payload",
    "resolve_catalog_pair",
]
