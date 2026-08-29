# Review Provenance Retention Note

Status: completed

Decision: ADAPT

Reason: Podium 7 already had a durable review queue in `CatalogReviewQueue` backed by `catalog_v2_review_tasks`. The smallest safe retention was an additive, immutable bindings table written in the same transaction as the review task rather than a new provenance subsystem or resolver change.

Integrated by PR #178.

Preserved constraints:
- MATCH/REVIEW/NO_MATCH semantics are unchanged;
- only explicit prospective review-side bindings are retained;
- partial persistence remains fail-closed;
- legacy reviews without bindings remain explicit and are not silently reconstructed;
- no historical provenance backfill is inferred.

Subsequent operational provenance work (#167, #196, #142) narrows which retained record sides may be replayed when source attribution is defensible. That does not authorize reconstructing missing historical review-side provenance.
