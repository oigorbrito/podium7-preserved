# Podium 7 handoff

Last refreshed: 2026-08-30

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
- Private operator installation has a validated runbook in `docs/OPERATOR-INSTALLATION-V1.md`; the smallest self-contained smoke is the review-operator CLI test that seeds a temporary SQLite database and exercises `review list`/`review show`.

## Current closed baseline

- The private technical MVP is complete.
- #267 operator installation and first-run closeout is complete; PR #268 is merged.
- Clean installation, package installation, health, operational readiness, first-run smoke, persistence, backup/restore boundary, review workflow, update procedure, troubleshooting, and optional-integration separation are validated/documented.
- #232 is completed and closed; its quantitative benchmark is historical evidence, not active work.
- #214 and #168 are completed and retained as bounded evidence/benchmark records.
- The repository-wide post-MVP functional audit #236 remains durably recorded as `POST_MVP_FUNCTIONAL_AUDIT = PENDING_EXTERNAL_EVIDENCE`; this does not represent a known reproducible code/operational defect.
- No known reproducible code/operational defect remains within the audited implementation contracts.
- `PRIVATE_PROJECT_ENGINEERING_CLOSURE = PASS`
- `OPERATOR_INSTALLATION_CLOSEOUT = PASS`
- This is not authorization to claim `100% functional post-MVP` or universal automotive-data completeness.

## Resume order

1. Refresh live `main`, PRs, issues, CI, and repository-declared work.
2. If no required queue exists, remain in `MAINTENANCE / OPTIONAL PRODUCT EVOLUTION`; do not invent work merely to keep the project active.
3. Do not use quantitative equality for identity resolution and do not expose unbenchmarked PBEV quantities to BPT2.
4. Require repository CI on exact final heads before squash merge.
5. Treat paid, contractual, credentialed, or new-region/source capabilities as optional future work unless a separately approved scope makes them required.

## Operating style

Work in large sequential blocks and report brief PASS / FAIL / PENDENTE summaries. Store detailed evidence and durable context in the repository rather than chat.
