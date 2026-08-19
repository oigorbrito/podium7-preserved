# Podium 7 First Real Structured Ingestion

**Work unit:** `PODIUM7_FIRST_REAL_STRUCTURED_INGESTION_V1`

## Source

The first source is the previously identified `vehicle-makes-models` dataset, specifically the pinned `data/json/artega.json` snapshot from `gor3a/vehicle-makes-models`.

This is one source only. No multi-source fusion is attempted in this work unit.

## Decision classification

### `EVIDENCE_BACKED`

- Structured ingestion is kept separate from later normalization, entity resolution, and fusion stages.
- Raw evidence is preserved alongside extracted candidate entities/facts.

### `ENGINEERING_CHOICE`

- Use the upstream per-make JSON representation.
- Pin the first real source snapshot into `data/raw/vehicle-makes-models/` so the exact acquisition input remains inspectable and reproducible.
- Represent each source engine/powertrain record as one `AutomotiveIdentity(kind=POWERTRAIN)` candidate entity.
- Generate deterministic identifiers from the source locator using SHA-256.
- Extract only explicitly structured top-level fields during this work unit.

### `UNKNOWN`

- Completeness and correctness of the upstream dataset.
- Authority of this source relative to future sources.
- Suitability of this source for markets not represented by its records.

## Pipeline implemented

`STRUCTURED JSON -> RAW SNAPSHOT -> RAW EVIDENCE -> AUTOMOTIVE ENTITY CANDIDATE -> CANDIDATE FACTS -> EvidenceStore`

The importer is implemented in `podium7/ingestion.py` and can be run with:

```bash
python -m podium7.ingestion data/raw/vehicle-makes-models/artega.json --database podium7.sqlite
```

## Normalization boundary

This work unit intentionally does not perform Work Unit 4 semantic normalization. The source already exposes several values in explicit units (`powerHp`, `torqueNm`, `lengthMm`, etc.), but the importer does not claim that carrying those values through unchanged is a normalization result.

Therefore candidate facts retain:

- the structured source value as `raw_value`;
- the same value in the currently required `normalized_value` slot;
- `normalization_rule = None`.

Work Unit 4 must replace this temporary pass-through semantics with explicit, reproducible normalization rules where needed.

## Observed source measurements

The pinned Artega snapshot contains:

- makes: 1
- models: 2 (`GT`, `Scalo`)
- generations: 2
- engine/powertrain records: 2

The current deterministic mapping yields:

- automotive entity candidates: 2
- raw evidence records: 2
- candidate facts: 26

Thus:

`REAL_AUTOMOTIVE_RECORDS = 2 (> 0)`

These counts are derived directly from the pinned structured source and the importer field mapping. Per project direction on 2026-08-19, this work unit does not introduce or run a new test suite.

## Provenance and raw preservation

Every candidate entity receives a source locator pointing to the exact upstream JSON position. Every candidate fact references a `RawEvidence` record, and every evidence record references the pinned source snapshot through `raw_content_ref`.

No canonical facts are generated yet. No conflict resolution is performed. No source is silently treated as authoritative.

## Source licensing / attribution

The upstream `LICENSE-DATA` states that files under `data/` are ODbL v1.0 and requires attribution to `vehicle-makes-models` and autoevolution.com. Attribution for the pinned snapshot is recorded in `data/raw/vehicle-makes-models/SOURCE.md`.

## Gate

- `REAL_AUTOMOTIVE_RECORDS > 0`: YES (`2` source powertrain records)
- `RAW_SOURCE_RECORD_PRESERVED`: YES
- `RAW_EVIDENCE_REPRESENTABLE`: YES
- `CANDIDATE_ENTITY_REPRESENTABLE`: YES
- `CANDIDATE_FACTS_REPRESENTABLE`: YES
- `MULTI_SOURCE`: NO (intentionally deferred)
- `NORMALIZATION`: NOT YET
- `ENTITY_RESOLUTION`: NOT YET
- `FUSION`: NOT YET
