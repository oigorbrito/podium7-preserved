# Podium 7 Catalog Year Semantics V1

Status: **selected product rule; regression gate**.

## Purpose

This slice records the selected Podium 7 rule for manufacturing year versus model year and protects it as a focused source-backed regression.

Dataset:

```text
benchmarks/catalog_identity_year_semantics_challenge_v1.json
```

The slice is deliberately small and diagnostic. It is not a production-quality estimate.

## Evidence

The slice uses primary/official sources only:

- Senatran/SERPRO exposes `Ano Fabricação` and `Ano Modelo` as separate RENAVAM fields: `https://centraldeajuda.serpro.gov.br/consultasenatran/veiculo/`.
- FIPE explicitly states that the vehicle year in its lookup refers to **model year**: `https://www.fipe.org.br/pt-br/indices/veiculos`.
- Toyota do Brasil's May 2024 public-price sheet publishes Corolla Cross XRX Hybrid with `2024 / 2025` year/model notation: `https://media.toyota.com.br/dbff4f05-d6ed-47e8-bb7d-073369a7cff7.pdf`.
- Toyota do Brasil's June 2025 public-price sheet publishes Corolla Cross XRX Hybrid with `2025 / 2026` notation: `https://media.toyota.com.br/197da502-db1f-45c6-9608-16fdd530929a.pdf`.

These sources establish that manufacture year and model year are separate concepts and that the same named configuration can appear across adjacent model years. The owner selected the Podium 7 canonical matching rule on 2026-08-23.

## Selected product rule

1. Preserve manufacture-year and model-year as separate identity dimensions, aligned with Senatran/RENAVAM field semantics.
2. If both sides explicitly provide a year dimension and the ranges do not overlap, that dimension is a deterministic contradiction and produces `NO_MATCH`.
3. Missing manufacture-year evidence alone is not a contradiction when explicit model year and the other required identity evidence agree.
4. If model year is explicit on only one side, structural agreement alone does not justify automatic `MATCH`; route to `REVIEW` unless stronger identity evidence establishes the identity.
5. Preserve the product priority `false merges > missed duplicates > review volume`.

A shared `STRONG` external identifier remains capable of establishing a match after explicit contradiction checks. FIPE remains `SUPPORTING`, so it does not bypass incomplete model-year evidence by itself.

## Regression composition

Version `year-semantics-1.1` contains six cases:

```text
2 MATCH
3 NO_MATCH
1 REVIEW
```

The cases cover:

- same model year/configuration with explicit non-overlapping manufacture years → `NO_MATCH`;
- missing manufacture year with explicit matching model year → `MATCH`;
- adjacent explicit model years → `NO_MATCH`;
- explicit model year versus missing model year → `REVIEW`;
- overlapping manufacture-year ranges with matching model year → `MATCH`;
- same manufacture year with contradictory model years → `NO_MATCH`.

The expected outcomes are now product decisions rather than unresolved characterization labels. CI requires the resolver to reproduce all six exactly.

## Boundary

This rule does not collapse the two official year fields, infer a missing model year, or reinterpret legacy `year_from/year_to`. Any future change requires new evidence, an explicit product decision, and an updated regression dataset.
