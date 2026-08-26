# Field Source Provenance V1

Status: implementation prepared; executable validation pending

Issue: #144
Parent mission: #139
Related measurement: #141

## Problem

The retained catalog identity gold schema records `sourceIds` at case level. That is enough to preserve which sources support the curated comparison as a whole, but it is insufficient to prove which source supports a particular identity dimension. Reporting per-dimension source contribution from those case-level lists would therefore fabricate provenance.

## Additive contract

A benchmark case may now include:

```json
{
  "fieldSourceIds": {
    "left": {
      "model_year_from": ["source-a"],
      "transmission": ["source-b", "source-c"]
    },
    "right": {
      "model": ["source-a"]
    }
  }
}
```

The mapping is optional. Existing `podium7.catalog-identity-golden.v1` files remain valid without it.

## Fail-closed validation

Each explicit attribution must satisfy all of the following:

- side is exactly `left` or `right`;
- field is a real `CatalogVehicleIdentity` field;
- the field is actually present on that side of the case;
- attribution is a non-empty list;
- every source ID is non-empty and unique;
- every attributed source is already present in the case's `sourceIds`.

Unknown sources, unknown fields, absent-field attribution, duplicate source IDs, malformed mappings and empty lists are rejected.

## Measurement semantics

`measure_field_source_contribution` counts only explicit field attribution. It reports:

- total present field observations;
- explicitly attributed field observations;
- overall attribution coverage;
- total, attributed and unattributed counts by dimension;
- attribution coverage by dimension;
- source contribution counts by dimension.

A field supported by more than one explicitly declared source counts once toward attributed-field coverage and once for each declared source in contribution counts. This preserves corroboration rather than forcing a single-source winner.

## Legacy behavior

Legacy cases without `fieldSourceIds` remain loadable. Their fields are reported as unattributed. The loader and measurement code do not infer attribution from:

- case-level `sourceIds`;
- source descriptions or `supports` prose;
- rationale text;
- lexical similarity;
- source-family scope.

This makes missing attribution visible instead of silently manufacturing completeness.

## Safety / nonclaims

- No resolver, evidence-strength, fusion, ambiguity or publication rule changes.
- No historical field is retroactively attributed by this implementation.
- A field-level attribution states provenance of benchmark evidence only; it does not promote the source or field to `STRONG` identity evidence.
- Complete field-level source contribution for the production-scale corpus remains a separate data-curation question and must be supported by retained inspectable evidence.
