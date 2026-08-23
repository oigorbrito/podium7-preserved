# Official Source Discovery V1 execution plan

Status: active

## Outcome

Implement bounded deterministic U.S.-market vehicle candidate discovery using the already-selected official NHTSA vPIC and FuelEconomy.gov menu paths.

## Boundaries

- Discovery produces candidate identities/locators only; it is not canonical identity proof.
- Reuse the prior live source-selection evidence from run `32655508584`; do not repeat that probe merely to reconstruct fixtures.
- Preserve source-native identifiers and exact discovery locators as provenance.
- No new generic crawler, browser, agent, scheduler, or public-network CI dependency.
- CI and permanent tests remain offline/deterministic.
- Market-first ADR disposition: `ADAPT` the mature official APIs already evaluated; no infrastructure build is justified for this capability.

## Acceptance criteria

1. NHTSA `GetModelsForMakeYear` payloads yield bounded source-specific model candidates with NHTSA make/model IDs.
2. FuelEconomy.gov model-menu payloads yield source-specific model candidates, and options-menu payloads yield vehicle-ID candidates.
3. Malformed, ambiguous, or semantically incompatible response shapes fail explicitly rather than silently widening discovery.
4. Candidate records explicitly state that discovery is not identity proof.
5. Tests are offline and cover successful parsing, singleton/list menu shapes, duplicate handling, malformed inputs, and provenance.
6. Design documentation records the semantics and prior live evidence boundary.
7. Harness, focused tests, full isolated suite, PR CI, concurrency recheck, and squash merge pass.
8. After integration, archive this plan and restore `CURRENT-WORK: none` in a separate housekeeping PR if needed.
