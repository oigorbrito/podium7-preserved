# EEA Semantic Expansion V2 execution plan

Status: active

## Outcome

Close the final bounded source-family debt by expanding EEA diesel/diesel-electric fuel semantics from official classifications and explicitly resolving the retail-identity boundary.

## Market-first / evidence decision

No new infrastructure is required. Reuse the existing EEA structured parser and Podium normalization. Official EEA metadata is the primary semantic reference; the 2025 provisional Datahub publication confirms the source family remains current.

## Boundaries

- Enumerate only official fuel type/mode combinations needed for diesel and diesel/electric semantics.
- Unknown combinations remain explicit failures.
- EEA type/variant/version remain regulatory evidence and are not canonical retail identity proof.
- Permanent tests remain offline; live EEA availability is not a CI gate.

## Acceptance

Source-backed frozen benchmark, parser mappings, explicit identity non-proof contract, deterministic tests, design record, green official CI, concurrency recheck, squash merge, archive and clear remaining debt.
