# Donor Capability Evaluation V1

Status: issue #162 evaluation complete; rebuilt on current main after historical PR #163 closed without merge. The sole immediate implementation follow-up (#164/#165 source terms drift gate) is already integrated. Other donor adaptations remain gated by measured need.

## Purpose

Evaluate mature external automotive/open-source projects as capability donors before Podium 7 adopts or rebuilds equivalent functionality, consistent with ADR-0001. This record evaluates implementation patterns and semantic models, not just field count. It does not authorize importing donor data, code, schemas, or policy.

## Evaluation rule

A donor capability is useful only when all of the following hold:

1. the capability is documented in a primary upstream source;
2. its license/reuse boundary is understood sufficiently for the proposed use;
3. Podium does not already provide an equivalent capability at adequate quality; and
4. a measured Podium gap or operational risk justifies adoption/adaptation.

Disposition vocabulary: `ADOPT`, `ADAPT`, `REFERENCE`, `REJECT`, `UNDECIDED`.

## Donor matrix

| Donor | Capability | Upstream evidence | Podium overlap | Measured/observable Podium gap | License/reuse | Disposition |
|---|---|---|---|---|---|---|
| VehiclesDB | Multi-register reconciliation with corroboration before publication | VehiclesDB documents reconciliation of official registers and a publication rule requiring two independent sources or a high-count single source | Podium already preserves multiple evidence sources, conservative identity resolution, explicit conflicts and fail-closed `REVIEW` | No evidence that Podium needs VehiclesDB's fixed corroboration threshold; changing Podium publication/evidence thresholds is explicitly out of scope without owner authorization | Dataset CC BY 4.0 with attribution plus upstream notices; code/data reuse must be evaluated separately | `REFERENCE` |
| VehiclesDB | Stable model IDs and rename aliases | README/DECISIONS document stable IDs and rename-to-alias behavior | Podium already uses opaque stable canonical IDs, redirects after merge and model aliases | No current gap | Same as above | `REFERENCE` |
| VehiclesDB | Per-record source provenance and availability evidence | README/SCHEMA contract documents record-level sources and availability evidence | Podium already retains source -> raw evidence -> candidate -> canonical provenance and explicit evidence locators/hashes | No current provenance-model gap | Same as above | `REFERENCE` |
| VehiclesDB | Type-approval / homologation crosswalks where measured | README exposes `xrefs` / type-approval crosswalks; source notes distinguish approval/registration semantics | Podium preserves EEA type-approval/type/variant/version as namespaced regulatory evidence but does not yet demonstrate a general cross-source crosswalk product | Gap exists only where measured alias/identifier reconciliation requires explicit crosswalks; #123 identified cross-source alias corroboration as a source-discovery question | Donor data is CC BY 4.0; direct reuse would introduce attribution/upstream-license obligations | `ADAPT` as design pattern; data ingestion `UNDECIDED` |
| VehiclesDB | Auditable human overrides | AGENTS/README require curated changes through `overrides/`, each carrying a reason/source; generated outputs are not hand-edited | Podium has explicit `ENGINEERING_CHOICE` administrative override semantics and durable review, but no equivalent donor-style curated override input layer has been demonstrated as a general catalog operation | Potential operational gap for repeatable human curation after review; implementation must be justified by measured review/operator workflow, not convenience | Pattern can be reimplemented; copying donor files/data requires license review | `ADAPT` pattern, implementation deferred pending measured need |
| VehiclesDB | Spotcheck/tripwire assertions | README/AGENTS describe `spotchecks.yml` as assertions that important models must not disappear | Podium has regression datasets, identity benchmarks and quality gates | Existing Podium benchmarks already cover invariant/regression protection; donor spotchecks are a narrower operational form | Pattern only | `REFERENCE` |
| VehiclesDB | License-text pinning and drift gate | SOURCES/DECISIONS state upstream license text is pinned by SHA-256 and builds fail/open an issue on drift | Podium records access/reuse constraints and fails closed on source/schema/network drift, but recurring-source policy originally lacked a machine-enforced license-text drift gate | Genuine operational/compliance gap for recurring third-party source use; addressed by #164/#165 | Pattern can be independently implemented without consuming donor dataset | `ADAPT` — implemented in Podium-native form by #165 |
| VehiclesDB | Source-specific measured gotchas / forbidden-field use | SOURCES records measured semantic traps, including fields intentionally not read when aggregation altitude would make them wrong | Podium source contracts already require source-specific semantics, nonclaims, abstention and no semantic widening | No architectural gap; VehiclesDB provides useful corroborating precedent | Documentation pattern only | `REFERENCE` |
| High Mobility Auto API | Generated modular capability/property taxonomy for vehicle-generated data | Auto API defines YAML capabilities/properties, generation, modularity and backwards-compatible additive evolution | Podium catalog identity/spec evidence is not a connected-vehicle command/telemetry protocol | No current product gap in identity reconciliation; may become relevant if Podium later adds telemetry/capability interoperability | Repository MIT | `REFERENCE` only; do not import into current identity model |
| OpenCars VIN Decoder | VIN decomposition into WMI/VDS/VIS plus check-digit/year decoding | OpenCars exposes a small MIT VIN decoder with WMI/VDS/VIS output and check-digit result | Podium already uses/has qualified NHTSA vPIC for VIN-backed U.S. evidence and preserves stronger official-source semantics | No measured gap that this donor closes beyond existing vPIC path; generic VIN parsing alone does not establish model/trim semantics | MIT code; manufacturer data/source semantics would still require separate evidence qualification | `REFERENCE`; no implementation issue |

## VehiclesDB findings

### Capabilities that should not be copied as policy

VehiclesDB's fixed publication corroboration rule is evidence of a mature conservative design, but it is not automatically Podium policy. Podium's existing evidence/publication rules are frozen project principles and may only change with explicit owner authorization. The donor therefore supports the direction of conservative corroboration without authorizing a threshold change.

VehiclesDB's stable slug IDs also should not replace Podium opaque canonical IDs. Podium already protects ID stability through opaque IDs and redirects, which avoids coupling canonical identity to mutable naming.

### Capability adapted from the measured gap

The strongest genuine donor gap was **license/reuse drift enforcement**. Podium already recorded source access/reuse constraints, recurring host policy, provenance and schema/network drift, but lacked a deterministic gate pinning the exact governing license/reuse artifact and failing closed when it changed.

That gap was subsequently addressed by #164 / merged PR #165 with a Podium-native source-terms drift gate. The donor evaluation therefore remains evidence for why that capability exists; it does not grant legal permission or import donor policy.

### Capabilities worth measuring before implementation

VehiclesDB's explicit curated `overrides/` layer is a useful pattern for turning human review into reproducible, reviewable inputs. Podium already supports review and explicit administrative `ENGINEERING_CHOICE`; however, introducing a general override layer should wait for a measured operational need showing that current review-resolution persistence is insufficient. It must not become a shortcut around evidence-backed correction rules.

Type-approval crosswalks are similarly promising as a targeted interoperability capability, especially for aliases and cross-market/regulatory identifiers. They should be implemented only from qualified source evidence and only where a measured unresolved case requires them.

## High Mobility Auto API finding

Auto API is a mature schema-generation reference, but its problem is different: consistent connected-vehicle state/getter/setter data rather than catalog identity reconciliation. Its modular capability/property definitions and additive-generation discipline are worth retaining as a future reference if Podium expands into telemetry or standardized specification capabilities. No current donor adoption is justified.

## OpenCars VIN Decoder finding

OpenCars provides a compact implementation reference for VIN structure and decoding, but it does not improve Podium's current evidence position over the already-qualified NHTSA/vPIC path. VIN structure parsing is not a substitute for manufacturer/source-backed configuration semantics. No implementation follow-up is justified by current measured gaps.

## Decision

`VEHICLESDB_LICENSE_DRIFT_GATE = ADAPT_IMPLEMENTED_BY_165`

`VEHICLESDB_OVERRIDE_LAYER = ADAPT_PATTERN_ONLY_PENDING_MEASURED_NEED`

`VEHICLESDB_TYPE_APPROVAL_CROSSWALK = ADAPT_PATTERN_ONLY_PENDING_MEASURED_CASE`

`VEHICLESDB_CORROBORATION_THRESHOLD = REFERENCE_NO_POLICY_CHANGE`

`HIGH_MOBILITY_AUTO_API = REFERENCE`

`OPENCARS_VIN_DECODER = REFERENCE`

## Utility disposition

`DONOR_EVALUATION_UTILITY = INTEGRATE`

The evaluation produced one concrete, non-duplicative operational gap, subsequently implemented by #164/#165, while explicitly rejecting or deferring donor capabilities that duplicate current Podium behavior or lack a measured need. The decision record is therefore durable product evidence rather than archival-only material.

This disposition does not authorize donor code/data import or any policy replacement. This rebuilt documentation change still requires the repository's normal validation before merge.

## Follow-up rule

Override-layer and type-approval-crosswalk implementation must wait for measured evidence showing the current review or identifier-reconciliation path is insufficient. No donor data or code is authorized for import by this evaluation.
