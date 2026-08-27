# Heterogeneity stress benchmark — issue #170

Status: active

## Goal

Measure degradation under structural, nomenclature, representation, unit, granularity and semantic heterogeneity without redefining Podium's safety metrics.

## Baseline

Podium already measures auto-match precision/recall, false merges, missed matches, ambiguous overcommit and review rate. The missing capability is controlled clean-versus-heterogeneous slicing with explicit deltas.

## Work

1. Freeze a reusable delta evaluator over existing Podium metrics.
2. Flag any increase in false merges or ambiguous overcommit as a safety regression.
3. Construct controlled automotive slices, including regulatory type/variant/version versus retail trim, without changing source semantics.
4. Evaluate current Podium behavior on clean and heterogeneous slices.
5. Evaluate candidate normalization/schema-mapping/blocking/matching approaches only after baseline results exist.
6. Record `CURRENT_BETTER`, `NEW_BETTER`, `COMPLEMENTARY`, or `NO_MATERIAL_GAIN`; material replacement requires explicit owner consent.

## Current block

`podium7/heterogeneity_benchmark.py` computes deltas from the existing Podium metric family and focused regressions cover safety-regression detection. No resolver, normalization or semantic policy changed.

## Safety

REVIEW/abstention remains acceptable. Regulatory variant semantics may not be promoted to retail trim by convenience. Manufacture/model year and all frozen source/evidence boundaries remain unchanged.

## Validation

Repository harness, focused tests, sequential suite, project facts and real CI remain required before integration. #112 is an independent hosted-runner blocker.
