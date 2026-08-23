# Podium 7 Catalog Year Semantics Challenge V1

Status: **characterized; product decision required before resolver semantics change**.

## Purpose

This challenge slice isolates the open question around manufacturing year versus model year without weakening the existing golden regression datasets or changing `resolve_catalog_pair()`.

Dataset:

```text
benchmarks/catalog_identity_year_semantics_challenge_v1.json
```

The slice is deliberately small and diagnostic. It is not a production-quality estimate.

## Evidence

The challenge uses primary/official sources only:

- Senatran/SERPRO exposes `Ano Fabricação` and `Ano Modelo` as separate RENAVAM fields: `https://centraldeajuda.serpro.gov.br/consultasenatran/veiculo/`.
- FIPE explicitly states that the vehicle year in its lookup refers to **model year**: `https://www.fipe.org.br/pt-br/indices/veiculos`.
- Toyota do Brasil's May 2024 public-price sheet publishes Corolla Cross XRX Hybrid with `2024 / 2025` year/model notation: `https://media.toyota.com.br/dbff4f05-d6ed-47e8-bb7d-073369a7cff7.pdf`.
- Toyota do Brasil's June 2025 public-price sheet publishes Corolla Cross XRX Hybrid with `2025 / 2026` notation: `https://media.toyota.com.br/197da502-db1f-45c6-9608-16fdd530929a.pdf`.

These sources establish that manufacture year and model year are separate concepts and that the same named configuration can appear across adjacent model years. They do **not** by themselves decide whether manufacture year belongs in Podium 7's canonical configuration identity.

## Challenge design

The six cases are balanced:

```text
2 MATCH
2 NO_MATCH
2 REVIEW
```

The `REVIEW` cases are intentionally conservative. They identify situations where the available evidence does not justify a deterministic merge or deterministic rejection without an explicit product rule.

## Current characterization

The current resolver produces:

```text
4 / 6 exact labels
0 false merges
0 missed duplicates
2 ambiguous overcommits
0 REVIEW predictions
```

The two decision-relevant mismatches are:

1. **Same model year and configuration, different manufacture years** — expected challenge disposition `REVIEW`; current resolver returns `NO_MATCH` because manufacture-year ranges do not overlap.
2. **Explicit singleton model year versus missing model year while the same named configuration exists in adjacent model years** — expected challenge disposition `REVIEW`; current resolver returns `MATCH` because the remaining generation/powertrain/trim evidence is equal.

The controls confirm that explicit non-overlapping model-year singleton ranges remain `NO_MATCH`, while overlapping/missing manufacture-year evidence can still match when there is no direct contradiction.

## Decision boundary

No resolver change is made in this work unit.

A future product decision must choose and document the intended semantics before code changes. The narrow options exposed by this benchmark are:

- keep manufacture year identity-defining, accepting deterministic `NO_MATCH` on non-overlap;
- treat manufacture-year-only conflict as insufficient and route it to `REVIEW` (or remove manufacture year from configuration identity entirely);
- require explicit model-year evidence for automatic `MATCH` when the same configuration spans multiple model years, routing missing model year to `REVIEW`.

Any selected rule must be implemented with this challenge slice converted from characterization into a regression gate, while preserving the priority `false merges > missed duplicates > review volume`.
