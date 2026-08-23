# Frozen web acquisition evidence V1

Status: completed — integrated by PR #55 on 2026-08-23

## Outcome

Make the retained two-family web benchmark acquisition lineage explicit and reproducibly verifiable from source URL to frozen snapshot to SHA-256 content reference, without claiming live crawling or production navigation coverage.

## Why this unit

The repository had measured extraction behavior on Autoevolution and FuelEconomy.gov, while acquisition/navigation generalization remained unknown. Before adding a crawler or browser layer, the existing retained corpus needed a deterministic acquisition-evidence gate so missing, empty, non-HTTPS, duplicated, unpinned/orphaned, or mutated snapshots fail explicitly.

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

`LOCALLY_VERIFIED` on the retained web benchmark inventory integrated by PR #55:

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

## Final validation evidence

- PR: #55 `Verify frozen web acquisition evidence across source families`;
- validated branch head: `bd1d0814a4301b538f95095da1eb06a529e28048`;
- final merge-candidate run: `32650193728`, job `97220446755`;
- PR merge ref SHA: `fc55c7b0825db3a354c19c1a068fe7786799ff78`;
- Python `3.13.15`;
- `HARNESS PASS`;
- runtime health `PASS`;
- repository isolated suite `353/353` PASS;
- validation artifact ID `9495962447`, ZIP SHA-256 `a2452275dae82486eb6b29dfef980f3c0f07793a08f93034aa3eca22081c7669`;
- PR #55 squash merge commit: `63bd6cba46157f903034d88e0ba0a25d39d34f31`.

## Decision classification

- content-addressed retained acquisition evidence: `EVIDENCE_BACKED` direction from the project's existing provenance invariant;
- deriving the manifest from benchmark JSON instead of maintaining a second inventory: `ENGINEERING_CHOICE` to avoid divergent ledgers;
- pinning repository blob identities separately from generated SHA-256 evidence references: `ENGINEERING_CHOICE` to make retained snapshot mutation fail explicitly;
- exact issue codes/report shape: `ENGINEERING_CHOICE`;
- measured frozen-corpus acquisition-evidence coverage above: `LOCALLY_VERIFIED`;
- live navigation, source discovery, crawling completeness and production source distribution: `UNKNOWN` and outside this completed unit.

## Remaining debt

None for retained-snapshot lineage/integrity on the current two frozen corpora. `TECH-DEBT.md` separately retains live acquisition/navigation/source-discovery generalization and broader production source distribution/corpus coverage as open measurement problems. This work unit does not justify selecting a generic crawler/browser/agent dependency.
