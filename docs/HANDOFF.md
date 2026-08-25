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

- `main` is `5ee601c189f5c47a69e3f757cd1edfd27a5244aa` after PR #110.
- PR #106 (`Exhaust current production reviews V2`) is merged as `630e1e462458ede1790f241d6d7e2841f372370e`; exact `(caseId, side, evidenceId)` review-disposition coverage is integrated.
- PR #107 (`Expose catalog review operator CLI V1`) is merged as `c2653ae7ea15124782b4ab0e35b1e54c8ae30b32`; the private operator preflight/canonical-path safety contract is integrated.
- PR #108 (`Add durable chat and agent handoff`) is merged as `1f8cbbffe67cf4b6f2efc75d4b150eb927806b6f`.
- PR #109 (`Wire market-first infrastructure principle into workflow`) is merged as `a8d302d6cccf424c4bcaf060d23abd5f69974f36`.
- PR #110 (`Preserve Senatran year semantics through operational resolver path`) is merged as `5ee601c189f5c47a69e3f757cd1edfd27a5244aa`.
- There are no open pull requests or issues at this refresh.
- `CURRENT-WORK.md` is `Status: none`; the completed Production Review Exhaustion V2 plan is archived under `docs/exec-plans/completed/`.

## Resume order

1. Refresh live `main`, PRs, issues, CI, and repository-declared work.
2. If no new work is declared, stop rather than inventing scope.
3. If new work appears, follow `DEVELOPMENT-WORKFLOW.md`, preserve the stable constraints above, and use a fresh execution plan when required.

## Operating style

Work in large sequential blocks and report brief PASS / FAIL / PENDENTE summaries. Store detailed evidence and durable context in the repository rather than chat.
