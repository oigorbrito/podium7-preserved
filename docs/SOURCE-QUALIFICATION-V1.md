# Targeted Automotive Source Qualification V1

Status: issue #124 research qualification complete; no new adapter selected for implementation without an explicit source contract.

## Decision question

Given the measured post-MVP gaps (`MISSING_IDENTITY_EVIDENCE` and `LABEL_AMBIGUITY`), which current primary/official source paths can defensibly add manufacturing/model-year, trim/configuration, transmission/body-style/engine-identifier, and cross-source label evidence without changing Podium's existing evidence, fusion, ambiguity, or resolution principles?

This record intentionally does not repeat broad historical live-source batteries. Existing NHTSA, EEA, Inmetro and FuelEconomy operational evidence is reused from `CANDIDATE-EVALUATION-LEDGER.md`. New work in this block is bounded to primary-documentation qualification for the decision-critical gaps identified by `SOURCE-EVIDENCE-GAP-MATRIX-V1.md`.

## Qualification rules

A source path is classified only within its documented semantics and access boundary:

- `ADAPT`: suitable for a deterministic Podium source path inside a bounded documented scope;
- `REFERENCE`: authoritative/useful evidence, but not currently a general automated acquisition path for the needed granularity;
- `UNDECIDED`: semantics are useful but a decision-critical access, contract, reuse, or implementation condition is unresolved;
- `REJECT`: not suitable for the stated evidence need.

No source is promoted to canonical identity proof merely because it exposes a field with a familiar name. Missing fields remain missing evidence. Regulatory type/variant/version identifiers are not silently converted into retail trims. Existing namespace-strength and fail-closed rules remain unchanged.

## Candidate 1 — SENATRAN WSDenatran / RENAVAM

Primary documentation:

- https://www.gov.br/conecta/catalogo/apis/wsdenatran
- https://www.gov.br/conecta/catalogo/apis/wsdenatran/at_download/api_tecnico_documentacao

### Established semantics

The official Conecta catalog describes WSDenatran as an integration service exposing official vehicle information from RENAVAM, among other national traffic systems. The published technical response model contains vehicle fields including `codigoMarcaModelo`, `descricaoMarcaModelo`, `codigoTipoCarroceria`, `descricaoTipoCarroceria`, `anoModelo`, `anoFabricacao`, `potencia`, `cilindradas`, fuel fields, `numeroMotor`, and `numeroCambio`.

This is directly relevant to the Brazil-specific gaps because the API preserves manufacturing year and model year as separate fields and also exposes several configuration/identifier dimensions that Podium currently treats as sparse.

### Access boundary

The official catalog states that use is provided through SENATRAN authorization and contracting of the online consultation service with SERPRO. This is therefore not an anonymous public-data endpoint that Podium can assume is available for recurring operation.

### Disposition

`UNDECIDED` for automated Podium acquisition.

Reason: the semantics are a strong fit for Brazil-specific identity enrichment, but contractual authorization/access is a decision-critical prerequisite outside repository-only implementation. Do not build a substitute or scrape around this access boundary.

Potential future role if access is legitimately obtained: source-specific `SUPPORTING` evidence for documented vehicle attributes, with identifier strengths decided separately by namespace contract rather than assumed here.

## Candidate 2 — SENATRAN public fleet datasets

Primary documentation:

- https://www.gov.br/transportes/pt-br/assuntos/transito/conteudo-Senatran/frota-de-veiculos-2026

### Established semantics

The current official 2026 fleet publication includes monthly datasets grouped by municipality and `Ano de Fabricação Modelo`, as well as separate groupings for brand/model, fuel, power and vehicle type/species.

### Boundary

These publications are aggregated fleet statistics. They demonstrate and preserve official field semantics and can support population-level/reference checks, but they do not provide the row-level vehicle/configuration identity needed to resolve one Podium candidate against another.

### Disposition

`REFERENCE`.

Use to corroborate official Brazilian terminology and aggregate plausibility where methodologically appropriate. Do not use an aggregate row as proof of an individual catalog identity, trim, engine, transmission, or specific manufacturing/model-year pairing.

## Candidate 3 — SENATRAN CAT / SISCAT homologation semantics

Primary documentation:

- https://www.gov.br/pt-br/servicos/sistema-de-certificacao-de-adequacao-a-legislacao-de-transito
- https://www.gov.br/transportes/pt-br/assuntos/transito/conteudo-Senatran/carta-de-servicos-rev11-06-25.pdf

### Established semantics

SENATRAN documents the Certificado de Adequação à Legislação de Trânsito (CAT) as the homologation instrument that grants a specific RENAVAM `marca/modelo/versão` code for vehicles subject to the process. This is valuable evidence that Brazilian regulatory identity has an explicit brand/model/version concept rather than only a free-form retail label.

### Boundary

The current official service material establishes the homologation semantics and applicant workflow, but this qualification did not establish a public, anonymous, machine-readable catalog/API from which Podium can enumerate CAT records or their full configuration details.

### Disposition

`REFERENCE`.

Use as primary semantic authority for the meaning/existence of RENAVAM brand/model/version homologation. Do not claim a production acquisition path until a documented query surface with appropriate access and reuse terms is established.

## Candidate 4 — NHTSA vPIC VIN/manufacturer data

Primary documentation:

- https://vpic.nhtsa.dot.gov/api/

### Established semantics

NHTSA states that vPIC is populated from information submitted by motor-vehicle manufacturers through 49 CFR Part 565-related submissions and uses those data to decode VINs and extract vehicle information. The API exposes VIN decoding, make/model/year methods, manufacturer identifiers and a vehicle-variable catalog. It also documents partial VIN decoding and recommends supplying model year when decoding.

The retained Podium live characterization already established normal-access JSON acquisition for make/model/year discovery. The current documentation additionally supports using VIN-backed vPIC outputs as case-bound manufacturer-submitted vehicle attribute evidence when the returned variables are present.

### Boundary

vPIC is scoped to vehicles intended for sale/import in the United States and is not a universal trim/specification catalog. A field omitted from a decode is absence of evidence, not proof that the vehicle lacks the attribute. Model/year enumeration alone is discovery support, not trim identity proof. Broad redistribution rights remain outside the established retained evidence.

### Disposition

`ADAPT` (existing decision strengthened, not replaced).

Use for U.S.-scope discovery and VIN/manufacturer-backed identity/specification support under a source-specific contract. Do not promote all vPIC values or identifiers to `STRONG` identity evidence by default.

## Candidate 5 — EEA passenger-car CO2/type-approval monitoring

Primary documentation:

- https://www.eea.europa.eu/en/datahub/datahubitem-view/fa8b1229-3db6-495d-b18e-9c9b3267c02b

### Established semantics

The official 2025 provisional EEA monitoring dataset records new passenger-car registrations under Regulation (EU) 2019/631. Published fields include manufacturer, type-approval number, type, variant, version, make, commercial name, fuel, engine capacity/power, mass, registration year and electric/emissions fields.

The retained Podium characterization already verified the current SQL REST path and structured records. These fields remain useful regulatory configuration evidence and provide explicit identifiers for cross-source corroboration inside their EU type-approval semantics.

### Boundary

A type/variant/version tuple is regulatory/type-approval evidence, not automatically a retail trim, generation, or globally unique Podium catalog configuration. Registration year is not manufacturing year and must not be substituted for it.

### Disposition

`ADAPT` (existing decision retained).

Use as structured EU regulatory/specification evidence. Preserve the source identifiers and semantics; do not silently map them to retail trim identity.

## Candidate 6 — primary manufacturer specification/homologation artifacts

### Qualification result

Primary manufacturer artifacts (official specification pages, technical sheets, homologation/ordering guides or other manufacturer-published documents) remain a valid evidence class for case-bound enrichment when they are the direct publisher for the vehicle/configuration and the exact resource can be retained with provenance.

However, this block does not designate a single generic manufacturer source family or generic scraper: publication shape, terms, field semantics and availability vary by manufacturer, market and model year. A manufacturer artifact must therefore be qualified and contracted source-by-source when a measured unresolved case requires it.

### Disposition

`REFERENCE` as an evidence class; individual resources may later become `ADAPT` only after source-specific qualification.

This is the preferred path for generation names, retail trims and mechanical/configuration distinctions that regulatory datasets do not explicitly prove. Search/discovery results alone are never canonical evidence; the retained primary resource is.

## Gap disposition matrix

| Measured/decision-critical gap | Qualified path | Result |
|---|---|---|
| Brazil manufacturing year vs model year | WSDenatran exposes both fields | semantics fit; automated use `UNDECIDED` pending legitimate SENATRAN/SERPRO access |
| Brazil brand/model/version regulatory identity | CAT/SISCAT semantics + WSDenatran brand/model fields | authoritative semantic `REFERENCE`; automated row-level acquisition not yet established publicly |
| U.S. model year and VIN-backed configuration | NHTSA vPIC | `ADAPT` within documented U.S./VIN scope |
| EU regulatory variant/version/configuration | EEA type-approval monitoring | `ADAPT` as regulatory evidence; not retail-trim equivalence |
| Transmission/body style/engine identifiers in Brazil | WSDenatran publishes body, motor and gearbox fields | semantics fit; automated use `UNDECIDED` pending authorized access |
| Transmission/body/engine/configuration in U.S. | vPIC VIN-backed variable outputs when present | `ADAPT`; case-bound and fail-closed on missing fields |
| Generation / retail trim ambiguity | primary manufacturer artifacts | `REFERENCE` evidence class; source-specific qualification required per unresolved case/source family |
| Cross-source alias corroboration | official identifiers/names from NHTSA, EEA, SENATRAN/CAT plus manufacturer artifacts | supporting evidence only; no lexical alias auto-proof introduced |
| Resource-level reuse | EEA has explicit public-sector reuse framework in retained evidence; NHTSA broad redistribution not established; WSDenatran contractual; manufacturer terms resource-specific | remains source-specific; no universal redistribution assumption |

## Decision

The measured gaps do have defensible primary-source paths, but not all paths are immediately automatable:

1. Reuse NHTSA vPIC and EEA as already-qualified `ADAPT` sources inside their exact semantics.
2. Treat WSDenatran as the strongest identified Brazil row-level evidence candidate but keep it `UNDECIDED` until legitimate SENATRAN/SERPRO access and applicable use terms are available.
3. Keep SENATRAN fleet data and CAT/SISCAT as authoritative `REFERENCE` surfaces, not substitutes for row-level identity evidence.
4. Use manufacturer-published artifacts case-by-case for generation/retail-trim/mechanical distinctions that the structured regulatory sources do not prove.
5. Do not search for or introduce a generic opaque vehicle-spec API merely to fill fields.

## Retest decision

`BROAD_HISTORICAL_RETEST = NO`

`NEW_LIVE_PROBE_REQUIRED_FOR_THIS_QUALIFICATION = NO`

Reason: NHTSA and EEA operational access already have recoverable current Podium evidence; the new SENATRAN decision is blocked by documented authorization/contract requirements rather than an unknown anonymous endpoint behavior; public SENATRAN/CAT records are semantic/reference evidence rather than selected automated adapters.

Any future live test of WSDenatran requires legitimate authorized credentials/access and therefore is an owner/external access boundary, not a repository test to bypass.

## #124 disposition

`TARGETED_SOURCE_QUALIFICATION = PASS`

`IMMEDIATE_NEW_ADAPTER_CANDIDATES = existing NHTSA + EEA only`

`BRAZIL_ROW_LEVEL_CANDIDATE = WSDenatran / UNDECIDED_ACCESS`

`GENERATION_TRIM_PATH = case-bound primary manufacturer evidence`

`NEXT_BLOCK = #125 source-specific semantic/provenance contracts for selected implementable sources`
