# Production Operational Measurement V1

Status: implemented

This block measures the expanded 60-record source-backed replay after Product Corpus Run V2 without changing identity policy.

The measurement records total/created/matched/review/failed counts, automatic and review rates, persisted catalog size, action distribution by left/right benchmark side, durable open-review count, and classified review causes/reasons.

The bounded baseline is 60 records: 19 CREATED, 19 MATCHED, 22 REVIEW, zero failures, 19 persisted catalog vehicles, and 22 durable open review tasks. The automatic-path rate is 38/60 and the review rate is 22/60.

Review causes are derived from the actual candidate comparisons persisted in the durable review queue. Unknown review causes fail the regression test instead of being silently bucketed as acceptable behavior.

These numbers characterize this curated source-backed replay only. They are not a production-completeness, market-coverage, or independent field-accuracy claim. The next block uses the measured failure/review shape to prioritize an actionable operational gap.
