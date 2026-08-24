# Podium 7 handoff

Last refreshed: 2026-08-24

This file is the compact resume point for a new chat, Codex session, or agent handoff. It is not a historical log and does not replace the canonical design/workflow documents.

## Resume protocol

1. Read the root `AGENTS.md` and this file before changing the repository.
2. Read `docs/INDEX.md`, `docs/CURRENT-STATE.md`, `docs/CURRENT-WORK.md`, and `docs/DEVELOPMENT-WORKFLOW.md`.
3. Refresh live repository state before acting: current `main`, open PRs, current CI status, and the active execution plan(s). Prefer live GitHub state over stale snapshot details below.
4. Continue the active work autonomously under `DEVELOPMENT-WORKFLOW.md`; do not ask the user to reconstruct prior chat context that is recoverable from the repository.
5. Update this handoff when a material transition changes what the next chat/session must know. Keep durable policy in its canonical document and completed history in `docs/exec-plans/completed/`.

## Current product/architecture constraints

- Repository: `tihotm/podium7`, private/proprietary; public/package release remains intentionally blocked until an explicit owner licensing decision. Private development/testing/operation may continue.
- Evidence priority is reproducible Podium results, then primary technical documentation, then benchmarks/standards, then engineering judgment.
- Ambiguous catalog identity remains fail-closed as `REVIEW`; never weaken matching merely to reduce review volume.
- Manufacture year and model year remain distinct, aligned with Senatran/RENAVAM semantics.
- Before non-trivial infrastructure experimentation or construction, follow ADR-0001 and evaluate mature market solutions first.
- Public internet must not become a permanent CI gate.

## Current remote state

- PR #105, `Prefer explicit contradictions over partial label overlap`, is merged. The catalog resolver now lets an independent explicit structural contradiction win over lexical partial-label overlap while preserving `REVIEW` when no such contradiction exists.
- PR #106, `Exhaust current production reviews V2`, is open. Its current replay/disposition work is case-bound and fail-closed; merge is intentionally blocked until repository CI can actually execute green on the merge-candidate head.
- PR #107, `Expose catalog review operator CLI V1`, is open. Self-review hardened the operator to validate an existing Podium catalog-review database in read-only mode before normal opening; empty files, non-Podium SQLite files, and catalog databases without the durable review schema now fail closed without schema initialization or mutation. The current head is `c1c928252ee39ab071bd1b37a756fa7b0e74f023` and remains blocked from merge until executable green repository CI exists.
- The observed CI blocker is external to the tested code path: repeated GitHub Actions runs on independent PR branches fail before any workflow step is created (`steps=null`, no job log blob). The latest PR #107 merge-candidate run observed was `32791354640`, with both `tests` and `minimum-python` failing pre-step. Treat this as an infrastructure/account execution blocker, not as code PASS/FAIL. Repository APIs alone have not established whether the account-side cause is runner entitlement, included minutes, billing, or a spending limit.

## Recommended resume order

1. Re-check the GitHub Actions/account execution blocker using live repository/account evidence.
2. Once Actions can execute steps again, rerun the merge-candidate CI for PR #106. If green, self-review/concurrency-check and integrate it by squash according to the workflow.
3. Rebase/reconcile PR #107 against the resulting `main`, run executable CI, self-review, and integrate only if green.
4. Recompute the remaining production-review state from the repository after those integrations; do not reuse an old chat count as authoritative.
5. Close/archive active execution plans and return `CURRENT-WORK.md` to `Status: none` only after the active work is actually integrated or explicitly stopped.

## Operational style

Work in large sequential blocks and report only brief progress summaries. Keep detailed evidence, fixtures, diagnostics, and durable records in the repository rather than in chat. Continue automatically through routine reversible work; surface only real external/high-risk/product-choice blockers.
