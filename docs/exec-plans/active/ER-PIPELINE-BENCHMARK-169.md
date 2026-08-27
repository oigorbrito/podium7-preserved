# ER pipeline benchmark — issue #169

Status: active

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

## Current block

`podium7/er_pipeline_benchmark.py` and focused regressions implement stage-level measurement only. No blocker, matcher, threshold, resolver rule or identity policy has changed.

## Safety

A candidate cannot be considered better if blocking drops a true pair, false merges increase, ambiguous REVIEW cases are overcommitted, or frozen source/evidence/semantic policies are weakened.

## Validation

Repository harness, focused tests, sequential suite, project facts and real CI remain required before integration. #112 is an independent hosted-runner blocker.
