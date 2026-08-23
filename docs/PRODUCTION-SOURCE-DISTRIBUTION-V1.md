# Production Source Distribution V1

Status: implemented bounded distribution gate.

## Decision

ADR-0001 applies: reuse the already selected official source families instead of introducing a generic acquisition platform. V1 measures retained evidence distribution across independently inspected source families and regions.

The frozen gate contains NHTSA vPIC and FuelEconomy.gov (US), EEA CO2 cars (EU), and Inmetro PBEV (BR). A passing slice requires at least three independently inspected source families, three regions, positive record counts, and no source family above 70% of retained benchmark records.

## Meaning

This closes the concrete distribution/corpus-breadth debt by making source diversity measurable and regression-tested. It does not claim exhaustive market coverage, heterogeneous-web completeness, or production-wide precision/recall. Those are product-scale operating measurements, not prerequisites for the bounded architecture process.

Permanent tests are offline and fail closed on uninspected evidence, insufficient geographic/source diversity, invalid counts, or excessive single-source dominance.
