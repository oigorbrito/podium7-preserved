# Web extraction source-family corpus characterization

Status: completed — integrated by PR #46 on 2026-08-23

## Outcome

Replace the documented `UNKNOWN` around broader web-extraction measurement with a reproducible source-family characterization of the existing Autoevolution extraction artifact, without changing extractor behavior before measuring it.

## Acceptance criteria

- freeze a broader set of factual Autoevolution configuration snapshots with source URLs and acquisition dates;
- cover multiple manufacturers, eras, powertrain/transmission variants, and both compatible and incompatible observed field shapes;
- curate expected target facts independently of extractor output;
- implement a deterministic evaluator reporting page success, field precision, field recall, and explicit failure reasons;
- evaluate the existing `AUTOEVOLUTION_ARTEGA_GT_RULES` unchanged in this work unit;
- preserve explicit failures rather than silently dropping unsupported fields;
- update `REPEATABLE-WEB-EXTRACTION-V1.md` with measured results and a clear evidence boundary;
- do not claim production-wide or heterogeneous-web precision/recall from this source-family corpus;
- repository CI green before integration.

## Boundaries

- this is new characterization, not a historical candidate retest;
- no generic browser/agent benchmark and no LLM/provider selection;
- no resolver/catalog-policy changes;
- no live-web dependency in CI; CI uses frozen snapshots;
- do not change extraction rules merely to improve the measured score inside the same characterization work unit.

## Sources of truth

- [`../../DEVELOPMENT-WORKFLOW.md`](../../DEVELOPMENT-WORKFLOW.md)
- [`../../INVARIANTS.md`](../../INVARIANTS.md)
- [`../../SCIENTIFIC-FOUNDATION.md`](../../SCIENTIFIC-FOUNDATION.md)
- [`../../REPEATABLE-WEB-EXTRACTION-V1.md`](../../REPEATABLE-WEB-EXTRACTION-V1.md)
- [`../../AI-DISCOVERY-V1.md`](../../AI-DISCOVERY-V1.md)

## Evidence basis

- `DOCUMENTED`: `REPEATABLE-WEB-EXTRACTION-V1.md` marked measured precision/recall on a broader page corpus as `UNKNOWN` before this work unit.
- `EVIDENCE_BACKED`: WebLists supports discover/configure/reuse; SODIUM, WideSearch, WebDS and WANDR support explicit evidence and measured completeness instead of inferring reliability from successful navigation.
- `ENGINEERING_CHOICE`: characterize the existing source-specific artifact first on a diverse Autoevolution source-family corpus before any heterogeneous-web claim or new architecture.
- `ENGINEERING_CHOICE`: freeze snapshots for reproducibility and keep live acquisition outside CI.

## Execution

1. Freeze a compact but diverse source-family corpus from independently inspected Autoevolution vehicle configuration tables.
2. Curate gold target facts and expected structural limitations from the inspected source evidence, independently of extractor output.
3. Add an evaluator and focused tests for dataset integrity and reproducible characterization.
4. Run the existing rules unchanged and record the observed metrics/failure modes.
5. Update the design record with what the measurement does and does not establish.
6. Self-review, PR, CI, integrate only when green, then archive this plan before selecting another gap.

## Validation evidence

Characterization dataset: `benchmarks/web_extraction_source_family_corpus_v1.json`, version `autoevolution-source-family-1.0`.

Measured on the unchanged `AUTOEVOLUTION_ARTEGA_GT_RULES`:

- configurations: 12 across 7 manufacturers;
- page successes: 8/12 (66.7%);
- explicit failures: 4/12 (33.3%);
- expected outcome agreement: 12/12;
- source target fields: 142;
- emitted/correct fields: 96/96;
- field precision: 1.000;
- field recall: 96/142 (67.6%);
- unsupported structures failed explicitly; no incorrect emitted field was observed.

Execution evidence:

- PR: #46 `Characterize reusable web extraction across source-family corpus`;
- initial measurement CI: run `32643262400`, job `97203527673`, repository suite `309/309` PASS;
- documentation/technical-debt confirmation CI: run `32643348081`, job `97203731915`, `HARNESS PASS`, runtime health PASS, repository suite `309/309` PASS;
- final merge-candidate CI after synchronizing with current `main`: run `32644783758`, job `97207268195`, Python `3.13.15`, `HARNESS PASS`, runtime health PASS, repository suite `309/309` PASS;
- final validation artifact: ID `9494566361`, SHA-256 `cdf48fdfad4879c12901132e06b8512c5416f401ec819322f044254cd8117e4a`;
- PR #46 squash merge commit: `dec7415aa6a3a074eaafb59fa48f362b69e6ce67`;
- extractor/rule change required in this characterization: **NO**.

The measured source-family coverage/generalization gap is recorded as `OPEN / LOCALLY_VERIFIED` in `TECH-DEBT.md`. Exact remediation remains deliberately unselected.

## Remaining blockers

None for this completed work unit. The broader source-family coverage/generalization gap remains separately tracked in `TECH-DEBT.md` and does not invalidate this characterization.
