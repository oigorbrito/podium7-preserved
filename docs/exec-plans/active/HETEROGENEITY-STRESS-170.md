# Heterogeneity stress benchmark — issue #170

Status: benchmark contract integrated; current-resolver baseline measured; mitigation comparison pending

## Goal

Measure degradation under structural, nomenclature, representation, unit, granularity and semantic heterogeneity without redefining Podium's safety metrics.

## Baseline

Podium already measures auto-match precision/recall, false merges, missed matches, ambiguous overcommit and review rate. The heterogeneity contract adds controlled clean-versus-heterogeneous slicing with explicit deltas while preserving those existing safety metrics.

The current-resolver baseline is now executable and measured on the controlled fixtures already retained in `tests/test_catalog_heterogeneity_current_resolver.py`:

- representation variation (`transmission="M-6"` → `"M6"`) on an otherwise paired Mustang identity causes `recallDelta=-1.0` and `missedMatchDelta=+1.0`, with `falseMergeDelta=0.0`; this is a robustness loss but not a safety overcommit;
- a deliberately invalid regulatory type/variant/version → retail-trim projection causes `ambiguousOvercommitDelta=+1.0` and is correctly flagged as `safetyRegression=true`.

These are bounded controlled-fixture measurements. They are not production-wide rates, and they do not establish frequency or prevalence of either heterogeneity pattern in the operational corpus.

## Work

1. Freeze a reusable delta evaluator over existing Podium metrics. — complete.
2. Flag any increase in false merges or ambiguous overcommit as a safety regression. — complete.
3. Construct controlled automotive slices, including regulatory type/variant/version versus retail trim, without changing source semantics. — complete.
4. Evaluate current Podium behavior on clean and heterogeneous slices. — complete for the retained controlled baseline fixtures.
5. Evaluate candidate normalization/schema-mapping/blocking/matching approaches only after a concrete candidate is defined. — pending.
6. Record `CURRENT_BETTER`, `NEW_BETTER`, `COMPLEMENTARY`, or `NO_MATERIAL_GAIN` after candidate comparison; material replacement requires explicit owner consent. — pending.

## Benchmark-contract utility disposition

`HETEROGENEITY_STRESS_BENCHMARK_UTILITY = INTEGRATED_BASELINE_MEASURED`

The contract is complementary to existing identity-quality metrics. Existing metrics describe aggregate resolver quality; this block holds case IDs and gold labels constant and measures the delta caused by controlled heterogeneity. That makes naming/schema/representation/unit/granularity/semantic robustness observable without inventing a second safety metric family.

The adapter validates mapped catalog metrics at its public boundary, including non-finite rates, out-of-range rates and malformed count types. Clean and heterogeneous slices must preserve the same case IDs and expected labels so dataset composition cannot masquerade as a heterogeneity effect.

## Candidate-comparison disposition

`HETEROGENEITY_MITIGATION_COMPARISON = PENDING_CANDIDATE`

The baseline demonstrates two different failure classes that future candidates must not conflate:

- representation robustness may improve recall, but a candidate must still preserve false-merge and ambiguous-overcommit gates;
- semantic projection from regulatory identifiers into retail trim is a safety boundary, not a normalization opportunity.

No normalization, schema mapping, blocker or matcher is currently defined as a production candidate. The existing deliberately wrong regulatory→retail projection remains only a safety tripwire and must not be treated as a proposal.

A future candidate comparison is valid only when a concrete candidate is specified, the clean/gold cases remain fixed, paired-slice measurements are reproducible, and any apparent robustness gain does not increase false merges or ambiguous overcommit. Material replacement remains explicit-owner-consent gated.

## Safety

REVIEW/abstention remains acceptable. Regulatory variant semantics may not be promoted to retail trim by convenience. Manufacture/model year and all frozen source/evidence boundaries remain unchanged.

## Validation

The baseline behavior is already covered by focused repository tests. This documentation reconciliation still requires fresh repository-hosted CI on the exact merge-candidate head before integration. Historical runs are not substituted for the final head.
