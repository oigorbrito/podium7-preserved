# Current work

Status: blocked

Operational Readiness V1 and MVP Exit Gate V1 were integrated by PR #115, and issue #114 is complete.

Two active items remain:

- PR #117, `Fix Operational Readiness test command matching`, contains a test-only correction discovered by agent-local validation. The focused readiness/MVP-gate suite passes locally after the fix, but repository CI for the PR still fails before any workflow step is created.
- Issue #112, `Restore GitHub Actions hosted-runner execution`, is the external blocker preventing official integration validation and the formal private-MVP exit gate from reaching `PASS`.

GitHub-hosted Actions jobs are still failing pre-step (`steps=null`, no job logs). Do not interpret that condition as a code-test failure, and do not change runner architecture or add infrastructure workarounds merely to bypass it; ADR-0001 remains in force.

Owner action for #112 remains limited to GitHub account/repository Actions settings: verify Actions usage/minutes, payment method and budget/spending limits, and repository Actions enablement.

Closure order:

1. Restore normal GitHub-hosted Actions execution so workflows create real job steps/logs.
2. Re-run PR #117 CI on its current merge-candidate head; require executable green checks before integration.
3. Integrate #117, then run Operational Readiness V1 and evaluate MVP Exit Gate V1 with verified CI evidence.
4. Close #112 and refresh durable state when the gate can reach `PASS`.
