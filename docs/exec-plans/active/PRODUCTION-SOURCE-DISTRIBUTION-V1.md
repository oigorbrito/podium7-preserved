# Production Source Distribution V1 execution plan

Status: active

## Outcome

Turn the remaining source-distribution/corpus-breadth debt into a bounded, measurable regression gate over independently inspected official source families.

## Boundaries

- Reuse NHTSA vPIC, FuelEconomy.gov, EEA CO2 cars and Inmetro PBEV evidence already selected under ADR-0001.
- No new crawler, browser, orchestration platform or permanent live-network CI gate.
- Require three regions, three source families and bounded source dominance.
- Do not claim exhaustive production coverage or global precision/recall.

## Acceptance

Implementation, frozen benchmark, deterministic tests, design record, green official CI, concurrency recheck, squash merge, then archive/clear current work.
