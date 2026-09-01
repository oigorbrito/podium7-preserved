# Podium 7 operational multi-source contract v2 — draft

Status: `DRAFT_NOT_ACCEPTED`

Decision dependency: `ADR-0002-OPERATIONAL-MULTISOURCE-PROVENANCE.md`

Purpose: freeze a falsifiable input/validation contract for the `PRESERVE_FIELD_LEVEL_MULTI_SOURCE_REPLAY` option without selecting that option or changing runtime behavior.

The existing v1 single-source operational path remains authoritative until ADR-0002 is accepted and a later implementation passes its gates.

## Evidence boundary

Wave 01 classifies the 48 blocked retained record-sides as:

- `COMPOSITE_SUPPORT = 36`;
- `VERIFIED_SINGLE_SOURCE = 10`;
- `INSUFFICIENT_SINGLE_SOURCE_SUPPORT = 2`.

Current code establishes that `CatalogBatchEnvelope` and `ingest_catalog_record` are one-source/one-evidence per observation, while canonical facts, provenance derivations, and review field bindings already support more granular evidence relationships. Therefore v2 is specified as a versioned input/reconciliation contract; it does not assume a replacement storage subsystem.

## Proposed semantic envelope

```text
record
  contractVersion = "podium7.catalog-operational.v2"
  recordId
  vehicle
  provenance
    sources[]
    evidence[]
    fieldEvidence
      <present vehicle field> -> one-or-more evidence ids
```

Each evidence object is bound to exactly one declared source.

Illustrative payload:

```json
{
  "contractVersion": "podium7.catalog-operational.v2",
  "recordId": "example:t-cross:highline",
  "vehicle": {
    "make": "Volkswagen",
    "model": "T-Cross",
    "generation": "2019 Brazil generation",
    "variant": "Highline 250 TSI",
    "powertrain": "250 TSI flex",
    "transmission": "6-speed automatic",
    "market": "BR"
  },
  "provenance": {
    "sources": [
      {"id": "vw-generation", "name": "Volkswagen generation source", "locator": "https://example.invalid/generation"},
      {"id": "vw-configuration", "name": "Volkswagen configuration source", "locator": "https://example.invalid/configuration"}
    ],
    "evidence": [
      {"id": "ev-generation", "sourceId": "vw-generation", "locator": "https://example.invalid/generation/t-cross", "retrievedAt": "2026-08-31T12:00:00+00:00", "acquisitionMethod": "fixture", "rawContentRef": "fixture:generation"},
      {"id": "ev-configuration", "sourceId": "vw-configuration", "locator": "https://example.invalid/configuration/t-cross", "retrievedAt": "2026-08-31T12:00:00+00:00", "acquisitionMethod": "fixture", "rawContentRef": "fixture:configuration"}
    ],
    "fieldEvidence": {
      "make": ["ev-generation", "ev-configuration"],
      "model": ["ev-generation", "ev-configuration"],
      "generation": ["ev-generation"],
      "variant": ["ev-configuration"],
      "powertrain": ["ev-configuration"],
      "transmission": ["ev-configuration"],
      "market": ["ev-generation", "ev-configuration"]
    }
  }
}
```

The example defines representation only; it authorizes no retained benchmark mutation.

## Structural invariants

A conforming v2 validator MUST fail closed unless:

1. `contractVersion` is the supported v2 version.
2. `recordId` is non-empty text.
3. `vehicle` satisfies the existing catalog identity contract.
4. `sources` is non-empty and source ids are unique.
5. `evidence` is non-empty and evidence ids are unique.
6. every evidence `sourceId` resolves to one declared source.
7. every present vehicle field has `fieldEvidence`.
8. `fieldEvidence` names no absent vehicle field.
9. each present field has at least one evidence reference.
10. every field evidence id resolves to declared evidence.
11. duplicate evidence ids per field are deterministically rejected or canonicalized without increasing corroboration count.
12. presence of a source never implies attribution of an unbound field.
13. source/evidence input ordering does not alter normalized semantics.
14. field-evidence ordering does not alter normalized semantics.
15. unresolved conflicts are not converted into accepted facts by normalization.

## Canonicalization

Equivalent payloads MUST normalize identically regardless of input ordering. Sources and evidence normalize by stable ids; field names and per-field evidence references use one frozen deterministic ordering. Canonicalization MUST NOT choose a preferred source/evidence, infer missing attribution, merge evidence by locator similarity, or rewrite identity values.

## Fail-closed rejection matrix

| Code | Condition |
| --- | --- |
| `UNSUPPORTED_CONTRACT_VERSION` | version absent, malformed, or unsupported |
| `INVALID_RECORD_ID` | record id absent or empty |
| `INVALID_VEHICLE` | vehicle violates existing identity contract |
| `MISSING_SOURCES` | no source declared |
| `DUPLICATE_SOURCE_ID` | source id repeated |
| `MISSING_EVIDENCE` | no evidence declared |
| `DUPLICATE_EVIDENCE_ID` | evidence id repeated |
| `UNKNOWN_EVIDENCE_SOURCE` | evidence references undeclared source |
| `MISSING_FIELD_EVIDENCE` | present field lacks binding |
| `EXTRANEOUS_FIELD_EVIDENCE` | binding names absent vehicle field |
| `EMPTY_FIELD_EVIDENCE` | present field has zero evidence ids |
| `UNKNOWN_FIELD_EVIDENCE` | binding references undeclared evidence |
| `DUPLICATE_FIELD_EVIDENCE` | repeated field evidence when reject policy is selected |

Human-readable messages may change without changing these codes.

## Source qualification boundary

Structural provenance validity is not source authority:

`FIELD_PROVENANCE_VALID != SOURCE_QUALIFIED != IDENTITY_DETERMINISTIC`

Existing rules such as `FIPE SUPPORTING != AUTOMATIC IDENTITY` remain unchanged.

## Conflict boundary

Multiple evidence references do not imply agreement. Conflicting attributed evidence must remain candidate/conflict/review evidence and must not be fused into accepted fact merely because the envelope is structurally valid.

## v1 compatibility

Every valid v1 record must have a semantics-preserving v2 projection:

```text
v1 source -> one v2 source
v1 evidence -> one v2 evidence
all present vehicle fields -> [that evidence id]
```

Equivalent v1/v2 input must produce the same normalized identity and CREATE/MATCH/REVIEW decision. The v1 path remains supported during migration.

## Ingestion/review mapping target

If ADR-0002 selects Option B, implementation should reuse existing storage where it already supports the semantics:

- create one candidate fact per `(vehicle field, evidence)` supplied;
- allow multiple candidate facts for a field when multiple evidence objects support it;
- preserve evidence ids through canonical fact/conflict references;
- for REVIEW, persist supplied field/source/evidence bindings instead of deriving all bindings from one evidence id;
- after CREATE, MATCH, or REVIEW, retain a reconstruction path to field-level provenance.

## Required implementation tests if Option B is accepted

1. valid two-source complete envelope parses deterministically;
2. reversed source/evidence arrays normalize identically;
3. reversed field evidence arrays normalize identically;
4. missing present-field binding fails closed;
5. unknown evidence source fails closed;
6. unknown field evidence fails closed;
7. duplicate source id fails closed;
8. duplicate evidence id fails closed;
9. source/evidence mismatch fails closed;
10. supporting-only source is not promoted to automatic identity authority;
11. equivalent v1/v2 single-source records produce the same resolver decision;
12. CREATE preserves field provenance;
13. MATCH preserves field provenance;
14. REVIEW preserves field provenance;
15. conflicting evidence remains conflict/review evidence;
16. replay output is invariant to source/evidence input order.

## Relationship to the split-replay experiment

PR #282 establishes that naive sequential source splitting is order-sensitive under current ingestion: the first partial observation becomes canonical and the complementary observation routes to REVIEW. That rejects the sequential-split shortcut, but does not prove this v2 contract correct.

## Decision state

`ADR-0002 = DECISION_REQUIRED`

`MULTISOURCE_V2_CONTRACT = SPECIFIED_FOR_EVALUATION_ONLY`

No runtime, benchmark, resolver, source qualification, replay threshold, or publication behavior changes here.
