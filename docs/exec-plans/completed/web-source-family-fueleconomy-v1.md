# FuelEconomy.gov web source family V1

Status: completed — integrated by PR #53 on 2026-08-23

## Outcome

Demonstrate whether Podium's deterministic extraction machinery can be reused on a second web source family while preserving source-specific provenance and refusing semantically incompatible values.

## Source selection

Selected: FuelEconomy.gov `Find a Car` vehicle pages, operated by the U.S. Department of Energy/EPA ecosystem. Official web-service documentation defines vehicle fields and currently covers 1984-current model years. The retained corpus stores only factual label/value observations needed for this benchmark.

Alternative OEM pages were not selected for this unit where copying/automation terms would make retained benchmark evidence less suitable.

## Acceptance criteria

- freeze a small second-family corpus with exact HTTPS source IDs and acquisition date;
- keep retained evidence to factual fields required by the benchmark;
- add a reusable FuelEconomy.gov artifact without modifying historical Autoevolution artifacts;
- ensure extraction-rule provenance names the actual source family;
- accept gasoline MPG and the PHEV gas-only label through an explicit alias;
- reject MPGe as gasoline MPG rather than converting it with the MPG rule;
- preserve valid facts alongside explicit issues in partial mode;
- record strict and partial precision/recall on independent gold;
- keep all historical Autoevolution gates green;
- integrate only with green merge-candidate CI.

## Boundaries

- no claim of arbitrary-web or production-wide generalization;
- no generic crawler/browser dependency;
- no MPGe-to-L/100km semantic mapping in this unit;
- no use of MSRP, tank-size, owner-reported MPG, images, or other third-party/non-target page content;
- no public distribution/license decision.

## Decision classification

- second-family measurement before broader generalization: `EVIDENCE_BACKED` direction;
- choosing FuelEconomy.gov for this characterization slice: `ENGINEERING_CHOICE` grounded in official, structured, current source evidence;
- exact three-field artifact and four-case corpus: `ENGINEERING_CHOICE`;
- measured metrics below: `LOCALLY_VERIFIED`.

## Measured result

Frozen dataset `fueleconomy-find-a-car-source-family-1.0`:

- strict: 2/4 pages succeed, 2/4 fail explicitly on MPGe, 4/4 expected outcomes agree, 6/6 emitted facts are correct, precision 1.000, recall 6/12;
- partial evidence: 10/10 emitted facts are correct, zero incorrect facts, 10/12 target facts retained, two explicit unresolved MPGe targets;
- official hyphenated drivetrain labels normalize to existing Podium drivetrain tokens while preserving raw source text;
- historical Autoevolution tests remain green.

## Final validation evidence

- PR: #53 `Characterize FuelEconomy.gov as a second web source family`;
- final merge-candidate run: `32648934964`, job `97217413777`;
- PR merge ref SHA: `030ab134b457cd1243703e17ac4bc02ad59a7db9`;
- validated branch head: `658c317a6a1740edb66db3e7d1b11921040b43d6`;
- Python `3.13.15`;
- `HARNESS PASS`;
- runtime health `PASS`;
- repository isolated suite `343/343` PASS;
- validation artifact ID `9495637426`, ZIP SHA-256 `1e7f9d0419747093d943c02d6a76a208d94771b0c117b21f794b9e11b22ebe12`;
- PR #53 squash merge commit: `773c2a2437c7c26370fe7b672c6749620cd74480`.

## Remaining blockers

None for this completed work unit. Heterogeneous-web/source-family acquisition and broader production characterization remain separately tracked in `TECH-DEBT.md`. MPGe normalization remains deliberately unselected until electric-efficiency semantics become decision-critical. Public distribution remains intentionally blocked by the private/proprietary release policy until a later explicit owner decision.
