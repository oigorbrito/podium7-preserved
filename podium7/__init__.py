from .domain import (
    AutomotiveIdentity,
    CandidateFact,
    CanonicalFact,
    Conflict,
    ConflictState,
    DecisionStatus,
    EntityKind,
    ProvenanceRecord,
    RawEvidence,
    Source,
)
from .ingestion import IngestionReport, ingest_vehicle_makes_models_json
from .normalization import NormalizationResult, normalize_fact
from .persistence import EvidenceStore

__all__ = [
    "AutomotiveIdentity",
    "CandidateFact",
    "CanonicalFact",
    "Conflict",
    "ConflictState",
    "DecisionStatus",
    "EntityKind",
    "EvidenceStore",
    "IngestionReport",
    "NormalizationResult",
    "ProvenanceRecord",
    "RawEvidence",
    "Source",
    "ingest_vehicle_makes_models_json",
    "normalize_fact",
]
