# BR PBEV Technical Sheet Contract V1

Status: current source-native launch contract.

Schema identifier:

`podium7.br-pbev-technical-sheet.v1`

## Purpose

Expose a small Brazil-specific technical-sheet surface backed by the retained
Inmetro PBEV benchmark without changing the generic
`podium7.quantitative-enrichment.v1` contract.

This contract exists because the retained PBEV evidence contains official
source-native quantities that are not semantically equivalent to
`fuel_economy_combined`.

## Authority

- Source benchmark: `benchmarks/inmetro_pbev_quantitative_semantics_v1.json`.
- Implementation: `podium7/br_pbev_technical_sheet.py`.
- Tests: `tests/test_br_pbev_technical_sheet.py`.

## Fields

| Field | Source column | Unit | Semantics |
| --- | ---: | --- | --- |
| `ethanol_city_consumption` | 17 | `km/l` | Ethanol city consumption/efficiency as published by PBEV. |
| `ethanol_road_consumption` | 18 | `km/l` | Ethanol road consumption/efficiency as published by PBEV. |
| `gasoline_city_consumption` | 19 | `km/l` | Gasoline city consumption/efficiency as published by PBEV. |
| `gasoline_road_consumption` | 20 | `km/l` | Gasoline road consumption/efficiency as published by PBEV. |
| `electric_equivalent_city_efficiency` | 21 | `km/le` | Electric equivalent city efficiency as published by PBEV. |
| `electric_equivalent_road_efficiency` | 22 | `km/le` | Electric equivalent road efficiency as published by PBEV. |
| `energy_consumption` | 23 | `MJ/km` | Energy consumption as published by PBEV. |
| `electric_range` | 24 | `km` | Electric range as published by PBEV. |
| `pbe_relative_class` | 25 | none | PBE relative class as source text. |
| `pbe_general_class` | 26 | none | PBE general class as source text. |
| `conpet_symbol` | 27 | none | CONPET symbol text as published by PBEV. |

## Fact Semantics

Every published sheet contains every field exactly once.

Known facts include:

- `field`;
- `knowledgeState: known`;
- `provenanceRef`;
- `rawValue`;
- `value`;
- `unit` when the source field is numeric.

Source placeholder cells are represented as:

- `knowledgeState: not_applicable`;
- the retained raw placeholder;
- a deterministic reason.

The producer must not infer a combined fuel economy value from city/road or
fuel-specific fields.

## Identity Boundary

PBEV quantitative facts attach only after identity resolution. They do not
participate in identity matching and cannot create or merge canonical vehicle
identity.

## BPT2 Launch Boundary

This contract can support a narrow Brazil PBEV technical-sheet surface where the
consumer already has a safe identity join and can present source-native labels.

It does not authorize:

- Comparator;
- ranking;
- recommendations;
- quantitative search filters;
- broad generic ficha tecnica;
- reinterpretation as `podium7.quantitative-enrichment.v1`.
