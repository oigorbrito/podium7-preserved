# Podium 7 handoff

Last refreshed: 2026-08-29

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
- GitHub Actions is the official repository CI validation gate. Hosted-runner execution has been restored; #112 is historical/closed and must not be treated as a current blocker.

## Remote state at refresh

- The private technical MVP is complete.
- The repository-wide post-MVP functional audit #236 completed its code/operational review after fixing its reproducible findings.
- Durable audit disposition: `POST_MVP_FUNCTIONAL_AUDIT = PENDING_EXTERNAL_EVIDENCE`.
- No known reproducible code/operational defect remains within the audited implementation contracts.
- This is not authorization to claim `100% functional post-MVP` or universal automotive-data completeness.
- Remaining external-evidence/scientific blockers are #214 (reproducible bound PDF bytes), #168 (PDF-to-structured extraction benchmark), and #232 (PBEV quantitative semantic benchmark). These remain fail-closed.

## Resume order

1. Refresh live `main`, PRs, issues, CI, and repository-declared work.
2. Advance #214 using ADR-0001 market-first evaluation of mature durable snapshot/storage mechanisms; never substitute mutable upstream bytes for the bound historical digest.
3. Advance #232 independently where evidence can be separately acquired, frozen, reuse-reviewed and digest-bound without weakening source semantics.
4. Run #168 only when the exact source-bound PDF bytes required by its benchmark are reproducibly available; #214 is its direct blocker.
5. Require repository CI on exact final heads before squash merge.

## Operating style

Work in large sequential blocks and report brief PASS / FAIL / PENDENTE summaries. Store detailed evidence and durable context in the repository rather than chat.
