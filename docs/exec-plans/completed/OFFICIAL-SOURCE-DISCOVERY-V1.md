# Official Source Discovery V1 execution plan

Status: completed

## Outcome

Implemented bounded deterministic U.S.-market vehicle candidate discovery using the already-selected official NHTSA vPIC and FuelEconomy.gov menu paths.

## Boundaries preserved

- Discovery produces candidates/locators only; it is not canonical identity proof.
- Reused prior live source-selection evidence from run `32655508584`; no historical candidate-evaluation batch was repeated.
- Preserves source-native identifiers and exact discovery locators as provenance.
- Added no generic crawler, browser, agent, scheduler, or permanent public-network CI dependency.
- Permanent tests remain offline/deterministic.
- Market-first ADR disposition: `ADAPT` the mature official APIs already evaluated; no infrastructure build was justified.

## Acceptance evidence

- NHTSA `GetModelsForMakeYear` parser preserves NHTSA make/model IDs and fails on incompatible count/make/ID semantics.
- FuelEconomy.gov model-menu parser preserves source model keys and handles list/singleton `menuItem` shapes.
- FuelEconomy.gov options parser preserves positive numeric vehicle IDs and source option labels.
- Conflicting duplicate source IDs/keys fail explicitly; identical duplicates are deterministic.
- Every `DiscoveryCandidate` is locked to `evidence_role="discovery_candidate"` and `identity_proof=False`.
- `docs/OFFICIAL-SOURCE-DISCOVERY-V1.md` records semantics, nonclaims, prior live evidence, and the market-first decision.
- Offline benchmark: `benchmarks/official_source_discovery_v1.json` plus permanent unit tests.

## Final validation and integration

PR: #68 `Implement official source discovery V1`.

Final PR merge-candidate CI: GitHub Actions run `32666764350`, job `97261252745`, Python 3.13.15. Harness PASS, generated repository facts PASS, runtime health PASS, isolated suite **410/410 PASS**.

Validation artifact: ID `9500244480`, ZIP SHA-256 `9a3f8ed418812f812e3302fa9f2dd7394decf0e2355cfe2e559344bb3b92ce2b`. The artifact was downloaded to local task storage for inspection; `test-report.json` records 410 discovered / 410 passed and no failed test.

Before integration, `main` was rechecked against the PR base `b7f904b65f9eaed46be24780fda0619215e430cb` and was identical (no concurrent commits). PR #68 was marked ready and squash-merged with expected head `0f4fbfabaa8751634ac6635d341a12d2736594cd`.

Integrated `main` commit: `dacb9c9a862172a17f39e8dad5928e349335bbf8`.

## Remaining durable debt

- recurring-operation robots/rate/politeness and host pacing before broad scheduled acquisition;
- strengthened network target binding / SSRF-DNS-rebinding defense before arbitrary untrusted locators;
- Inmetro PBEV machine-readable or deliberate document-path characterization only when Brazilian coverage becomes active;
- broader production source-family/corpus coverage only with independently inspected evidence and measured failure modes.
