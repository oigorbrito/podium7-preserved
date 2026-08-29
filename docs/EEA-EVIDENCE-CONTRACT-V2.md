# EEA Evidence Contract V2

Status: source-specific semantic/provenance refinement for post-MVP enrichment; issue #125.

## Purpose

Refine the already implemented EEA passenger-car source-family boundary so that post-MVP enrichment can use regulatory identity/support fields without inventing retail-trim, manufacturing-year or global-identity semantics.

Primary dataset: https://www.eea.europa.eu/en/datahub/datahubitem-view/fa8b1229-3db6-495d-b18e-9c9b3267c02b

Existing acquisition and factual mappings remain governed by `EEA-SOURCE-FAMILY-V1.md` and `EEA-SEMANTIC-EXPANSION-V2.md`. This contract does not replace those historical implementation records; it defines the evidence role of additional retained fields for later enrichment/fusion.

## Source authority and scope

The EEA passenger-car CO2 monitoring dataset is an official EU regulatory registration/type-approval monitoring source under Regulation (EU) 2019/631. The current 2025 provisional dataset documents fields including manufacturer, type-approval number, type, variant, version, make, commercial name, fuel, engine capacity, engine power, mass, electric-energy fields and registration year.

Source authority classification: `EVIDENCE_BACKED` for documented EEA dataset semantics.

Operational evidence classification: existing bounded acquisition remains `LOCALLY_VERIFIED` through the frozen V1 snapshot and benchmark. This contract creates no new live observation.

## Regulatory identity/support fields

The following source fields may be retained as source-native regulatory evidence:

| EEA field/evidence | Podium role | Contract boundary |
|---|---|---|
| manufacturer | supporting manufacturer evidence | preserve source spelling/identifier context |
| make | supporting make evidence | not global alias proof by itself |
| commercial name | source-native commercial/model label evidence | not automatically canonical model/trim |
| type-approval number | namespaced regulatory identifier | supporting/reference unless separately promoted by explicit namespace decision |
| type | namespaced regulatory configuration evidence | not canonical generation |
| variant | namespaced regulatory configuration evidence | not retail trim |
| version | namespaced regulatory configuration evidence | not retail trim |
| registration year | registration-year evidence | never manufacturing year; not automatically Podium model year |
| engine power | specification evidence | existing mapped semantics remain governed by source-family implementation |
| engine capacity | specification evidence | existing mapped semantics remain governed by source-family implementation |
| fuel/fuel mode | powertrain/spec evidence | only registered source combinations may normalize |
| mass in running order | retained regulatory spec evidence | not curb weight |
| electric energy/range/emissions fields | retained regulatory spec evidence | normalize only through explicit future contracts |

## External identifier policy

EEA type-approval/type/variant/version values must retain explicit namespaces and source provenance.

Default contract classification is `REFERENCE_ONLY` or `SUPPORTING` according to the concrete namespace registry introduced during implementation. This document does not promote any EEA regulatory identifier to `STRONG`.

A shared regulatory identifier may corroborate two evidence records, but automatic identity effects remain governed by `CATALOG-IDENTITY-V2.md` and require the namespace's explicit registered strength.

## Model, trim and generation non-equivalence

- `commercial name` may support a model/commercial label only inside the source's regulatory context.
- `type`, `variant` and `version` must not be renamed or collapsed into Podium `generation` or `variant` merely because those concepts appear superficially similar.
- A source tuple may be preserved as regulatory configuration evidence and compared to another source tuple without asserting retail-trim equality.
- Generation or retail-trim identity still requires separate primary evidence when it is decision-critical.

## Year semantics

EEA `registration year` means the year associated with monitored registration data.

It must not populate:

- `manufacturing_year_from/to`;
- `model_year_from/to` merely by convenience;
- any generic year field whose semantics would erase the distinction required by `CATALOG-IDENTITY-V2.md`.

A separate source-backed mapping would be required before registration year could participate in another year dimension.

## Normalization boundary

- Existing engine-power, displacement and registered fuel mappings remain unchanged.
- Raw regulatory fields must remain available even when not promoted to normalized candidate facts.
- Unknown fuel/type/mode or newly observed enumerations fail closed according to existing source-family behavior.
- Equal units do not establish semantic equivalence.
- No free-form decomposition of commercial name into generation/trim/configuration is authorized by this contract.

## Conflict and corroboration behavior

- Agreement between EEA and another qualified source can create corroborating provenance for the aligned fact only.
- Disagreement remains an explicit conflict; no confidence-only winner selection is introduced.
- Regulatory identifier agreement may support case review, but does not silently convert to a canonical merge unless current resolver rules and registered identifier strength allow it.
- If an EEA row lacks a decision-critical dimension, that dimension remains unresolved rather than inferred from neighboring rows or labels.

## Provenance contract

For every acquired EEA evidence unit preserve, at minimum:

- source family = `eea_co2_passenger_cars`;
- dataset release/table identifier;
- exact Discodata/source locator or canonical query representation;
- source record identifier(s) sufficient to reproduce the bounded row selection;
- retrieval timestamp;
- HTTP/media/acquisition metadata under existing acquisition contracts;
- raw response reference, byte size and SHA-256;
- retained source-native fields used for extraction/alignment;
- extraction method/version and normalization-rule IDs;
- resulting candidate fact/evidence references;
- attribution/reuse metadata applicable to the concrete dataset/resource.

The evidence chain must remain source → raw evidence → candidate → normalization → resolution → canonical.

## Reuse and access constraints

The retained evaluation records the EEA public-sector reuse framework (generally CC-BY for EEA-owned materials and open-data licensing such as ODC-By or similar unless otherwise indicated), while preserving dataset-specific and third-party notices as authoritative.

Any packaged/exported EEA-derived data must retain the required attribution/resource metadata. Do not generalize one page-level notice to every underlying resource when dataset-specific terms differ.

Recurring acquisition must comply with the repository's recurring-source, direct-HTTP and network-target-binding policies.

## Deterministic fixture requirements before new enrichment code

Any new use of regulatory identity/support fields must add independently inspected frozen fixtures covering:

1. a row with type-approval/type/variant/version and commercial name;
2. a row where one or more regulatory fields are null/absent, proving no inference;
3. two rows demonstrating why equal/similar commercial labels do not by themselves establish canonical trim identity;
4. a conflict/corroboration case with another qualified source where source semantics remain distinct;
5. schema/field drift failure behavior for any newly required source field.

Expected mappings/nonclaims must be defined independently of extractor code.

## Nonclaims

This contract does not establish:

- one EEA row = one Podium catalog configuration;
- retail trim or generation identity from type/variant/version;
- manufacturing year or model year from registration year;
- global market identity;
- `mass in running order == curb_weight`;
- `STRONG` identity authority for EEA regulatory identifiers;
- production-wide precision/recall or completeness.

## Implementation disposition

`SOURCE = EEA passenger-car monitoring`

`DECISION = ADAPT`

`AUTHORIZED_NEXT_STEP = bounded regulatory-identity/support enrichment using frozen fixtures under #126`

`IDENTITY_POLICY_CHANGE = NO`
