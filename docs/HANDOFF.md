# Podium 7 handoff

Last refreshed: 2026-08-24

This file is the compact resume point for a new chat, Codex session, or agent handoff. It is not a historical log and does not replace the canonical design/workflow documents.

## Resume protocol

1. Read the root `AGENTS.md` and this file before changing the repository.
2. Read `docs/INDEX.md`, `docs/CURRENT-STATE.md`, `docs/CURRENT-WORK.md`, and `docs/DEVELOPMENT-WORKFLOW.md`.
3. Refresh live repository state before acting: current `main`, open PRs, current CI status, and the active execution plan(s). Prefer live GitHub state over stale snapshot details below.
4. Continue the active work autonomously under `DEVELOPMENT-WORKFLOW.md`; do not ask the user to reconstruct prior chat context that is recoverable from the repository.
5. If a block is stopped only by an external dependency such as the current Actions execution failure, record it and continue to the next independent repository-scoped block rather than idling.
6. Update this handoff when a material transition changes what the next chat/session must know. Keep durable policy in its canonical document and completed history in `docs/exec-plans/completed/`.

## Current product/architecture constraints

- Repository: `tihotm/podium7`, private/proprietary; public/package release remains intentionally blocked until an explicit owner licensing decision. Private development/testing/operation may continue.
- Evidence priority is reproducible Podium results, then primary technical documentation, then benchmarks/standards, then engineering judgment.
- Ambiguous catalog identity remains fail-closed as `REVIEW`; never weaken matching merely to reduce review volume.
- Manufacture year and model year remain distinct, aligned with Senatran/RENAVAM semantics.
- Before non-trivial infrastructure experimentation or construction, follow ADR-0001 and evaluate mature market solutions first.
- Public internet must not become a permanent CI gate.

## Current remote state

- PR #105, `Prefer explicit contradictions over partial label overlap`, is merged. The operational catalog resolver now lets an independent explicit structural contradiction win over lexical partial-label overlap while preserving `REVIEW` when no such contradiction exists.
- PR #106, `Exhaust current production reviews V2`, is open at `364ed0b48ea0668ab3eea181fbf5043904000371`. Its current replay/disposition work is case-bound and fail-closed; self-review also reconciled `TECH-DEBT.md` so the historical V3 enrichment result (18 reviews) is not confused with the post-#105 replay (13 reviews). Run `32791671236` failed both lanes before any workflow step was created.
- PR #107, `Expose catalog review operator CLI V1`, is open at `c1c928252ee39ab071bd1b37a756fa7b0e74f023`. Self-review hardened the operator to validate an existing Podium catalog-review database in read-only mode before normal opening; empty files, non-Podium SQLite files, and catalog databases without the durable review schema fail closed without schema initialization or mutation.
- PR #108, `Add durable chat and agent handoff`, is open. It owns this handoff, routes root `AGENTS.md` through it, and refreshes current-state documentation. Current branch state also records the post-#105 resolver precedence as a stable fact.
- PR #109, `Wire market-first infrastructure principle into workflow`, is open at `a0c793b367d048dd34f73d0bfffdda230daf1d8a`. It does not duplicate ADR-0001; it links the accepted ADR from `ARCHITECTURE-PRINCIPLES.md` and `DEVELOPMENT-WORKFLOW.md`. Run `32791804203` failed both lanes pre-step.
- PR #110, `Preserve Senatran year semantics through operational resolver path`, is open at `229aacf50d6a0355edabe755d5b12b6a50d1d093`. Its test-only hardening now requires the operational resolver path to preserve the six selected Senatran/model-year cases, the V2.1 external-identifier decisions, and all curated labels across the four source-backed identity benchmark slices. Run `32792141619` failed both lanes pre-step.
- The observed CI blocker is external to the tested code paths: repeated GitHub Actions runs on independent documentation and code/test branches fail before any workflow step is created (`steps=null`, no job log blob). Treat this as an infrastructure/account execution blocker, not as code PASS/FAIL. Repository APIs alone have not established whether the account-side cause is runner entitlement, included minutes, billing, or a spending limit.

## Recommended resume order

1. Refresh live PR/head/CI state. Do not assume the snapshot above is current.
2. If PR #108 is still open when Actions can execute again, validate and integrate that documentation-only housekeeping first so future sessions receive the durable handoff from `main`.
3. Validate/integrate independent hardening PRs #109 and #110 when executable CI is green; reconcile with current `main` first if needed.
4. Rerun the merge-candidate CI for PR #106. If green, self-review/concurrency-check and integrate it by squash according to the workflow.
5. Rebase/reconcile PR #107 against the resulting `main`, run executable CI, self-review, and integrate only if green.
6. Recompute the remaining production-review state from the repository after those integrations; do not reuse an old chat count as authoritative.
7. Close/archive active execution plans and return `CURRENT-WORK.md` to `Status: none` only after the active work is actually integrated or explicitly stopped.

## Operational style

Work in large sequential blocks and report only brief progress summaries. Keep detailed evidence, fixtures, diagnostics, and durable records in the repository rather than in chat. Continue automatically through routine reversible work; surface only real external/high-risk/product-choice blockers.
