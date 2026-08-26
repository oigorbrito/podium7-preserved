# Operational Field Provenance V1

Status: implementation prepared; corpus attribution pending
Issue: #166
Parent: #139
Depends on: #145
Blocks: #140 / #141 full operational replay

## Outcome

Prevent benchmark case-level source lists from being promoted into record-level provenance by position. Operational replay may construct a single-source batch record only when explicit `fieldSourceIds` prove that one source is common to every present field on that side.

## Acceptance

- no `sourceIds[0]` fallback;
- every replayed record has explicit field-level attribution;
- missing attribution fails closed;
- no common source across all fields fails closed;
- multiple fully covering sources remain ambiguous rather than selecting one;
- source/evidence/resolver/fusion/publication policy is unchanged.

## Boundary

`CatalogBatchEnvelope` binds exactly one `Source` and one `RawEvidence` to a vehicle observation. This block does not create a composite source or multi-source envelope. A side assembled from multiple sources therefore remains non-replayable through this path until a separately justified evidence model exists.

## Validation

Focused deterministic tests cover positional-source independence, missing field provenance, incompatible field-source coverage and multiple fully covering sources. The retained V3 corpus currently has no populated `fieldSourceIds`; full #140/#141 replay remains PENDING until attribution is reconstructed from retained primary evidence. GitHub-hosted executable validation is independently blocked by #112.
