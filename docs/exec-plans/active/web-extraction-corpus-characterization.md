# Web extraction source-family corpus characterization

Status: active — characterization complete; integration pending final green merge candidate

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
- validation artifact for run `32643348081`: ID `9494197654`, SHA-256 `09ecbc58de92ee74248ef59ac3d7f3f110e0b9463d729613c63eb4b3df892bed`;
- extractor/rule change required in this characterization: **NO**.

The measured source-family coverage/generalization gap is recorded as `OPEN / LOCALLY_VERIFIED` in `TECH-DEBT.md`. Exact remediation remains deliberately unselected.

## Remaining blockers

Only final green validation/integration of the current merge candidate; no external or product-decision blocker.
