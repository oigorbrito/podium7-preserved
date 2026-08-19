# Podium 7 Selective Review V1

**Work unit:** `PODIUM7_SELECTIVE_REVIEW_V1`

Review is routed selectively for identity ambiguity, unresolved conflicts, unknown sources, schema failures, and anomalies. Deterministic resolved identity outcomes and known/valid/non-anomalous evidence remain automatic.

No arbitrary numeric confidence threshold is introduced.

## Gate

- `SAFE_HIGH_CONFIDENCE_PATH = AUTOMATIC` (categorical deterministic path)
- `AMBIGUOUS_PATH = REVIEW / UNRESOLVED`
- selective review tests: 5/5 PASS, run individually
- cumulative tests run individually: 49/49 PASS
