# Podium 7 Data Fusion and Conflicts V1

**Work unit:** `PODIUM7_DATA_FUSION_AND_CONFLICTS_V1`

## Scientific basis

MaDI-Bench separates conflict resolution/data fusion as its own integration stage. DTBench reinforces that conflict resolution remains a hard problem.

## V1 policy

- one candidate: canonicalize with provenance;
- multiple candidates with identical normalized value+unit: canonicalize by unanimous agreement;
- disagreement: create `Unresolved Conflict` and do not select a silent winner;
- every canonical decision records all candidate references and provenance.

## Classification

- explicit conflict preservation: `EVIDENCE_BACKED`
- v1 single/unanimous policy: `ENGINEERING_CHOICE`

## Gate

- `CONFLICTS_PRESERVED = YES`
- `DECISIONS_TRACEABLE = YES`
- fusion tests: 6/6 PASS, run individually
- cumulative tests run individually: 28/28 PASS
