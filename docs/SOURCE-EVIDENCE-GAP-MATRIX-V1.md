# Source Evidence Gap Matrix V1

Status: post-MVP baseline reconstructed for issue #123.

## Purpose

This record maps current qualified automotive source families against Podium 7 catalog evidence needs. It is a decision aid for source discovery, not a claim of global coverage and not a change to evidence/fusion/resolution policy.

The matrix reconstructs durable repository evidence before any retest, as required by `DEVELOPMENT-WORKFLOW.md` and `CANDIDATE-EVALUATION-LEDGER.md`.

## Interpretation vocabulary

- `IDENTITY_SUPPORT` — source can support one or more identity dimensions inside its documented scope, but does not automatically prove canonical identity.
- `SPEC_EVIDENCE` — source can provide factual specification evidence that may enrich a candidate when semantics align.
- `DISCOVERY` — source can enumerate candidate makes/models/options/identifiers but discovery is not identity proof.
- `REFERENCE` — useful inspectable evidence with a current limitation that prevents stronger automated use.
- `GAP` — current retained evidence does not establish adequate defensible coverage for the stated need.

A source field being present does not imply semantic equivalence with another source or with a Podium canonical field.

## Current qualified-source baseline

| Source family | Region / market scope | Current disposition | Proven useful semantics | Current boundary |
|---|---|---|---|---|
| `vehicle-makes-models` pinned snapshot | mixed upstream catalog sample | selected historical structured source | make/model/generation/variant-like structured ingestion evidence for the first real ingestion path | community-maintained upstream dataset; retained primarily as pinned/reproducible ingestion evidence, not authoritative universal identity proof |
| NHTSA vPIC | vehicles intended for sale/import in the U.S. | `ADAPT` | make/model/year discovery, NHTSA IDs, VIN/manufacturer-oriented identity support where documented | U.S.-scope; model enumeration is not universal trim/spec proof; broad redistribution status not established by the retained evaluation |
| FuelEconomy.gov | U.S. | `REFERENCE` | deterministic year→make→model/options discovery; fuel type, drivetrain and gasoline MPG on characterized pages | characterized extraction is bounded; MPGe remained unsupported in the retained benchmark; discovery/menu identity is not canonical trim proof |
| EEA passenger-car CO2 monitoring | EU registration/type-approval monitoring | `ADAPT` | make/commercial name/manufacturer; type-approval/type/variant/version; mass; fuel; engine capacity/power; registration year; electric/CO2 fields | regulatory registration/type-approval rows must not be reinterpreted as globally unique retail configurations |
| Inmetro PBE Veicular | Brazil | `REFERENCE` | official model/version, fuel, consumption, emissions and efficiency evidence; current document path exists | machine-readable CSV/API path was not established in the retained evaluation; source-specific PDF/document semantics apply and resource-specific reuse metadata remains authoritative |

## Catalog-dimension gap matrix

| Podium dimension / evidence need | Existing qualified support | Current assessment | Decision-critical gap |
|---|---|---|---|
| Make / manufacturer | NHTSA, EEA, Inmetro, FuelEconomy discovery, retained structured snapshot | comparatively strong across retained families | no generic new-source search justified solely for make/manufacturer |
| Model / commercial name | NHTSA, EEA, Inmetro, FuelEconomy, retained snapshot | broad candidate/discovery support, but source naming semantics differ | corroboration and alias evidence remain needed when labels differ across market/source families |
| Generation | retained structured evidence and manufacturer/source-backed benchmark cases | sparse in current official machine-readable source families | `GAP`: qualify primary manufacturer or regulatory evidence where generation distinction is required for unresolved cases |
| Variant / trim | EEA regulatory variant/version identifiers; Inmetro model/version; selected manufacturer evidence in benchmarks/enrichment | useful but semantically heterogeneous and often incomplete | `GAP`: trim-defining evidence is a measured cause of `REVIEW`; seek source-specific primary evidence rather than treating regulatory variant codes as retail trims |
| Powertrain | EEA fuel/engine/electric fields; Inmetro fuel/efficiency; FuelEconomy fuel/drivetrain; manufacturer evidence in benchmark/enrichment | moderate factual support | `GAP`: exact configuration/powertrain identity may still need manufacturer-specific mechanical evidence for ambiguous models/variants |
| Transmission | FuelEconomy/drivetrain pages may contribute related facts; manufacturer evidence used in catalog benchmark | not broadly established as structured cross-market evidence | `GAP`: qualify primary source paths for transmission where it is identity-defining |
| Body style | present in selected identity benchmark/manufacturer evidence; not established as consistently covered by retained official machine-readable families | sparse | `GAP`: source discovery should target primary body-style evidence only for measured unresolved cases |
| Market | source-family scope itself supplies regional context; catalog benchmark contains market distinctions | source scope is useful but not equivalent to explicit vehicle-market identity | `GAP`: preserve explicit market evidence when cross-market naming/configuration collision is possible |
| Manufacturing year | Senatran-aligned product semantics require this to remain distinct from model year | no retained general-purpose qualified source establishes broad manufacturing-year coverage | `GAP`: high-priority Brazil-specific primary evidence path where manufacturing year is decision-critical; do not infer from registration/model year |
| Model year | NHTSA make/model/year discovery; FuelEconomy year menus; manufacturer evidence; FIPE semantics in year challenge | meaningful support but asymmetric/missing evidence still routes to `REVIEW` | measured `GAP`: missing explicit model-year evidence is part of `MISSING_IDENTITY_EVIDENCE`; enrich case-bound evidence rather than auto-fill |
| Engine identifiers | vPIC/VIN-oriented attributes may support some U.S. cases; manufacturer evidence can support case-bound identifiers | no broad retained cross-market engine-ID source contract | `GAP`: qualify source-specific primary identifiers where engine code materially disambiguates variants |
| External identifiers | NHTSA IDs are preservable provenance/discovery identifiers; FIPE is `SUPPORTING`; EEA type-approval/type/variant/version are regulatory identifiers | namespaces exist but strengths are source/namespace-specific | `GAP`: every new namespace requires explicit semantic/strength treatment; do not promote reference IDs to `STRONG` by convenience |
| Fuel / energy type | EEA, Inmetro, FuelEconomy | comparatively strong factual enrichment | semantic normalization must stay source-backed; no new-source search justified absent a measured unresolved need |
| Engine capacity / power | EEA; Inmetro/manufacturer evidence depending on case | useful specification support | coverage is market/source limited; seek additional primary evidence only for measured unresolved configurations |
| Mass | EEA | official EU monitoring evidence | cross-market coverage remains limited but not presently an identity-priority gap by itself |
| Consumption / efficiency / emissions | Inmetro, FuelEconomy, EEA | strong region-specific factual coverage | retain region/source semantics; these facts are generally enrichment rather than canonical identity proof |
| Electric range / energy consumption | EEA and Inmetro where published; FuelEconomy has bounded EV-related limitations in prior extractor characterization | partial official support | qualify additional source only if a concrete EV coverage measurement shows a decision-critical gap |
| Provenance / locator / raw hash | Podium acquisition/evidence contracts across retained characterized sources | strong architectural support | no semantic gap; every future adapter must preserve the same chain |
| Reuse / attribution / access constraints | individually recorded for EEA, Inmetro pages, NHTSA access/rate controls; bounded statements for FuelEconomy | source-specific, deliberately conservative | `GAP`: exact resource-level terms must be resolved before any broader redistribution/production use where not already established |

## Measured operational gaps

The retained 60-record source-backed replay produced 19 `CREATED`, 19 `MATCHED`, 22 `REVIEW`, and zero failures. The 22 review tasks were classified as:

1. `MISSING_IDENTITY_EVIDENCE`: 13/22 — missing model-year, trim-defining, or other deterministic identity evidence.
2. `LABEL_AMBIGUITY`: 9/22 — insufficient evidence to resolve partial/ambiguous labels automatically.

These are the decision-driving gaps for issue #124. They do not justify weakening the resolver.

## Source-discovery questions for #124

Source qualification should answer the smallest set of questions below, in priority order:

1. **Brazil year semantics:** which current primary Senatran/SERPRO or equivalent official access path can provide defensible manufacturing-year and model-year evidence at the granularity Podium needs, with documented access/reuse constraints?
2. **Trim / configuration identity:** for measured ambiguous model/variant cases, which primary manufacturer, homologation, regulatory, or documented commercial sources expose trim-defining mechanical/configuration evidence without conflating regulatory variant codes with retail trims?
3. **Transmission / body style / engine identifiers:** which primary documented sources provide these identity-defining dimensions for unresolved cases and markets already represented in the corpus?
4. **Cross-source alias corroboration:** which primary manufacturer/regulatory identifiers or explicit alias surfaces can corroborate differing commercial/model labels without using lexical similarity as proof?
5. **Resource-level reuse:** for otherwise useful sources whose redistribution/attribution status is not yet established, what exact dataset/resource terms govern retention and downstream use?

## Explicit non-gaps / no-repeat decisions

- Do not search for another generic make/model API merely because one exists; current qualified sources already provide substantial discovery coverage.
- Do not rerun the NHTSA, EEA, Inmetro or FuelEconomy historical live batteries absent a version/environment change or a decision-critical missing slice.
- Do not reintroduce Autoevolution bypass work; retained direct HTTP and normal Chromium failures plus official alternatives already support that disposition.
- Do not treat source diversity (three regions/families) as production completeness.
- Do not alter existing year, ambiguity, conflict or evidence policy to reduce `REVIEW` volume.

## #123 disposition

`BASELINE_RECONSTRUCTION = PASS`

`BROAD_RETEST_REQUIRED = NO`

`PRIMARY_OPERATIONAL_GAPS = MISSING_IDENTITY_EVIDENCE + LABEL_AMBIGUITY`

`NEXT_BLOCK = #124 targeted source qualification`
