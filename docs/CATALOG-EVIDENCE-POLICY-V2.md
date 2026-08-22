# Podium 7 Catalog Evidence Policy V2

Status: **internal publication policy; does not freeze the external JSON contract**.

## Purpose

This policy defines the minimum evidence gate before a catalog identity change is treated as externally publishable. It complements Catalog Identity V2/V2.1 without changing SQLite schema or payload shape.

## Actions

The policy distinguishes three actions:

- `CREATE`: first externally publishable identity for a catalog vehicle;
- `CORRECTION`: evidence-backed change to an existing published identity;
- `ADMINISTRATIVE_OVERRIDE`: explicit manual exception when normal evidence-backed publication is not available or must be superseded.

## Minimum evidence

Normal `CREATE` and `CORRECTION` require:

1. `DecisionStatus.EVIDENCE_BACKED`;
2. at least one non-empty evidence reference for the change;
3. for `CORRECTION`, a non-empty reason.

`HYPOTHESIS`, `UNKNOWN`, `LOCALLY_VERIFIED` and `ENGINEERING_CHOICE` are not sufficient labels for normal external publication.

This gate validates the minimum publication decision. Persistence remains responsible for proving that referenced evidence actually exists and for preserving the full source → raw evidence → candidate → normalization → resolution → canonical chain.

## Administrative override

An administrative override is intentionally not disguised as evidence-backed data. It requires:

- `DecisionStatus.ENGINEERING_CHOICE`;
- a non-empty `actor_id`;
- a non-empty reason.

Evidence references may still be attached and preserved, but are not mandatory for the override itself. An override therefore remains auditable as an engineering/manual decision rather than being mislabeled as source evidence.

## Change impact

`catalog_change_impact()` returns:

- `NO_CHANGE`: no catalog change;
- `INFORMATIONAL`: serialized content changed without changing semantic catalog identity;
- `IDENTITY`: semantic identity changed.

Identity-changing examples include:

- make/model/generation/variant/powertrain/transmission/body-style/market changes;
- manufacturing-year or model-year changes;
- alias or engine-identifier semantic changes;
- changes to external identifiers whose namespace is `STRONG` or `SUPPORTING`.

Informational examples include:

- case/punctuation-only edits that preserve normalized identity tokens;
- adding/removing a `REFERENCE_ONLY` or unknown external identifier.

This distinction is conservative: if a change can affect entity resolution, it is treated as `IDENTITY`.

## External identifiers

The V2.1 namespace registry remains authoritative:

- `STRONG` and `SUPPORTING` identifier changes are identity-affecting;
- `REFERENCE_ONLY` and unknown namespace changes are informational unless another identity dimension changes;
- FIPE remains `SUPPORTING`.

## Non-goals

This policy does not:

- freeze JSON naming/casing;
- introduce a consumer API;
- expose a provenance/audit API;
- change catalog persistence schema;
- automatically choose or synthesize evidence.

Those remain separate gates.
