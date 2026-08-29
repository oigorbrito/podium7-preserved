from .acceptance import AcceptanceReport, run_acceptance_slice
from .ai_discovery import ValidatedExtractionArtifact, validate_extraction_artifact
from .autonomy import AcquisitionCache, Checkpoint, EnrichmentJob, JobResult, JobState, RateLimiter, RetryPolicy, identify_gaps, plan_jobs, run_job
from .bound_http_acquisition import BoundNetworkTarget, acquire_bound_http, resolve_bound_target
from .document_extraction import DocumentExtractionReport, extract_ford_dark_horse_document
from .domain import AutomotiveIdentity, CandidateFact, CanonicalFact, Conflict, ConflictState, DecisionStatus, EntityKind, ProvenanceRecord, RawEvidence, Source
from .enrichment_contract import CONTRACT_FIELDS, CONTRACT_SCHEMA, EnrichmentContext, KnowledgeState, PublishedEnrichmentConflict, PublishedEnrichmentFact, ValueShape, publish_enrichment_json, publish_enrichment_payload
from .export import export_entity_json, export_entity_payload, write_entity_json
from .fusion import FusionResult, fuse_candidates
from .identity import MatchOutcome, ResolutionDecision, blocking_key, generate_candidates, resolve_pair
from .ingestion import IngestionReport, ingest_vehicle_makes_models_json
from .inmetro_pbev import InmetroPbevRecord, acquire_inmetro_pbev_pdf, extract_inmetro_pbev_pdf, extract_inmetro_pbev_tables, inmetro_pdf_policy
from .normalization import NormalizationResult, normalize_fact
from .official_discovery import DiscoveryCandidate, build_fueleconomy_model_menu_locator, build_fueleconomy_options_menu_locator, build_nhtsa_models_locator, discover_fueleconomy_models, discover_fueleconomy_vehicle_options, discover_nhtsa_models
from .persistence import EvidenceStore
from .review import ReviewAction, ReviewDecision, review_conflict, review_evidence, review_identity
from .source_policy import RecurringSourceGate, RobotsMode, SourceOperationDecision, SourceOperationPolicy
from .web_extraction import ExtractedWebFact, WebFieldRule, extract_autoevolution_artega_gt, extract_with_rules

__all__ = [
    "AcceptanceReport", "AcquisitionCache", "AutomotiveIdentity", "BoundNetworkTarget", "CandidateFact", "CanonicalFact", "Checkpoint",
    "CONTRACT_FIELDS", "CONTRACT_SCHEMA", "Conflict", "ConflictState", "DecisionStatus", "DiscoveryCandidate", "DocumentExtractionReport", "EnrichmentContext", "EnrichmentJob",
    "EntityKind", "EvidenceStore", "ExtractedWebFact", "FusionResult", "IngestionReport", "InmetroPbevRecord",
    "JobResult", "JobState", "KnowledgeState", "MatchOutcome", "NormalizationResult", "ProvenanceRecord", "PublishedEnrichmentConflict", "PublishedEnrichmentFact",
    "RateLimiter", "RawEvidence", "RecurringSourceGate", "ResolutionDecision", "RetryPolicy", "ReviewAction",
    "ReviewDecision", "RobotsMode", "Source", "SourceOperationDecision", "SourceOperationPolicy", "ValidatedExtractionArtifact", "ValueShape", "WebFieldRule", "acquire_bound_http", "acquire_inmetro_pbev_pdf", "blocking_key",
    "build_fueleconomy_model_menu_locator", "build_fueleconomy_options_menu_locator", "build_nhtsa_models_locator",
    "discover_fueleconomy_models", "discover_fueleconomy_vehicle_options", "discover_nhtsa_models",
    "export_entity_json", "export_entity_payload", "extract_autoevolution_artega_gt",
    "extract_ford_dark_horse_document", "extract_inmetro_pbev_pdf", "extract_inmetro_pbev_tables", "extract_with_rules", "fuse_candidates", "generate_candidates",
    "identify_gaps", "ingest_vehicle_makes_models_json", "inmetro_pdf_policy", "normalize_fact", "plan_jobs", "publish_enrichment_json", "publish_enrichment_payload", "resolve_bound_target",
    "resolve_pair", "review_conflict", "review_evidence", "review_identity", "run_acceptance_slice",
    "run_job", "validate_extraction_artifact", "write_entity_json",
]
