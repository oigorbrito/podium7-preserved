from __future__ import annotations

from contextlib import contextmanager
import json
import sqlite3
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator

from .domain import (
    AutomotiveIdentity,
    CandidateFact,
    CanonicalFact,
    Conflict,
    ConflictState,
    EntityKind,
    ProvenanceRecord,
    RawEvidence,
    Source,
)


class EvidenceStore:
    """SQLite-backed persistence for Podium 7 domain records.

    SQLite is an ENGINEERING_CHOICE for the first vertical slice. The store
    preserves source, evidence, candidates, canonical decisions, conflicts,
    and provenance as independently addressable records so downstream logic
    can be re-run without reacquiring the original source.
    """

    def __init__(self, database: str | Path = ":memory:") -> None:
        self._connection = sqlite3.connect(str(database))
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._transaction_depth = 0
        self._savepoint_counter = 0
        self._create_schema()

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> "EvidenceStore":
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.close()

    @contextmanager
    def transaction(self) -> Iterator["EvidenceStore"]:
        """Group persistence operations atomically, including nested units."""

        outermost = self._transaction_depth == 0
        savepoint: str | None = None
        if outermost:
            self._connection.execute("BEGIN")
        else:
            self._savepoint_counter += 1
            savepoint = f"podium7_sp_{self._savepoint_counter}"
            self._connection.execute(f"SAVEPOINT {savepoint}")

        self._transaction_depth += 1
        try:
            yield self
        except Exception:
            self._transaction_depth -= 1
            if outermost:
                self._connection.rollback()
            else:
                assert savepoint is not None
                self._connection.execute(f"ROLLBACK TO SAVEPOINT {savepoint}")
                self._connection.execute(f"RELEASE SAVEPOINT {savepoint}")
            raise
        else:
            self._transaction_depth -= 1
            if outermost:
                self._connection.commit()
            else:
                assert savepoint is not None
                self._connection.execute(f"RELEASE SAVEPOINT {savepoint}")

    def _create_schema(self) -> None:
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS sources (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                locator TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS automotive_entities (
                id TEXT PRIMARY KEY,
                kind TEXT NOT NULL,
                make TEXT NOT NULL,
                model TEXT,
                generation TEXT,
                variant TEXT,
                powertrain TEXT,
                market TEXT,
                year_from INTEGER,
                year_to INTEGER,
                aliases_json TEXT NOT NULL,
                engine_identifiers_json TEXT NOT NULL,
                external_identifiers_json TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS raw_evidence (
                id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                locator TEXT NOT NULL,
                retrieved_at TEXT NOT NULL,
                acquisition_method TEXT NOT NULL,
                raw_content_ref TEXT NOT NULL,
                FOREIGN KEY (source_id) REFERENCES sources(id)
            );

            CREATE TABLE IF NOT EXISTS candidate_facts (
                id TEXT PRIMARY KEY,
                entity_candidate_id TEXT NOT NULL,
                attribute TEXT NOT NULL,
                raw_value_json TEXT NOT NULL,
                normalized_value_json TEXT NOT NULL,
                unit TEXT,
                evidence_id TEXT NOT NULL,
                extraction_method TEXT NOT NULL,
                confidence REAL,
                normalization_rule TEXT,
                FOREIGN KEY (entity_candidate_id) REFERENCES automotive_entities(id),
                FOREIGN KEY (evidence_id) REFERENCES raw_evidence(id)
            );

            CREATE TABLE IF NOT EXISTS provenance (
                id TEXT PRIMARY KEY,
                entity_id TEXT NOT NULL,
                activity_id TEXT NOT NULL,
                agent_id TEXT,
                was_derived_from_json TEXT NOT NULL,
                was_generated_by TEXT,
                was_associated_with TEXT,
                FOREIGN KEY (entity_id) REFERENCES automotive_entities(id)
            );

            CREATE TABLE IF NOT EXISTS canonical_facts (
                id TEXT PRIMARY KEY,
                entity_id TEXT NOT NULL,
                attribute TEXT NOT NULL,
                accepted_value_json TEXT NOT NULL,
                candidate_references_json TEXT NOT NULL,
                fusion_decision TEXT NOT NULL,
                provenance_id TEXT NOT NULL,
                FOREIGN KEY (entity_id) REFERENCES automotive_entities(id),
                FOREIGN KEY (provenance_id) REFERENCES provenance(id)
            );

            CREATE TABLE IF NOT EXISTS conflicts (
                id TEXT PRIMARY KEY,
                attribute TEXT NOT NULL,
                candidate_references_json TEXT NOT NULL,
                reason TEXT NOT NULL,
                resolution_state TEXT NOT NULL,
                selected_candidate_id TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_evidence_source ON raw_evidence(source_id);
            CREATE INDEX IF NOT EXISTS idx_candidate_entity ON candidate_facts(entity_candidate_id);
            CREATE INDEX IF NOT EXISTS idx_candidate_evidence ON candidate_facts(evidence_id);
            CREATE INDEX IF NOT EXISTS idx_canonical_entity ON canonical_facts(entity_id);
            """
        )
        self._connection.commit()

    def save_source(self, source: Source) -> None:
        self._insert_once(
            "INSERT INTO sources(id, name, locator) VALUES (?, ?, ?)",
            (source.id, source.name, source.locator),
        )

    def save_entity(self, entity_id: str, identity: AutomotiveIdentity) -> None:
        self._insert_once(
            """INSERT INTO automotive_entities(
                id, kind, make, model, generation, variant, powertrain, market,
                year_from, year_to, aliases_json, engine_identifiers_json,
                external_identifiers_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                entity_id,
                identity.kind.value,
                identity.make,
                identity.model,
                identity.generation,
                identity.variant,
                identity.powertrain,
                identity.market,
                identity.year_from,
                identity.year_to,
                self._json(identity.aliases),
                self._json(identity.engine_identifiers),
                self._json(identity.external_identifiers),
            ),
        )

    def save_raw_evidence(self, evidence: RawEvidence) -> None:
        self._insert_once(
            """INSERT INTO raw_evidence(
                id, source_id, locator, retrieved_at, acquisition_method,
                raw_content_ref
            ) VALUES (?, ?, ?, ?, ?, ?)""",
            (
                evidence.id,
                evidence.source_id,
                evidence.locator,
                evidence.retrieved_at.isoformat(),
                evidence.acquisition_method,
                evidence.raw_content_ref,
            ),
        )

    def save_candidate_fact(self, fact: CandidateFact) -> None:
        self._insert_once(
            """INSERT INTO candidate_facts(
                id, entity_candidate_id, attribute, raw_value_json,
                normalized_value_json, unit, evidence_id, extraction_method,
                confidence, normalization_rule
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                fact.id,
                fact.entity_candidate_id,
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

    def save_provenance(self, provenance_id: str, record: ProvenanceRecord) -> None:
        self._insert_once(
            """INSERT INTO provenance(
                id, entity_id, activity_id, agent_id, was_derived_from_json,
                was_generated_by, was_associated_with
            ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                provenance_id,
                record.entity_id,
                record.activity_id,
                record.agent_id,
                self._json(record.was_derived_from),
                record.was_generated_by,
                record.was_associated_with,
            ),
        )

    def save_canonical_fact(self, fact: CanonicalFact, provenance_id: str) -> None:
        with self.transaction():
            self._require_candidate_references(fact.candidate_references)
            self._require_candidate_attribute(fact.candidate_references, fact.attribute)
            self.save_provenance(provenance_id, fact.provenance)
            self._insert_once(
                """INSERT INTO canonical_facts(
                    id, entity_id, attribute, accepted_value_json,
                    candidate_references_json, fusion_decision, provenance_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    fact.id,
                    fact.entity_id,
                    fact.attribute,
                    self._json(fact.accepted_value),
                    self._json(fact.candidate_references),
                    fact.fusion_decision,
                    provenance_id,
                ),
            )

    def save_conflict(self, conflict: Conflict) -> None:
        self._require_candidate_references(conflict.candidate_references)
        self._require_candidate_attribute(conflict.candidate_references, conflict.attribute)
        self._insert_once(
            """INSERT INTO conflicts(
                id, attribute, candidate_references_json, reason,
                resolution_state, selected_candidate_id
            ) VALUES (?, ?, ?, ?, ?, ?)""",
            (
                conflict.id,
                conflict.attribute,
                self._json(conflict.candidate_references),
                conflict.reason,
                conflict.resolution_state.value,
                conflict.selected_candidate_id,
            ),
        )

    def get_source(self, source_id: str) -> Source | None:
        row = self._one("SELECT * FROM sources WHERE id = ?", (source_id,))
        return None if row is None else Source(row["id"], row["name"], row["locator"])

    def get_entity(self, entity_id: str) -> AutomotiveIdentity | None:
        row = self._one("SELECT * FROM automotive_entities WHERE id = ?", (entity_id,))
        if row is None:
            return None
        return AutomotiveIdentity(
            kind=EntityKind(row["kind"]),
            make=row["make"],
            model=row["model"],
            generation=row["generation"],
            variant=row["variant"],
            powertrain=row["powertrain"],
            market=row["market"],
            year_from=row["year_from"],
            year_to=row["year_to"],
            aliases=tuple(json.loads(row["aliases_json"])),
            engine_identifiers=tuple(json.loads(row["engine_identifiers_json"])),
            external_identifiers=tuple(json.loads(row["external_identifiers_json"])),
        )

    def get_raw_evidence(self, evidence_id: str) -> RawEvidence | None:
        row = self._one("SELECT * FROM raw_evidence WHERE id = ?", (evidence_id,))
        if row is None:
            return None
        return RawEvidence(
            id=row["id"],
            source_id=row["source_id"],
            locator=row["locator"],
            retrieved_at=datetime.fromisoformat(row["retrieved_at"]),
            acquisition_method=row["acquisition_method"],
            raw_content_ref=row["raw_content_ref"],
        )

    def get_candidate_fact(self, fact_id: str) -> CandidateFact | None:
        row = self._one("SELECT * FROM candidate_facts WHERE id = ?", (fact_id,))
        if row is None:
            return None
        return CandidateFact(
            id=row["id"],
            entity_candidate_id=row["entity_candidate_id"],
            attribute=row["attribute"],
            raw_value=json.loads(row["raw_value_json"]),
            normalized_value=json.loads(row["normalized_value_json"]),
            unit=row["unit"],
            evidence_id=row["evidence_id"],
            extraction_method=row["extraction_method"],
            confidence=row["confidence"],
            normalization_rule=row["normalization_rule"],
        )

    def get_provenance(self, provenance_id: str) -> ProvenanceRecord | None:
        row = self._one("SELECT * FROM provenance WHERE id = ?", (provenance_id,))
        if row is None:
            return None
        return ProvenanceRecord(
            entity_id=row["entity_id"],
            activity_id=row["activity_id"],
            agent_id=row["agent_id"],
            was_derived_from=tuple(json.loads(row["was_derived_from_json"])),
            was_generated_by=row["was_generated_by"],
            was_associated_with=row["was_associated_with"],
        )

    def get_canonical_fact(self, fact_id: str) -> CanonicalFact | None:
        row = self._one("SELECT * FROM canonical_facts WHERE id = ?", (fact_id,))
        if row is None:
            return None
        provenance = self.get_provenance(row["provenance_id"])
        if provenance is None:
            raise RuntimeError(f"canonical fact {fact_id!r} references missing provenance")
        return CanonicalFact(
            id=row["id"],
            entity_id=row["entity_id"],
            attribute=row["attribute"],
            accepted_value=json.loads(row["accepted_value_json"]),
            candidate_references=tuple(json.loads(row["candidate_references_json"])),
            fusion_decision=row["fusion_decision"],
            provenance=provenance,
        )

    def get_conflict(self, conflict_id: str) -> Conflict | None:
        row = self._one("SELECT * FROM conflicts WHERE id = ?", (conflict_id,))
        if row is None:
            return None
        return Conflict(
            id=row["id"],
            attribute=row["attribute"],
            candidate_references=tuple(json.loads(row["candidate_references_json"])),
            reason=row["reason"],
            resolution_state=ConflictState(row["resolution_state"]),
            selected_candidate_id=row["selected_candidate_id"],
        )

    def evidence_for_source(self, source_id: str) -> list[RawEvidence]:
        rows = self._connection.execute(
            "SELECT id FROM raw_evidence WHERE source_id = ? ORDER BY retrieved_at, id",
            (source_id,),
        ).fetchall()
        return [self.get_raw_evidence(row["id"]) for row in rows if row is not None]

    def candidates_for_entity(self, entity_id: str) -> list[CandidateFact]:
        rows = self._connection.execute(
            "SELECT id FROM candidate_facts WHERE entity_candidate_id = ? ORDER BY id",
            (entity_id,),
        ).fetchall()
        return [self.get_candidate_fact(row["id"]) for row in rows if row is not None]

    def canonical_facts_for_entity(self, entity_id: str) -> list[CanonicalFact]:
        rows = self._connection.execute(
            "SELECT id FROM canonical_facts WHERE entity_id = ? ORDER BY id",
            (entity_id,),
        ).fetchall()
        return [self.get_canonical_fact(row["id"]) for row in rows if row is not None]

    def snapshot_counts(self) -> dict[str, int]:
        tables = (
            "sources",
            "automotive_entities",
            "raw_evidence",
            "candidate_facts",
            "provenance",
            "canonical_facts",
            "conflicts",
        )
        return {
            table: self._connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in tables
        }

    def _require_candidate_references(self, references: tuple[str, ...]) -> None:
        placeholders = ",".join("?" for _ in references)
        rows = self._connection.execute(
            f"SELECT id FROM candidate_facts WHERE id IN ({placeholders})",
            references,
        ).fetchall()
        existing = {row["id"] for row in rows}
        missing = [reference for reference in references if reference not in existing]
        if missing:
            raise ValueError(
                "persistence integrity error: missing candidate references: "
                + ", ".join(missing)
            )

    def _require_candidate_attribute(self, references: tuple[str, ...], attribute: str) -> None:
        placeholders = ",".join("?" for _ in references)
        rows = self._connection.execute(
            f"SELECT id, attribute FROM candidate_facts WHERE id IN ({placeholders})",
            references,
        ).fetchall()
        mismatched = [row["id"] for row in rows if row["attribute"] != attribute]
        if mismatched:
            raise ValueError(
                f"persistence integrity error: candidate references do not match attribute {attribute!r}: "
                + ", ".join(mismatched)
            )

    def _insert_once(self, sql: str, values: tuple[Any, ...]) -> None:
        try:
            self._connection.execute(sql, values)
            if self._transaction_depth == 0:
                self._connection.commit()
        except sqlite3.IntegrityError as exc:
            if self._transaction_depth == 0:
                self._connection.rollback()
            raise ValueError(f"persistence integrity error: {exc}") from exc

    def _one(self, sql: str, values: tuple[Any, ...]) -> sqlite3.Row | None:
        return self._connection.execute(sql, values).fetchone()

    @staticmethod
    def _json(value: Any) -> str:
        if hasattr(value, "__dataclass_fields__"):
            value = asdict(value)
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"), default=str)
