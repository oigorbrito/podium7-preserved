# Podium 7 AI Discovery V1

**Work unit:** `PODIUM7_AI_DISCOVERY_V1`

AI is not required for every known page. V1 defines the boundary `AI proposal -> validated reusable artifact`.

`validate_extraction_artifact()` accepts a proposed extraction configuration only when source identity, rule fields, regex syntax, capture groups, and attribute uniqueness validate deterministically. Validated rules can then run through the existing repeatable extractor.

## Classification

- AI/configuration instead of mandatory repeated inference: `EVIDENCE_BACKED` direction from WebLists and Steiner & Bizer 2026.
- JSON artifact schema and regex validation: `ENGINEERING_CHOICE`.
- any specific LLM/provider: `UNKNOWN / NOT SELECTED`.

## Gate

- `LLM_OUTPUT -> VALIDATED_REUSABLE_ARTIFACT = IMPLEMENTED`
- fresh LLM inference required for reuse: `NO`
- artifact validation tests: 4/4 PASS, run individually
- cumulative tests run individually: 44/44 PASS
