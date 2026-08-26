# Donor capability evaluation execution plan V1

Status: active
Issue: #162

## Outcome

Evaluate external automotive/open-source donor capabilities against measured Podium 7 gaps before any adoption or rebuild, following ADR-0001 and preserving existing evidence/resolution policy.

## Acceptance criteria

- Primary upstream documentation supports each donor claim.
- License/reuse boundaries are recorded conservatively.
- Existing Podium overlap is reconstructed before declaring a gap.
- Only capabilities that close a measured or observable operational gap may produce implementation follow-up.
- No donor code/data/schema/policy is imported by this evaluation.

## Boundaries

- No evidence hierarchy, resolver, fusion, year, ambiguity, publication or source-policy changes.
- No adoption based on field count or convenience.
- No implementation work except separately authorized follow-up derived from the completed matrix.

## Evaluated donors

- VehiclesDB
- High Mobility Auto API
- OpenCars VIN Decoder

## Result

The durable comparison is `docs/DONOR-CAPABILITY-EVALUATION-V1.md`.

The only capability sufficiently distinct from current Podium behavior to justify an immediate focused follow-up is a source-specific license/reuse drift gate inspired by VehiclesDB's license-text pinning pattern. Human override layers and type-approval crosswalks remain pattern references pending measured need.
