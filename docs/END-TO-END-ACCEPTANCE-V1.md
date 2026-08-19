# Podium 7 End-to-End Acceptance V1

**Work unit:** `PODIUM7_END_TO_END_ACCEPTANCE_V1`

The acceptance slice uses two real-source snapshots for the same Artega GT: the structured `vehicle-makes-models` JSON and the verified Autoevolution web spec snapshot.

## Path exercised

`multi-source evidence -> structured/web extraction -> normalization -> entity resolution -> fusion -> canonical facts -> provenance -> JSON export`

The structured source contributes two persisted raw evidence records (GT and Scalo); the web source contributes one additional raw evidence record. The GT identities resolve to `MATCH`. Twelve overlapping normalized attributes agree and fuse into canonical facts with no conflict in this slice.

## Gate

- `REAL_DATA = YES`
- `MULTI_SOURCE = YES`
- `RAW_EVIDENCE = PRESERVED`
- `NORMALIZATION = PASS`
- `ENTITY_RESOLUTION = PASS`
- `CONFLICT_HANDLING = PASS`
- `PROVENANCE = PASS`
- `EXPORT = PASS`
- `REPRODUCIBLE = PASS`
- acceptance test: PASS, run individually
- cumulative tests introduced and executed individually: 56/56 PASS

## Execution note

The environment did not provide the `gh` CLI, so the final E2E test was executed against a local compatible mirror of the published modules and fixtures. The implementation and acceptance test themselves are committed to the repository.
