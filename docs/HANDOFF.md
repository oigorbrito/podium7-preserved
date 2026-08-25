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

- `main` is `c2653ae7ea15124782b4ab0e35b1e54c8ae30b32` after PR #107.
- PR #106 (`Exhaust current production reviews V2`) is merged as `630e1e462458ede1790f241d6d7e2841f372370e`. Review dispositions are fail-closed by exact `(caseId, side, evidenceId)`.
- PR #107 (`Expose catalog review operator CLI V1`) is merged as `c2653ae7ea15124782b4ab0e35b1e54c8ae30b32`. The canonical private review operator uses an existing-database read-only preflight, reopens the same resolved path, and the legacy script delegates to it.
- PR #108 (`Add durable chat and agent handoff`) was reconciled with current `main` after becoming 47 commits behind; its branch now preserves current `main` and reapplies only the handoff/current-state delta.
- PR #109 (`Wire market-first infrastructure principle into workflow`) remains open/draft and must be refreshed against current `main` before integration.
- PR #110 (`Preserve Senatran year semantics through operational resolver path`) remains open/draft and must be refreshed against current `main` before integration.
- No active implementation mission remains after #106/#107 integration; `CURRENT-WORK.md` is `Status: none` unless live state says otherwise.

## Resume order

1. Refresh `main` and open PRs.
2. Validate/integrate #108 when conflict-free and executable repository CI is green.
3. Reconcile #109 and #110 against the resulting `main`, preserving current documentation/test changes, then validate and integrate only with green CI.
4. Recompute repository-declared work after those integrations; do not invent new product scope merely to remain busy.

## Operating style

Work in large sequential blocks and report brief PASS / FAIL / PENDENTE summaries. Store detailed evidence and durable context in the repository rather than chat.
