# Podium 7 handoff

Last refreshed: 2026-08-25

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
- Repository CI on the merge-candidate head is the official integration validation; a pre-step Actions failure is a blocker, not a code PASS/FAIL result.

## Current remote state

- `main` is still `920a1152d9969a3b532d320a0ab940035755c1a0` from PR #105, `Prefer explicit contradictions over partial label overlap`. The operational resolver lets an independent explicit structural contradiction win over lexical partial-label overlap while preserving `REVIEW` when no such contradiction exists.
- PR #106, `Exhaust current production reviews V2`, is open/draft at `08f4b81c42e58127f0e7268998a96fcd819a2f2d`. Its current disposition schema is fail-closed by exact `(caseId, side, evidenceId)`, not just case or side. The `evidenceId` includes the source benchmark `datasetVersion`, so evidence-version drift is reported as both a current unassessed item and a stale disposition until explicitly reassessed. Focused regressions cover a missing side, a stale side, and a stale evidence ID. Earlier head `8f776f35722d25e5f419209907068c22f54fc953` had executable green CI in run `32709518982`; latest run `32812276342` failed both lanes before steps (`steps=null`). The active plan is `docs/exec-plans/active/PRODUCTION-REVIEW-EXHAUSTION-V2.md`.
- PR #107, `Expose catalog review operator CLI V1`, is open/draft at `3d48ba0009d3b3b799d0362508fae0b854fb8190`. The canonical `python -m podium7 review list|show|match|create` surface performs an existing-database read-only schema/version preflight, exposes source/canonical candidate context on `show`, and delegates mutations to the established audited domain functions. The legacy `scripts/resolve_catalog_review.py` is now only a compatibility wrapper. Further self-review made the operator reopen the same canonical filesystem path that was validated read-only, rather than validating a resolved target and reopening an alias/symlink pathname. A dedicated regression covers that path binding. Run `32812076383` failed both lanes pre-step.
- PR #108, `Add durable chat and agent handoff`, is open and owns this handoff plus the root `AGENTS.md` resume route and current-state refresh. It should remain compact and prefer live GitHub state over its snapshot.
- PR #109, `Wire market-first infrastructure principle into workflow`, is open/draft at `a0c793b367d048dd34f73d0bfffdda230daf1d8a`. It links accepted ADR-0001 from `ARCHITECTURE-PRINCIPLES.md` and `DEVELOPMENT-WORKFLOW.md` without duplicating the policy. A fresh rerun on 2026-08-25 again failed both lanes before steps.
- PR #110, `Preserve Senatran year semantics through operational resolver path`, is open/draft at `229aacf50d6a0355edabe755d5b12b6a50d1d093`. Its test-only hardening gates the operational structural-precedence wrapper against all four curated identity benchmark slices, the selected six-case Senatran/model-year policy, and V2.1 external-identifier decisions. Its CI also fails pre-step.
- The CI symptom is consistent across independent documentation, test-only, and runtime branches: GitHub Actions jobs complete as failure before any step is created (`steps=null`, no job log blob). Repository APIs do not establish the account-side cause. Do not change runner architecture merely to bypass it.

## Recommended resume order

1. Refresh live `main`, open PR heads, mergeability, and CI. Do not reuse the snapshot above as authoritative.
2. If Actions is still pre-step blocked, record that once and continue independent repository-scoped review/hardening rather than repeatedly rerunning the same failure.
3. When executable Actions returns, validate/integrate PR #108 first if still open so durable handoff/navigation reaches `main`; reconcile its docs with any independently merged doc PRs.
4. Validate/integrate independent hardening PRs #109 and #110 when their merge-candidate CI is green and they are current with `main`.
5. Rerun PR #106 on its final merge candidate. If green, self-review/concurrency-check and squash-merge it.
6. Reconcile PR #107 against the resulting `main`, preserving both its operator doc/index addition and any newer main documentation, then run executable CI and integrate only if green.
7. Recompute the remaining production-review state after integrations; do not carry the bounded 13-review count forward as a future fact without replaying from current repository state.
8. Close/archive active execution plans and return `CURRENT-WORK.md` to `Status: none` only after active work is actually integrated or explicitly stopped.

## Operational style

Work in large sequential blocks and report only brief progress summaries. Keep detailed evidence, fixtures, diagnostics, and durable records in the repository rather than in chat. Continue automatically through routine reversible work; surface only real external/high-risk/product-choice blockers.
