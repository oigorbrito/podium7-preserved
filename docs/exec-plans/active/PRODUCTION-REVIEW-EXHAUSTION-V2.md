# Production Review Exhaustion V2

## Outcome

Close the current V3 production review queue conservatively after the partial-label contradiction fix, with every remaining review explicitly dispositioned from source-backed evidence and no resolver weakening.

## Acceptance criteria

- Current enriched V3 replay remains failure-free.
- All 13 current REVIEW items are explicitly dispositioned.
- No current review is left unassessed.
- No stale disposition remains for an exact `(caseId, side, evidenceId)` review item no longer present in the current review queue.
- No resolver-policy change is introduced by this block.
- Repository CI on the PR merge candidate is green before merge.

## Boundaries / non-goals

- No public-release or licensing change.
- No inferred identity field is promoted without source-backed evidence.
- No weakening of REVIEW behavior to reduce review volume.
- No infrastructure substitution or new runner architecture merely to bypass a GitHub-hosted runner failure.

## Sources of truth

- [`../../DEVELOPMENT-WORKFLOW.md`](../../DEVELOPMENT-WORKFLOW.md)
- [`../../INVARIANTS.md`](../../INVARIANTS.md)
- `benchmarks/source_backed_enrichment_v3.json`
- `benchmarks/review_disposition_v2.json`

## Execution decisions

- PR #105 corrected partial model-label overlap masking explicit structural contradictions. The current V3 replay is 21 CREATED / 26 MATCHED / 13 REVIEW / 0 failed.
- The 13 remaining reviews are evidence-bounded human-review items. The Corolla Altis Hybrid MY25/MY26 family remains REVIEW because the Toyota evidence establishes year-specific variants but does not establish identity equivalence to older generic yearless canonicals.
- Self-review first added a case-level exact-coverage guard so obsolete case dispositions could not survive silently after topology changes.
- Further self-review found that case-level coverage was not sufficiently fail-closed because more than one current review item can share a case. The disposition schema was therefore bound to explicit `left`/`right` sides and exact coverage by `(caseId, side)`.
- A later self-review found that case/side alone could still inherit an old disposition if the benchmark dataset changed while retaining the same case ID and side. The disposition schema now also binds each side to the exact operational `evidenceId`, whose value includes the benchmark `datasetVersion`. Coverage is checked by `(caseId, side, evidenceId)`: an evidence-version change is both a current unassessed item and a stale disposition until explicitly reassessed.

## Validation evidence

- Earlier PR #106 head `8f776f35722d25e5f419209907068c22f54fc953` with the 13-review disposition gate received executable green repository CI in run `32709518982`. Its validation artifact reported the full then-current sequential suite PASS.
- Subsequent GitHub Actions runs after the exact-coverage hardening failed before creating any job steps; repeated reruns reproduce `steps=null` with no job log in both `tests` and `minimum-python`.
- Focused regressions now prove fail-closed behavior for a missing side, an obsolete side, and a stale `evidenceId` with the same case/side.
- The workflow file is unchanged and uses standard `ubuntu-latest` GitHub-hosted runners. The current pre-step failure is therefore not observable code-test failure evidence.

## Remaining blocker

GitHub-hosted runner execution for this private repository is currently failing before any workflow step starts. Per the development workflow, this is treated as infrastructure/account execution evidence, not as a code failure. The PR must remain unmerged until the merge-candidate head receives green CI. Repository-side work should not replace the runner architecture merely to bypass this external condition. If the condition persists, the repository owner must inspect GitHub Actions usage/billing and repository Actions policy/settings because those are account-level controls not owned by the codebase.
