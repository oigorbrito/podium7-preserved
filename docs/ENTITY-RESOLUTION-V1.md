# Podium 7 Entity Resolution V1

**Work unit:** `PODIUM7_ENTITY_RESOLUTION_V1`

## Scientific basis

MaDI-Bench, KnowledgeNet, ComEM, and ALER establish entity resolution as a distinct capability. This implementation keeps blocking/candidate generation separate from matching/resolution.

## Decision classification

### `EVIDENCE_BACKED`
- blocking and matching are separate responsibilities;
- entity identity cannot be reduced to string equality;
- ambiguity must not be silently forced into a match.

### `ENGINEERING_CHOICE`
V1 uses deterministic signals: normalized make/model aliases, generation, year ranges, powertrain, and external identifiers.

## Outcomes

- `MATCH`
- `NO_MATCH`
- `UNRESOLVED`

`UNRESOLVED` is intentional when evidence is insufficient.

## Gate

- `NO_FORCED_MATCH_ON_AMBIGUITY = YES`
- mandatory domain scenarios: PASS
- entity-resolution tests: 6/6 PASS, executed individually
- cumulative repository tests executed individually so far: 22/22 PASS
