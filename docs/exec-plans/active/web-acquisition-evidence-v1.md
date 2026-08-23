# Frozen web acquisition evidence V1

Status: active — implementation and measured characterization complete; final documented merge-candidate validation/integration pending

## Outcome

Make the retained two-family web benchmark acquisition lineage explicit and reproducibly verifiable from source URL to frozen snapshot to SHA-256 content reference, without claiming live crawling or production navigation coverage.

## Why this unit

The current repository has measured extraction behavior on Autoevolution and FuelEconomy.gov, but `TECH-DEBT.md` still correctly marks acquisition/navigation generalization as unknown. Before adding a crawler or browser layer, the existing retained corpus needs a deterministic acquisition-evidence gate so missing, empty, non-HTTPS, duplicated, or mutated snapshots fail explicitly.

## Acceptance criteria

- derive one manifest from the two existing web benchmark datasets rather than duplicating their case inventory;
- require stable case identity, source family, exact HTTPS source URL, and frozen snapshot path;
- produce SHA-256 content-addressed references using the existing evidence primitive;
- verify every current snapshot exists, is non-empty, and still matches its pinned repository blob identity;
- allow multiple configurations to share one source URL while keeping snapshots distinct;
- reject duplicate `(source_family, case_id)` identities and duplicate snapshot ownership;
- report deterministic cross-family coverage metrics and explicit issues;
- add a reproducible CLI and focused tests;
- preserve all existing extraction behavior and package dependency-free status;
- document clearly that live acquisition/navigation completeness remains UNKNOWN;
- integrate only with green merge-candidate CI and normal concurrency/self-review gates.

## Measured result

`LOCALLY_VERIFIED` on the current retained web benchmark inventory:

- source families: 2 (`autoevolution`, `fueleconomy_gov`);
- benchmark cases: 16;
- unique exact HTTPS source URLs: 13;
- declared frozen snapshots: 16;
- snapshots verified against pinned repository blob identity: 16/16;
- snapshots producing verified SHA-256 content-addressed references: 16/16;
- acquisition-evidence issues on the retained corpus: 0;
- duplicate snapshot ownership: 0;
- orphan snapshot pins: 0.

Focused negative cases verify explicit failure for missing snapshots, empty snapshots, mutated snapshot content, missing/orphan pins, duplicate case identity, duplicate snapshot ownership and non-HTTPS source locators. Multiple benchmark cases may legitimately share one source URL when their retained snapshots are distinct.

Implementation validation run `32650010396`, job `97219999963`: Python 3.13.15, `HARNESS PASS`, runtime health PASS, repository isolated suite `353/353` PASS, validation artifact ID `9495914846`, ZIP SHA-256 `9074cfa7f5c59fe3d86e573d5987436efcc6d70d8048b6ca4d5527bff81c33db`.

This run validates the implementation head before the final documentation updates. Integration still requires green CI on the resulting documented merge candidate plus normal concurrency/self-review gates.

## Decision classification

- content-addressed retained acquisition evidence: `EVIDENCE_BACKED` direction from the project's existing provenance invariant;
- deriving the manifest from benchmark JSON instead of maintaining a second inventory: `ENGINEERING_CHOICE` to avoid divergent ledgers;
- pinning repository blob identities separately from generated SHA-256 evidence references: `ENGINEERING_CHOICE` to make retained snapshot mutation fail explicitly;
- exact issue codes/report shape: `ENGINEERING_CHOICE`;
- measured frozen-corpus acquisition-evidence coverage above: `LOCALLY_VERIFIED`;
- live navigation, source discovery, crawling completeness and production source distribution: `UNKNOWN` and outside this unit.
