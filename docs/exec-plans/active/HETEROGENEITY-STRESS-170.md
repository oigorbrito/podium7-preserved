# Heterogeneity stress benchmark — issue #170

Status: benchmark contract integrated; current-resolver baseline measured; one bounded representation candidate integrated; broader mitigation comparison remains open

## Goal

Measure degradation under structural, nomenclature, representation, unit, granularity and semantic heterogeneity without redefining Podium's safety metrics.

## Baseline

Podium already measures auto-match precision/recall, false merges, missed matches, ambiguous overcommit and review rate. The heterogeneity contract adds controlled clean-versus-heterogeneous slicing with explicit deltas while preserving those existing safety metrics.

The current-resolver baseline is executable and measured on the controlled fixtures retained in `tests/test_catalog_heterogeneity_current_resolver.py`:

- representation variation (`transmission="M-6"` → `"M6"`) on an otherwise paired Mustang identity causes `recallDelta=-1.0` and `missedMatchDelta=+1.0`, with `falseMergeDelta=0.0`; this is a robustness loss but not a safety overcommit;
- a deliberately invalid regulatory type/variant/version → retail-trim projection causes `ambiguousOvercommitDelta=+1.0` and is correctly flagged as `safetyRegression=true`.

These are bounded controlled-fixture measurements. They are not production-wide rates, and they do not establish frequency or prevalence of either heterogeneity pattern in the operational corpus.

## Work

1. Freeze a reusable delta evaluator over existing Podium metrics. — complete.
2. Flag any increase in false merges or ambiguous overcommit as a safety regression. — complete.
3. Construct controlled automotive slices, including regulatory type/variant/version versus retail trim, without changing source semantics. — complete.
4. Evaluate current Podium behavior on clean and heterogeneous slices. — complete for the retained controlled baseline fixtures.
5. Evaluate candidate normalization/schema-mapping/blocking/matching approaches only after a concrete candidate is defined. — one bounded transmission-representation candidate measured and integrated; broader candidates remain open.
6. Record `CURRENT_BETTER`, `NEW_BETTER`, `COMPLEMENTARY`, or `NO_MATERIAL_GAIN` only at the scope actually measured; material replacement requires explicit owner consent. — bounded transmission representation disposition recorded below; no global mitigation winner declared.

## Benchmark-contract utility disposition

`HETEROGENEITY_STRESS_BENCHMARK_UTILITY = INTEGRATED_BASELINE_MEASURED`

The contract is complementary to existing identity-quality metrics. Existing metrics describe aggregate resolver quality; this block holds case IDs and gold labels constant and measures the delta caused by controlled heterogeneity. That makes naming/schema/representation/unit/granularity/semantic robustness observable without inventing a second safety metric family.

The adapter validates mapped catalog metrics at its public boundary, including non-finite rates, out-of-range rates and malformed count types. Clean and heterogeneous slices must preserve the same case IDs and expected labels so dataset composition cannot masquerade as a heterogeneity effect.

## Bounded transmission-representation candidate

The first concrete mitigation probe is deliberately test-only and field-scoped. It normalizes only transmission strings matching the narrow `letters-digits` form by removing the hyphen, for example `M-6` → `M6` and `DCT-7` → `DCT7`. It does not touch variant, regulatory identifiers, year semantics, powertrain, make/model, aliases, source semantics or production resolver code.

Fresh repository CI on candidate head `c87c6ccf31b5202bc11cd99667dec30131246ea2` executed the retained comparison successfully in both Python jobs. The controlled evidence is:

- transmission representation slice after candidate transform: `recallDelta=0.0`, `missedMatchDelta=0.0`, `falseMergeDelta=0.0`, `safetyRegression=false`;
- deliberately invalid regulatory type/variant/version → retail-trim slice remains `ambiguousOvercommitDelta=+1.0` and `safetyRegression=true`, proving the candidate does not normalize away the semantic safety tripwire.

The candidate syntax is now additionally anchored to retained source-backed transmission values from `benchmarks/inmetro_pbev_pdf_extraction_v1.json`: `A-1` and `M-5` match the narrow transform and `N.A.` is intentionally left unchanged. This broadens syntax evidence only; it does not create additional identity-resolution outcome cases or establish production prevalence.

`HETEROGENEITY_TRANSMISSION_REPRESENTATION_CANDIDATE = COMPLEMENTARY`

This means only that the narrow transform closes the one controlled `M-6`/`M6` robustness gap without masking the retained semantic tripwire, while its lexical scope also covers two retained source-backed hyphen codes without rewriting the non-code value `N.A.`. It is not evidence of production prevalence, broad normalization safety, or readiness for product adoption.

## Candidate-comparison disposition

`HETEROGENEITY_MITIGATION_COMPARISON = PENDING_BROADER_CANDIDATE_EVIDENCE`

The bounded candidate demonstrates that representation robustness and semantic safety can be tested independently. It does not justify a global normalizer from a one-outcome-case fixture plus syntax checks.

Any production proposal must first be measured on broader retained/source-backed paired identity cases and must show no increase in false merges or ambiguous overcommit. The regulatory→retail projection remains only a safety tripwire and must never be treated as a normalization target.

Material replacement or production normalization remains explicit-owner-consent gated.

## Safety

REVIEW/abstention remains acceptable. Regulatory variant semantics may not be promoted to retail trim by convenience. Manufacture/model year and all frozen source/evidence boundaries remain unchanged. The candidate transformation remains test-only; integration of the benchmark probe does not change production resolver behavior.

## Validation

The candidate behavior is covered by `tests/test_catalog_heterogeneity_transmission_candidate.py`.

- Original measured candidate head `c87c6ccf31b5202bc11cd99667dec30131246ea2`: fresh repository CI run `33258792014` passed in both `tests` and `minimum-python`.
- Final source-backed syntax-expansion head `3d6917892c6cb25e119ce8039664f04af1423b10`: fresh repository CI run `33259480461` passed in both jobs, including secret hygiene, repository harness, project facts, runtime health, package build/install, every test in isolation and validation evidence upload.
- PR #213 was then integrated into `main` by merge commit `908dd4713689da61503f6d6ead6a149b031d4685`.

Those green runs validate the bounded benchmark probe only. They do not authorize a production normalizer, establish prevalence, or complete the broader heterogeneity-mitigation comparison.
