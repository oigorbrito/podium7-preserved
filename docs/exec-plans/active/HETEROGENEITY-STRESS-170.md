# Heterogeneity stress benchmark — issue #170

Status: all specified controlled baseline slices measured; bounded representation candidate integrated; disposition `COMPLEMENTARY`; no production normalizer authorized

## Goal

Measure degradation under structural, nomenclature, representation, unit, granularity and semantic heterogeneity without redefining Podium's safety metrics.

## Baseline

Podium already measures auto-match precision/recall, false merges, missed matches, ambiguous overcommit and review rate. The heterogeneity contract adds controlled clean-versus-heterogeneous slicing with explicit deltas while preserving those existing safety metrics.

The current-resolver baseline is executable and measured on controlled fixtures retained in `tests/test_catalog_heterogeneity_current_resolver.py`. The clean and heterogeneous variants preserve the same case IDs and expected labels.

These are bounded controlled-fixture measurements. They are not production-wide rates and do not establish frequency or prevalence of any heterogeneity pattern in the operational corpus.

## Work

1. Freeze a reusable delta evaluator over existing Podium metrics. — complete.
2. Flag any increase in false merges or ambiguous overcommit as a safety regression. — complete.
3. Construct controlled automotive slices, including regulatory type/variant/version versus retail trim, without changing source semantics. — complete for all slices specified in #170.
4. Evaluate current Podium behavior on clean and heterogeneous slices. — complete for all retained controlled baseline slices.
5. Evaluate candidate normalization/schema-mapping/blocking/matching approaches only after a concrete candidate is defined. — one bounded transmission-representation candidate measured and integrated.
6. Record `CURRENT_BETTER`, `NEW_BETTER`, `COMPLEMENTARY`, or `NO_MATERIAL_GAIN` only at the scope actually measured; material replacement requires explicit owner consent. — `COMPLEMENTARY` at the bounded benchmark scope; no production adoption.

## Benchmark-contract utility disposition

`HETEROGENEITY_STRESS_BENCHMARK_UTILITY = INTEGRATED_BASELINE_MEASURED`

The contract is complementary to existing identity-quality metrics. Existing metrics describe aggregate resolver quality; this block holds case IDs and gold labels constant and measures the delta caused by controlled heterogeneity. That makes naming/schema/representation/unit/granularity/semantic robustness observable without inventing a second safety metric family.

The adapter validates mapped catalog metrics at its public boundary, including non-finite rates, out-of-range rates and malformed count types. Clean and heterogeneous slices must preserve the same case IDs and expected labels so dataset composition cannot masquerade as a heterogeneity effect.

## Complete controlled slice matrix

Fresh CI on PR #220 head `1f11eb626850c21d401e87011af985e7615f1e13` executes all seven categories specified by #170. For one-case expected-MATCH slices that produce no automatic MATCH, `matchPrecision` and therefore `precisionDelta` are undefined (`null`) by the existing benchmark contract rather than coerced to zero.

- **nomenclature** — `CX-5` versus `CX5`: `recallDelta=-1.0`, `missedMatchDelta=+1.0`, `reviewRateDelta=0.0`, `falseMergeDelta=0.0`, `ambiguousOvercommitDelta=0.0`, `safetyRegression=false`.
- **structural/schema incompleteness** — one side lacks body style while generation/powertrain and remaining trim evidence agree: `recallDelta=-1.0`, `missedMatchDelta=0.0`, `reviewRateDelta=+1.0`, `falseMergeDelta=0.0`, `ambiguousOvercommitDelta=0.0`, `safetyRegression=false`. The resolver abstains to `REVIEW`; REVIEW is intentionally distinct from a missed `NO_MATCH`.
- **representation/format** — transmission `M-6` versus `M6`: `recallDelta=-1.0`, `missedMatchDelta=+1.0`, `reviewRateDelta=0.0`, `falseMergeDelta=0.0`, `safetyRegression=false` on the current resolver.
- **unit representation** — equivalent controlled identity with power output represented as `150 kW` versus `201 hp`: `recallDelta=-1.0`, `missedMatchDelta=+1.0`, `reviewRateDelta=0.0`, `falseMergeDelta=0.0`, `ambiguousOvercommitDelta=0.0`, `safetyRegression=false`. The fixture measures absence of unit-conversion identity inference; it does not authorize or assert a conversion rule.
- **granularity mismatch** — `RAV4 Prime` versus broader `RAV4`: `recallDelta=-1.0`, `missedMatchDelta=0.0`, `reviewRateDelta=+1.0`, `falseMergeDelta=0.0`, `ambiguousOvercommitDelta=0.0`, `safetyRegression=false`. Partial model overlap abstains to REVIEW.
- **semantic mismatch** — deliberately invalid regulatory type/variant/version → retail-trim projection: `ambiguousOvercommitDelta=+1.0`, `safetyRegression=true`. This is a safety tripwire, not a normalization target.
- **combined heterogeneity** — representation change plus missing structural trim evidence: `recallDelta=-1.0`, `missedMatchDelta=+1.0`, `reviewRateDelta=0.0`, `falseMergeDelta=0.0`, `ambiguousOvercommitDelta=0.0`, `safetyRegression=false` for the retained controlled fixture.

The matrix demonstrates two distinct conservative failure modes: hard representational contradictions can become `NO_MATCH`, while incomplete/partial evidence can become `REVIEW`. Neither is evidence to weaken resolver safety semantics.

## Bounded transmission-representation candidate

The first concrete mitigation probe is deliberately test-only and field-scoped. It normalizes only transmission strings matching the narrow `letters-digits` form by removing the hyphen, for example `M-6` → `M6` and `DCT-7` → `DCT7`. It does not touch variant, regulatory identifiers, year semantics, powertrain, make/model, aliases, source semantics or production resolver code.

The controlled evidence is:

- transmission representation slice after candidate transform: `recallDelta=0.0`, `missedMatchDelta=0.0`, `falseMergeDelta=0.0`, `safetyRegression=false`;
- deliberately invalid regulatory type/variant/version → retail-trim slice remains `ambiguousOvercommitDelta=+1.0` and `safetyRegression=true`, proving the candidate does not normalize away the semantic safety tripwire.

The candidate syntax is additionally anchored to retained source-backed transmission values from `benchmarks/inmetro_pbev_pdf_extraction_v1.json`: `A-1` and `M-5` match the narrow transform and `N.A.` is intentionally left unchanged. This broadens syntax evidence only; it does not create additional identity-resolution outcome cases or establish production prevalence.

`HETEROGENEITY_TRANSMISSION_REPRESENTATION_CANDIDATE = COMPLEMENTARY`

This means only that the narrow transform closes the one controlled `M-6`/`M6` robustness gap without masking the retained semantic tripwire, while its lexical scope also covers two retained source-backed hyphen codes without rewriting the non-code value `N.A.`. It is not evidence of production prevalence, broad normalization safety, or readiness for product adoption.

## Candidate-comparison disposition

`HETEROGENEITY_MITIGATION_COMPARISON = COMPLEMENTARY`

The complete controlled matrix shows that heterogeneity failures are not one uniform normalization problem. The test-only transmission transform repairs the measured transmission-representation slice, but does not address nomenclature, unit, granularity or structural incompleteness and must not touch the semantic safety tripwire. Therefore it is complementary evidence, not a replacement for the current conservative resolver.

No production normalizer is adopted. A future production proposal would be new work and must be triggered by broader retained/source-backed paired identity evidence showing a measured operational need, then demonstrate no increase in false merges or ambiguous overcommit and receive explicit owner consent.

## Safety

REVIEW/abstention remains acceptable. Regulatory variant semantics may not be promoted to retail trim by convenience. Manufacture/model year and all frozen source/evidence boundaries remain unchanged. The candidate transformation remains test-only; integration of benchmark probes does not change production resolver behavior.

## Validation

The original candidate behavior is covered by `tests/test_catalog_heterogeneity_transmission_candidate.py`; the complete controlled slice matrix is covered by `tests/test_catalog_heterogeneity_current_resolver.py`.

- Original measured candidate head `c87c6ccf31b5202bc11cd99667dec30131246ea2`: CI run `33258792014` passed in both `tests` and `minimum-python`.
- Final source-backed syntax-expansion head `3d6917892c6cb25e119ce8039664f04af1423b10`: CI run `33259480461` passed in both jobs and was integrated through PR #213.
- Complete slice-matrix head before this documentation commit: `1f11eb626850c21d401e87011af985e7615f1e13`; CI run `33265950417` passed all isolated tests in both jobs after correcting the benchmark expectation that REVIEW is not counted as `missedMatch`.

These measurements authorize the benchmark disposition only. They do not authorize a production normalizer, establish prevalence, or convert controlled fixtures into market-coverage evidence.
