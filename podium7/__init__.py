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
from .export import export_entity_json, export_entity_payload, write_entity_json
from .fusion import FusionResult, fuse_candidates
from .identity import MatchOutcome, ResolutionDecision, blocking_key, generate_candidates, resolve_pair
from .ingestion import IngestionReport, ingest_vehicle_makes_models_json
from .normalization import NormalizationResult, normalize_fact
from .persistence import EvidenceStore
from .web_extraction import ExtractedWebFact, WebFieldRule, extract_autoevolution_artega_gt, extract_with_rules

__all__ = [
    "AutomotiveIdentity",
    "CandidateFact",
    "CanonicalFact",
    "Conflict",
    "ConflictState",
    "DecisionStatus",
    "EntityKind",
    "EvidenceStore",
    "ExtractedWebFact",
    "FusionResult",
    "IngestionReport",
    "MatchOutcome",
    "NormalizationResult",
    "ProvenanceRecord",
    "RawEvidence",
    "ResolutionDecision",
    "Source",
    "WebFieldRule",
    "blocking_key",
    "export_entity_json",
    "export_entity_payload",
    "extract_autoevolution_artega_gt",
    "extract_with_rules",
    "fuse_candidates",
    "generate_candidates",
    "ingest_vehicle_makes_models_json",
    "normalize_fact",
    "resolve_pair",
    "write_entity_json",
]
