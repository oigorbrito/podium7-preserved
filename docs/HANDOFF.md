# Podium 7 handoff

Last refreshed: 2026-08-25

This file is the compact resume point for a new chat, Codex session, or agent handoff. It does not replace canonical product, architecture, or workflow documents.

## Resume protocol

1. Read root `AGENTS.md`, then this file.
2. Read `docs/INDEX.md`, `docs/CURRENT-STATE.md`, `docs/CURRENT-WORK.md`, and `docs/DEVELOPMENT-WORKFLOW.md`.
3. Refresh live GitHub state before acting: current `main`, open PRs, mergeability, CI, issues, and active execution plans. Live repository state always outranks this snapshot.
4. Continue routine reversible work autonomously. If an external dependency blocks one block, record it once and move to the next independent repository-scoped block.
5. Keep durable policy in its canonical document; keep this file compact.

## Stable constraints

- Repository is private/proprietary; public/package release remains intentionally blocked until a later explicit owner licensing decision.
- Ambiguous catalog identity remains fail-closed as `REVIEW`; resolver safety must not be weakened to reduce review volume.
- Manufacture year and model year remain distinct under the selected Senatran-aligned semantics.
- Independent explicit structural contradictions may outrank lexical partial-label overlap; partial overlap remains `REVIEW` without an independent contradiction.
- Before non-trivial infrastructure experimentation or construction, follow ADR-0001 and evaluate mature market alternatives first.
- Repository CI on the merge-candidate head is the official integration validation.

## Remote state at refresh

- `main` is `b12049d6d78eb0793ee6a41fda8befc9e945237f` after PR #116.
- PR #117 is open with a test-only fix for Operational Readiness command matching discovered by agent-local validation.
- Agent-local evidence for the #117 delta is green: 5/5 focused readiness/MVP-gate tests pass and `py_compile` passes.
- Issue #112 (`Restore GitHub Actions hosted-runner execution`) remains open and is the external blocker.
- The #117 Actions run `32867616895` failed before any job step was created; `tests` and `minimum-python` have `steps=null` and no logs. Treat this as an external account/repository execution blocker, not observable code-test failure.
- Do not add runner or infrastructure workarounds merely to bypass #112; ADR-0001 remains in force.
- The formal private-MVP exit gate remains `PENDING` until a normal repository workflow executes real steps and is green.

## Resume order

1. Refresh live `main`, PRs, issues, CI, and repository-declared work.
2. If #112 remains open, check for a material account/Actions condition change before re-running CI; do not repeatedly rerun unchanged blocked jobs.
3. When Actions execution is restored, require the current #117 merge-candidate head to execute real steps/logs and pass.
4. Integrate #117 only after executable green repository CI.
5. Run Operational Readiness V1 and evaluate MVP Exit Gate V1 with independently verified green CI evidence.
6. Close #112 and refresh durable state when the gate can reach `PASS`.
7. Continue any independent repository-scoped work that appears; do not stop merely because a merge occurred.
8. If no further work is declared, stop rather than inventing scope.

## Operating style

Work in large sequential blocks and report brief PASS / FAIL / PENDENTE summaries. Store detailed evidence and durable context in the repository rather than chat.
