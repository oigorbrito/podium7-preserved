# Production Evidence Enrichment V2

Status: active

## Outcome

Reduce the bounded `REVIEW` load using explicit official evidence, with no resolver-policy change.

## Evidence target

The first V2 replay showed that enriching only the later Chevrolet Onix MY26 observation was insufficient: an earlier adjacent-year control had already created a deliberately sparse MY26 Premier canonical candidate. V2 therefore strengthens that earlier observation before ingestion using explicit official evidence: the MY26 price list supplies Premier 1.0 Turbo / six-speed automatic hatch fields, and Chevrolet's retained generation history supplies `2nd generation`. The later incomplete observation is enriched from the same MY26 price list.

## Boundaries

- Do not transfer fields across model years or trims.
- Do not use range-level transmission choices as trim-specific proof.
- Do not assign a model year to an observation whose source does not state one.
- Curated case provenance must explicitly include every source used by enrichment; a source outside the case `sourceIds` is rejected.
- Multiple evidence observations may enrich the same operational record only when their fields do not overlap.
- Keep Ford, Porsche, T-Cross and generic/missing-trim cases in `REVIEW` unless evidence closes the exact missing identity dimension.
- Preserve the Senatran-aligned year policy and all Catalog Identity V2 safety checks.

## Acceptance

- V2 enrichment observations have zero incorrect effects and zero resolver-policy changes.
- 60-record replay: 19 CREATED, 22 MATCHED, 19 REVIEW, 0 failed.
- Remaining review causes: 10 `MISSING_IDENTITY_EVIDENCE`, 9 `LABEL_AMBIGUITY`, no unknown causes.
- Auto-match precision and recall remain 1.0.
- False merges and ambiguous overcommit remain zero.
- Official repository CI passes before squash merge.
