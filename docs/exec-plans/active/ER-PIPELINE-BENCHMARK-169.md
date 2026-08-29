# ER pipeline benchmark — issue #169

Status: bounded retained-corpus blocker comparison executed; no safe material gain

## Goal

Benchmark filtering/blocking + verification as one pipeline while preserving Podium's conservative identity safety metrics.

## Baseline

Podium already measures final resolver outcomes including match precision/recall, false merges, missed duplicates, review rate and ambiguous overcommit. The stage-separated benchmark contract now separates candidate retention from verifier quality and preserves optional operational-cost slots.

## Work

1. Freeze a generic pair-level pipeline measurement contract.
2. Report blocking recall separately from verifier and end-to-end metrics.
3. Preserve falseMergeCount and ambiguousOvercommitCount as non-regression gates.
4. Add latency and peak-memory slots without introducing infrastructure dependencies.
5. Adapt the existing automotive golden corpus into bounded blocking/verification experiments.
6. Execute the already-declared `retain-all-current-verifier`, `same-make`, and `same-make-model` probes on the retained automotive corpora with the current verifier held constant.
7. Record the bounded comparison disposition without promoting a probe to production.

## Benchmark-contract utility disposition

`ER_PIPELINE_BENCHMARK_UTILITY = INTEGRATE_AFTER_REPOSITORY_VALIDATION`

The stage-separated contract closes a real measurement gap: final precision/recall alone cannot tell whether a pipeline lost a true pair during blocking or whether the verifier itself failed. `blockingRecall`, verifier metrics and end-to-end safety metrics therefore answer distinct questions and should remain separate.

`candidateReductionRatio` is reported only when a real full candidate-universe size and retained count are supplied. Reduction measured only inside labeled gold pairs remains explicitly named `labeledPairReductionRatio`; it is not promoted to an SMBench-style full-universe reduction claim.

Cost inputs are optional typed observations and malformed cost/scale containers fail closed.

## Bounded candidate-comparison evidence

The retained-corpus comparison covers:

- `benchmarks/catalog_identity_golden_v1.json`
- `benchmarks/catalog_identity_golden_br_v1.json`
- `benchmarks/catalog_identity_br_adjacent_incomplete_v1.json`
- `benchmarks/catalog_identity_year_semantics_challenge_v1.json`

The current verifier is held constant in every probe.

### `retain-all-current-verifier`

Across all four retained corpora, blocking recall remains `1.0`, false merges remain `0`, ambiguous overcommit remains `0`, and labeled-pair reduction remains `0.0`.

### `same-make`

Across all four retained corpora, the measured safety and end-to-end outcomes are equivalent to retain-all and labeled-pair reduction remains `0.0`. Therefore the retained labeled corpora demonstrate no material candidate-reduction gain for this probe.

### `same-make-model`

The probe reduces labeled pairs on two corpora but violates safety gates:

- global golden v1: `blockingRecall = 0.75`, `missedMatchCount = 1`, `ambiguousOvercommitCount = 2`, `labeledPairReductionRatio = 0.25`;
- Brazil golden v1: `blockingRecall = 0.5`, `missedMatchCount = 2`, `ambiguousOvercommitCount = 0`, `labeledPairReductionRatio = 1/6`;
- adjacent-incomplete and year-semantics challenge slices: no labeled-pair reduction.

The dropped global cases include one curated true match and two curated REVIEW cases. The dropped Brazil matches include the source-backed Corolla Cross presentation/alias case and the T-Cross/T Cross presentation case. Reduction obtained by losing a true pair or overcommitting an ambiguous case is not an efficiency gain under the frozen safety policy.

## Candidate-comparison disposition

`ER_BLOCKER_MATCHER_COMPARISON = CURRENT_BETTER`

For the bounded probes currently defined in this plan, the current retain-all + current-verifier behavior is retained. `same-make` shows `NO_MATERIAL_GAIN` on the retained labeled corpora, while `same-make-model` is ineligible because it fails blocking-recall and ambiguous-overcommit gates.

This does not claim that retain-all is globally optimal, and it does not close the door on a later concrete blocker/matcher candidate. A broader comparison requires a newly defined candidate and the same evidence gates; no candidate is invented merely to keep the evaluation active.

No production blocker/matcher replacement is authorized by this result. Any future material replacement remains explicit owner-consent gated.

## Unmeasured scope

This execution does not supply a full candidate universe, latency observations or peak-memory observations. Therefore:

- `candidateReductionRatio` remains unavailable and must not be inferred from labeled-pair reduction;
- no SMBench-style scale/efficiency claim is made;
- no latency or memory advantage is claimed.

## Safety

A candidate cannot be considered better if blocking drops a true pair, false merges increase, ambiguous REVIEW cases are overcommitted, or frozen source/evidence/semantic policies are weakened.

## Validation

Repository harness, focused tests, sequential suite, project facts and fresh repository-hosted CI on the exact merge-candidate head are required before integration. Issue #112 is resolved; historical workflow evidence is not substituted after a rebuild.
