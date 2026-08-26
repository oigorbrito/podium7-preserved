# Catalog Provenance Audit V1

Issue: #152
Parent: #141 / mission #139

## Outcome
Prove persisted provenance completeness for the expanded operating corpus rather than treating input locators as proof of the persisted chain.

## Scope
- audit canonical vehicle → persisted candidate facts;
- audit candidate → raw evidence → source;
- audit open review task → raw evidence → source;
- audit canonical consumer lookup resolves to the same canonical ID;
- emit explicit incomplete-link records and completeness rate.

## Boundaries
No inferred provenance, resolver/evidence/fusion/source/publication changes, source expansion, or policy relaxation.

## Validation
Focused tests cover the V3 source-backed replay and deliberate persisted-link corruption. Repository harness, sequential tests and PR CI remain required before integration; #112 remains the known hosted-runner blocker.
