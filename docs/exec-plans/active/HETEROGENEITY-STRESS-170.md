# Heterogeneity stress benchmark — issue #170

Status: benchmark contract and controlled stress fixtures prepared; comparative execution pending

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

## Benchmark-contract utility disposition

`HETEROGENEITY_STRESS_BENCHMARK_UTILITY = INTEGRATE_AFTER_REPOSITORY_VALIDATION`

The contract is complementary to existing identity-quality metrics. Existing metrics describe aggregate resolver quality; this block holds case IDs and gold labels constant and measures the delta caused by controlled heterogeneity. That makes naming/schema/representation/unit/granularity/semantic robustness observable without inventing a second safety metric family.

The adapter now validates mapped catalog metrics at its public boundary, including non-finite rates, out-of-range rates and malformed count types. Clean and heterogeneous slices must preserve the same case IDs and expected labels so dataset composition cannot masquerade as a heterogeneity effect.

## Candidate-comparison disposition

`HETEROGENEITY_MITIGATION_COMPARISON = PENDING_EXECUTION`

Current fixtures deliberately exercise existing behavior, including representation variation and a deliberately wrong regulatory→retail projection used as a safety tripwire. They do not propose that projection or any normalization rule.

No normalization, schema mapping, blocker or matcher is declared better yet. A candidate may be proposed only after paired-slice measurements show material robustness improvement without increasing false merges or ambiguous overcommit; replacement remains explicit-owner-consent gated.

## Safety

REVIEW/abstention remains acceptable. Regulatory variant semantics may not be promoted to retail trim by convenience. Manufacture/model year and all frozen source/evidence boundaries remain unchanged.

## Validation

Repository harness, focused tests, sequential suite, project facts and real CI remain required before integration. #112 is an independent hosted-runner blocker.
