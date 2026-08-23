# Web extraction explicit partial evidence V1

Status: completed — integrated by PR #49 on 2026-08-23

## Outcome

Preserve correctly extracted source facts even when a strict reusable web artifact encounters a missing or unsupported field, while keeping strict extraction failure semantics unchanged and recording every per-field problem explicitly.

## Acceptance criteria

- strict `extract_with_rules()` behavior remains fail-fast compatible for existing callers;
- add a deterministic report path that returns extracted facts plus explicit per-field issues instead of discarding earlier valid facts;
- support validated label aliases without ambiguous matching;
- preserve the exact observed source label when an alias is used;
- do not invent values for absent fields or coerce non-scalar weight ranges into scalar `curb_weight`;
- characterize the report path on the frozen 12-case Autoevolution corpus;
- preserve field precision and materially improve retained correct-field recall versus the strict all-or-nothing path;
- update design/debt documentation and integrate only with green CI.

## Boundaries

- no historical external-candidate retest;
- no live-web CI dependency;
- no browser/agent/LLM selection;
- no new canonical semantics for non-scalar curb-weight ranges;
- no weakening of the existing strict extraction API.

## Evidence basis

- the frozen corpus has 8/12 strict successes, 96/96 correct emitted fields and 96/142 strict field recall;
- two failing snapshots omit one artifact field entirely;
- two failing snapshots expose non-scalar curb-weight ranges that must not be collapsed to an arbitrary scalar;
- one of those also uses the observed label variant `Combined (EPA)`;
- validated extraction artifacts already support explicit reusable rule sets, so the smallest extension is deterministic per-field reporting plus validated aliases rather than a new generic agent layer.

## Implemented behavior

- `extract_with_rules_report()` returns independently valid facts plus `MISSING_FIELD`, `PARSER_MISMATCH`, or `AMBIGUOUS_LABEL` issues;
- strict `extract_with_rules()` remains fail-fast and raises on the first report issue;
- validated extraction artifacts may declare non-conflicting label aliases;
- extracted facts preserve `source_label`, so alias use does not erase the observed source representation;
- non-scalar weight ranges remain unresolved and their raw values are preserved on issues;
- `scripts/run_web_extraction_corpus.py --partial-evidence` exposes the reproducible report path while the existing default remains strict.

## Measured source-family result

On frozen `autoevolution-source-family-1.0`:

- strict page success remains 8/12;
- partial-evidence cases without issues: 8;
- cases with explicit issues: 4;
- explicit issues: 4;
- source target fields: 142;
- emitted/correct fields: 140/140;
- incorrect emitted fields: 0;
- unresolved source target fields: 2;
- field precision: 1.000;
- retained field recall: 140/142 (98.6%).

The two unresolved source target facts are the observed non-scalar curb-weight ranges. Missing artifact fields in the BMW and Onix snapshots remain explicit issues but are not source target facts in those snapshots.

## Validation evidence

Initial PR #49 merge-candidate CI:

- run `32645262641`, job `97208443783`;
- Python `3.13.15`;
- `HARNESS PASS`;
- runtime health `PASS`;
- repository isolated suite `318/318` PASS;
- validation artifact ID `9494692401`, ZIP SHA-256 `8ed75a04a3924eef2d0c3cb7b48da94dbec6fe94616f000c1658c5e1f19f3cdc`.

Final PR #49 merge-candidate CI after provenance and documentation refinements:

- run `32645470301`, job `97208957129`;
- PR merge ref SHA `9f3ab64baafb3bc32cf3b22a3931abd1b087bbbd`;
- Python `3.13.15`;
- `HARNESS PASS`;
- runtime health `PASS`;
- repository isolated suite `318/318` PASS;
- validation artifact ID `9494746311`, ZIP SHA-256 `4aa00d592595d3c89ee6c9dd4a847d8d6e9f8e1581869de62f36b924d12dd86e`;
- PR #49 squash merge commit `bfd5b6d9e6d7f4f5189f56bef79385dd479b9d78`.

## Remaining blockers

None for this completed work unit. The unresolved non-scalar range semantics and heterogeneous-web generalization boundary remain tracked in `TECH-DEBT.md`; neither is silently coerced or claimed solved here.
