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
- full discovered suite: 122/122 PASS, executed one test case per Python process

## Execution note

The earlier mirror-only limitation is closed. On 2026-08-19 the repository was cloned to `C:\Projetos\p7` on Windows with Python 3.13 and `python scripts\run_tests_one_by_one.py` completed all 122 discovered tests successfully, one process per test case. The sequential runner remains the canonical local/CI test command.
