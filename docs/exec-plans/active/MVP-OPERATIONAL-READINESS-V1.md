# MVP Operational Readiness V1

Status: active

Issue: #114

## Outcome

Close the remaining technical path from the current MVP state to a measurable private-operational MVP exit without introducing public-release scope or infrastructure workarounds.

## Blocks

### 1. CI execution recovery

Tracked by #112. Acceptance: a normal GitHub-hosted repository workflow creates actual steps/logs and is green on the merge candidate. Current state: external blocker; continue independent repository work.

### 2. Operational Readiness V1

Implement `scripts/run_operational_readiness.py` with a machine-readable report over runtime health, harness, secret hygiene, package installation, identity benchmark, project facts, and sequential tests. Acceptance: all required local checks are represented and fail closed on any non-zero result.

### 3. MVP Exit Gate V1

Implement `scripts/check_mvp_exit.py` and canonical criteria. Acceptance: repository readiness cannot produce MVP PASS without all required checks and explicit independently verified green CI; public licensing/release is not a private-MVP criterion.

## Boundaries

- Preserve fail-closed identity/review semantics and Senatran year semantics.
- No resolver-policy weakening.
- No public-license or package-release decision.
- No self-hosted runner or infrastructure workaround for #112.
- No destructive production/data operation.

## Validation

For executable changes: focused tests, `python scripts/check_harness.py`, and `python scripts/run_tests_one_by_one.py`; repository CI remains official final evidence. If Actions again fails before any step, record it as the existing external blocker rather than code-test failure.

## Completion

After executable green CI, run Operational Readiness V1 on the merge candidate, evaluate MVP Exit Gate V1 with verified CI evidence, merge the coherent PR, archive this plan, update `CURRENT-WORK.md`, and close #114. If CI remains externally blocked, blocks 2 and 3 may be implementation-complete while block 1 and final MVP declaration remain pending.
