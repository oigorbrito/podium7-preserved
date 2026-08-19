# Podium 7 Document Extraction V1

**Work unit:** `PODIUM7_DOCUMENT_EXTRACTION_V1`

## Scientific basis

DTBench motivates preserving original evidence and validating document-to-structured extraction. PARSE motivates schema validation; W3C PROV motivates traceability.

## V1 source

A factual snapshot from a Ford Brasil newsroom document about Mustang Dark Horse is retained under `data/raw/documents/`. It contains model, engine, power and torque facts.

## Pipeline

`document snapshot -> required-field schema -> CandidateFact -> normalization`

No canonical fact is overwritten directly.

## Gate

- `ORIGINAL_EVIDENCE_PRESERVED = YES`
- `SCHEMA_VALIDATED = YES`
- `DIRECT_OVERWRITE = NO`
- document extraction tests: 4/4 PASS, run individually
- cumulative tests run individually: 40/40 PASS
