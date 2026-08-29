# Review Provenance Retention Note

Status: active

Decision: ADAPT

Reason: Podium 7 already has a durable review queue in `CatalogReviewQueue` backed by `catalog_v2_review_tasks`. The smallest safe retention is an additive, immutable bindings table written in the same transaction as the review task, rather than a new provenance subsystem or resolver change.

Constraints:
- preserve MATCH/REVIEW/NO_MATCH semantics;
- retain explicit review-side bindings only;
- remain fail-closed on partial persistence;
- keep legacy reviews explicit when bindings are absent.
