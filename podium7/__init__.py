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
from .identity import MatchOutcome, ResolutionDecision, blocking_key, generate_candidates, resolve_pair
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
    "MatchOutcome",
    "NormalizationResult",
    "ProvenanceRecord",
    "RawEvidence",
    "ResolutionDecision",
    "Source",
    "blocking_key",
    "generate_candidates",
    "ingest_vehicle_makes_models_json",
    "normalize_fact",
    "resolve_pair",
]
