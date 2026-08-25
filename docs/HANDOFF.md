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

- `main` is `519ca47a957dd1c8d871802b4ebea5eeb5dfbd00` after PR #115.
- PRs #106–#115 relevant to the current sequence are merged; there are no open pull requests at this refresh.
- PR #115 integrated Operational Readiness V1 and MVP Exit Gate V1.
- Issue #114 is complete at repository scope; its execution plan is archived under `docs/exec-plans/completed/`.
- Issue #112 (`Restore GitHub Actions hosted-runner execution`) remains open and is the only active blocker.
- GitHub-hosted Actions jobs are still failing before any workflow step is created (`steps=null`, no job logs). Treat this as an external account/repository execution blocker, not observable code-test failure. Do not add runner or infrastructure workarounds merely to bypass it; ADR-0001 remains in force.
- The formal private-MVP exit gate remains `PENDING` until a normal repository workflow executes real steps and is green.

## Resume order

1. Refresh live `main`, PRs, issues, CI, and repository-declared work.
2. If #112 remains open, check for a material account/Actions condition change before re-running CI; do not repeatedly rerun unchanged blocked jobs.
3. When Actions execution is restored, require a normal hosted workflow to create real steps/logs and be green.
4. Run Operational Readiness V1 on the intended merge candidate and evaluate MVP Exit Gate V1 with independently verified green CI evidence.
5. Close #112 and refresh durable state when the gate can reach `PASS`.
6. Continue any independent repository-scoped work that appears; do not stop merely because a merge occurred.
7. If no further work is declared, stop rather than inventing scope.

## Operating style

Work in large sequential blocks and report brief PASS / FAIL / PENDENTE summaries. Store detailed evidence and durable context in the repository rather than chat.
