# ER pipeline benchmark — issue #169

Status: benchmark contract prepared; comparative execution pending

## Goal

Benchmark filtering/blocking + verification as one pipeline while preserving Podium's conservative identity safety metrics.

## Baseline

Podium already measures final resolver outcomes including match precision/recall, false merges, missed duplicates, review rate and ambiguous overcommit. The missing instrumentation is stage separation: candidate retention versus verifier quality and operational cost.

## Work

1. Freeze a generic pair-level pipeline measurement contract.
2. Report blocking recall separately from verifier and end-to-end metrics.
3. Preserve falseMergeCount and ambiguousOvercommitCount as non-regression gates.
4. Add latency and peak-memory slots without introducing infrastructure dependencies.
5. Adapt the existing automotive golden corpus into one or more blocking/verification candidate experiments.
6. Compare current Podium behavior with candidates inspired by SMBench/MaDI-Bench or targeted research.
7. Record `CURRENT_BETTER`, `NEW_BETTER`, `COMPLEMENTARY`, or `NO_MATERIAL_GAIN`; replacement requires explicit owner consent.

## Benchmark-contract utility disposition

`ER_PIPELINE_BENCHMARK_UTILITY = INTEGRATE_AFTER_REPOSITORY_VALIDATION`

The stage-separated contract closes a real measurement gap: final precision/recall alone cannot tell whether a pipeline lost a true pair during blocking or whether the verifier itself failed. `blockingRecall`, verifier metrics and end-to-end safety metrics therefore answer distinct questions and should remain separate.

`candidateReductionRatio` is reported only when a real full candidate-universe size and retained count are supplied. Reduction measured only inside labeled gold pairs remains explicitly named `labeledPairReductionRatio`; it is not promoted to an SMBench-style full-universe reduction claim.

Cost inputs are optional typed observations and malformed cost/scale containers fail closed.

## Candidate-comparison disposition

`ER_BLOCKER_MATCHER_COMPARISON = PENDING_EXECUTION`

The current `retain-all-current-verifier`, `same-make`, and `same-make-model` blockers are bounded probes used to exercise the measurement contract while holding the current verifier constant. They are not declared production candidates or winners.

A blocker/matcher combination can only be proposed as better if comparative execution shows material gain while preserving blocking recall and without increasing false merges or ambiguous overcommit. Replacement still requires explicit owner consent.

## Safety

A candidate cannot be considered better if blocking drops a true pair, false merges increase, ambiguous REVIEW cases are overcommitted, or frozen source/evidence/semantic policies are weakened.

## Validation

Repository harness, focused tests, sequential suite, project facts and fresh repository-hosted CI on the exact merge-candidate head are required before integration. Issue #112 is resolved; historical workflow evidence is not substituted after a rebuild.
