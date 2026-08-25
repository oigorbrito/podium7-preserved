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
- GitHub Actions remains the preferred repository CI evidence, but while #112 blocks hosted-runner execution, a structured independent-equivalent validation artifact on the exact clean candidate is an accepted execution-evidence source for the private MVP gate.

## Remote state at refresh

- The private technical MVP exit gate reached `PASS` through the independent-equivalent validation path integrated by PR #119.
- Operational Readiness V1 passed on the exact clean merge-candidate checkout used for that validation.
- There are no open pull requests and no active repository implementation mission at this refresh.
- Issue #112 (`Restore GitHub Actions hosted-runner execution`) remains open as infrastructure/operations debt, not as a private-MVP blocker.
- GitHub-hosted Actions jobs are still failing before any workflow step is created (`steps=null`, no job logs). Do not add runner or infrastructure workarounds merely to bypass it; ADR-0001 remains in force.

## Resume order

1. Refresh live `main`, PRs, issues, CI, and repository-declared work.
2. Treat the current private technical MVP as complete unless new evidence invalidates the accepted gate.
3. If #112 remains open, check for a material account/Actions condition change before re-running CI; do not repeatedly rerun unchanged blocked jobs.
4. When Actions execution is restored, require a normal hosted workflow to create real steps/logs and be green, then close #112.
5. Start new repository work only under an explicitly declared post-MVP mission; do not silently expand the completed MVP scope.

## Operating style

Work in large sequential blocks and report brief PASS / FAIL / PENDENTE summaries. Store detailed evidence and durable context in the repository rather than chat.
