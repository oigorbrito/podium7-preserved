# Production Evidence Enrichment V2

Status: implemented

Evidence Enrichment V2 continues the bounded review-reduction cycle without changing Catalog Identity V2 resolver policy.

## Measured gap

The V1 enriched replay retained 21 `REVIEW` outcomes. The first V2 experiment enriched the later Chevrolet Onix Premier MY26 incomplete mechanical observation from the official MY26 price list. The isolated pair correctly changed `REVIEW -> MATCH`, but the shared operational replay remained at 21 reviews.

Replay diagnostics showed why: the earlier adjacent-year Onix MY26-vs-MY27 control had already created a deliberately sparse MY26 Premier canonical candidate. That candidate contained make, model, variant, market and model year, but lacked generation, body style, powertrain and transmission. Later complete MY26 observations correctly abstained rather than ignoring that earlier candidate.

## Source-backed correction

V2 enriches the sparse MY26 observation before ingestion. Its curated case provenance now explicitly includes:

- Chevrolet's official MY26 price list for Premier 1.0 Turbo, hatch body and six-speed automatic transmission;
- Chevrolet's official product history for the current Onix as second generation.

The later incomplete Premier MY26 observation receives only its missing powertrain and transmission from the same official MY26 price list.

The adjacent-year control remains `NO_MATCH` after enrichment because explicit MY2026 versus MY2027 non-overlap remains decisive under the selected Senatran-aligned year policy.

## Contract changes

`podium7.source_backed_enrichment` remains fail-closed and gains only two bounded capabilities:

- an explicit evidence addition may strengthen a `NO_MATCH` benchmark observation while preserving its expected `NO_MATCH` decision;
- multiple enrichment observations may target the same operational record only when their field sets do not overlap.

Every enrichment source must still be declared in that benchmark case's `sourceIds`. Sources outside the curated case are rejected. Existing identity fields cannot be overwritten.

`podium7.enrichment_quality` also exposes review reason and candidate-identity diagnostics keyed by evidence ID. These diagnostics explain operational abstention without changing any decision.

## Quality gate

The implemented V2 replay produces:

- 19 `CREATED`;
- 22 `MATCHED`;
- 19 `REVIEW`;
- 0 failed;
- 10 `MISSING_IDENTITY_EVIDENCE` reviews;
- 9 `LABEL_AMBIGUITY` reviews;
- no unknown review cause.

The companion source-backed identity-quality corpus remains at auto-match precision 1.0 and recall 1.0, with zero false merges and zero ambiguous overcommit. Resolver-policy changes remain zero.

## Nonclaims

This is a bounded operational replay, not a production-completeness or market-coverage claim. The remaining reviews are not assumed to be safely resolvable; additional reductions require new explicit source-backed evidence.
