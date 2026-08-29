# NHTSA vPIC Evidence Contract V1

Status: source-specific semantic/provenance contract for post-MVP enrichment; issue #125.

## Purpose

Define how Podium 7 may use NHTSA vPIC beyond bounded discovery without changing existing catalog identity, evidence, fusion, ambiguity or publication principles.

Primary documentation: https://vpic.nhtsa.dot.gov/api/

Existing discovery implementation remains governed by `OFFICIAL-SOURCE-DISCOVERY-V1.md`. This contract adds the boundary for VIN/manufacturer-backed evidence; it does not turn discovery candidates into identity proof.

## Source authority and scope

NHTSA documents vPIC as a vehicle/manufacturer information API populated from information submitted by motor-vehicle manufacturers through NHTSA reporting processes, including VIN-assignment information. The source is applicable to vehicles intended for sale or importation into the United States and may be incomplete outside that scope.

Source authority classification: `EVIDENCE_BACKED` for documented NHTSA/vPIC semantics.

Operational evidence classification: retain the existing `LOCALLY_VERIFIED` acquisition evidence recorded in `CANDIDATE-EVALUATION-LEDGER.md` and `COMPLIANT-ALTERNATIVE-SOURCES-V1.md`; this contract does not create a new live observation.

## Evidence roles

### Discovery role

`GetModelsForMakeYear` and related enumeration methods remain `DISCOVERY` only.

A returned NHTSA make/model ID and label may be preserved as source-native identifiers and candidate locators, but does not by itself prove Podium generation, trim, powertrain, transmission, body style or global market identity.

### VIN-backed evidence role

VIN decode methods may produce source-backed attributes for a concrete VIN/partial VIN/model-year request. A returned variable may become a `CandidateFact` only when:

1. the exact vPIC variable is present with a non-empty/non-null source value;
2. the source variable's documented semantics align with the Podium candidate field;
3. the mapping is explicitly registered by the source adapter/contract rather than inferred from a similar label;
4. the evidence record retains the exact request locator or canonical request representation plus raw response bytes/hash;
5. no existing Podium semantic invariant is widened to make the field fit.

A missing, blank or null vPIC variable is absence of evidence. It is never negative evidence that the vehicle lacks the attribute.

vPIC explicitly supports partial VIN decoding. For the bounded `DecodeVinValues` adapter, source error-code handling is conservative and explicit: code `0` (clean decode) and code `6` (incomplete VIN/partial decode) are the only admitted decode states. Any other code, alone or combined with `6`, fails closed before candidate facts are emitted. This prevents a response that explicitly warns of inaccurate model-year/data semantics (for example code `11`) or unavailable/invalid decode conditions from becoming evidence merely because some fields are populated. Expanding the admitted code set requires a separate source-backed contract change.

## Initial field contract

This V1 authorizes source-contract work for these candidate dimensions when vPIC explicitly returns a corresponding documented vehicle variable:

| Source evidence class | Podium role | Strength boundary |
|---|---|---|
| make/manufacturer + source IDs | discovery / supporting identity evidence | preserve IDs; not `STRONG` by default |
| model + model year | discovery / supporting identity evidence | model-year is source model year; not manufacturing year |
| body/vehicle class variables | candidate body-style/type evidence | source taxonomy must be preserved; map only explicit registered values |
| engine model/configuration variables | candidate engine identifier/spec evidence | supporting/case-bound; no universal engine-code identity claim |
| transmission variables | candidate transmission evidence | supporting/case-bound; no inference from drivetrain alone |
| fuel/electrification variables | candidate powertrain/spec evidence | normalize only registered source combinations |
| trim/series-like variables | source-native configuration evidence | never auto-equate to canonical retail trim solely by name |

The exact vPIC vehicle-variable names/IDs admitted to an adapter must be frozen in deterministic fixtures before implementation. This document does not approve every variable in the vPIC variable catalog.

## External identifier policy

NHTSA Make_ID, Model_ID, WMI and other vPIC-native identifiers remain namespaced source identifiers.

Default contract classification: `REFERENCE_ONLY` or `SUPPORTING` according to the specific namespace contract implemented later. None is promoted to `STRONG` by this document. A future `STRONG` designation requires a separate documented product decision and contradiction analysis under `CATALOG-IDENTITY-V2.md`.

## Normalization boundary

- Preserve raw source values before normalization.
- Normalize only explicit registered mappings with source-backed meaning.
- Do not decompose free-form source labels into trim/generation/mechanical identity unless a separate deterministic parser contract is supported by inspected source evidence.
- Do not convert NHTSA model year into manufacturing year.
- Do not infer market outside the documented U.S. sale/import scope.
- Do not treat absent fields as contradictions.

Unsupported or newly observed values fail closed to retained raw evidence plus an explicit issue/review path.

## Conflict and abstention behavior

- Agreement with another qualified source may strengthen provenance/corroboration but does not erase source-specific semantics.
- Disagreement with another source becomes an explicit `Conflict`; confidence or source convenience must not silently choose a winner.
- A vPIC result that lacks a decision-critical identity dimension must leave that dimension unresolved.
- Partial-label overlap remains governed by the existing catalog resolver and may remain `REVIEW`.
- Explicit structural contradictions continue to outrank weak lexical similarity under current resolver rules.

## Provenance contract

For every acquired vPIC evidence unit preserve, at minimum:

- source family = `nhtsa_vpic`;
- API method and exact request locator/canonical request representation;
- requested make/model year or VIN/partial VIN/model year as applicable;
- retrieval timestamp;
- HTTP status/media type and relevant acquisition metadata under the existing direct-HTTP contract;
- raw response reference and SHA-256;
- vPIC API/version evidence when exposed/documented;
- source row/variable IDs and source-native values used by extraction;
- extraction method/version and normalization rule ID;
- resulting candidate fact references.

The evidence store must preserve the source → raw evidence → candidate → normalization → resolution → canonical chain required by `CATALOG-EVIDENCE-POLICY-V2.md`.

## Access and operational constraints

- Respect NHTSA's documented automated traffic rate control.
- Repeated acquisition must pass `RECURRING-SOURCE-POLICY-V1.md` and existing network-target-binding requirements.
- Do not introduce proxy rotation, alternate identity, browser challenge bypass or retry storms.
- Broad redistribution rights were not established by the retained source evaluation; downstream packaging/public redistribution must remain conservative until resource/terms evidence supports it.

## Deterministic fixture requirements before adapter implementation

A VIN-evidence adapter must freeze independently inspected responses covering at least:

1. a clean or supported partial-VIN case with explicit model year plus configuration variables intended for mapping;
2. a case with one or more absent optional variables, proving no negative inference;
3. an unsupported/unregistered variable or decode-error state that fails closed;
4. a malformed response path;
5. duplicate/conflicting source representation handling where applicable.

Fixtures must pin exact bytes/hash and expected source-to-Podium mappings independently of extraction code.

## Nonclaims

This contract does not establish:

- global vehicle coverage;
- retail-trim identity from NHTSA labels alone;
- manufacturing year;
- universal engine/transmission/body taxonomy equivalence;
- automatic `MATCH` authority from any vPIC identifier;
- production-wide quality metrics;
- permission for broad redistribution of all vPIC content.

## Implementation disposition

`SOURCE = NHTSA vPIC`

`DECISION = ADAPT`

`AUTHORIZED_NEXT_STEP = bounded VIN-backed evidence adapter/fixtures under #126`

`IDENTITY_POLICY_CHANGE = NO`
