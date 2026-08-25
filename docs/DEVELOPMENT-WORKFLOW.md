# Development workflow

This is the single canonical source for agent execution policy in Podium 7.

## Task shape

Treat implementation prompts as outcome-first GitHub Issues. Resolve details from the repository before asking the user to repeat context. A task should identify an outcome, any task-specific boundary, and an acceptance criterion when one exists.

For non-trivial work, create or update an execution plan under `docs/exec-plans/active/`. Keep `docs/CURRENT-WORK.md` short: current outcome, boundaries, acceptance criteria, and plan pointer only. Move durable lessons into design docs, decisions, or debt rather than accumulating history in current-work.

## Default autonomy

Proceed without repeated approval for routine, reversible, repository-scoped work already implied by the mission, including:

- reading/searching repository files and documentation;
- editing code, tests, docs, scripts, configuration, and CI;
- running local checks/tests and correcting failures;
- creating logical commits and a feature/chore branch when the available Git workflow requires one;
- opening/updating a PR, responding to CI failures, rerunning failed checks, self-reviewing, and merging a validated PR when permissions and repository rules allow it.

Continue through **edit → validate → fix → self-review → commit → PR → CI → fix → merge** until the acceptance criterion is met or a stopping condition below is reached. Do not create artificial checkpoints between these stages.

## Approval boundaries and stopping rules

Stop and surface a blocker only when the next action is external, materially high-risk, destructive/irreversible, legally owned by the user, requires unavailable credentials/permissions, or requires a product choice that cannot be inferred from existing evidence and has materially different consequences.

Examples: choosing a software license; changing secrets or account permissions; destructive production/data operations; logging into an external model service; selecting between incompatible product semantics with no repository evidence.

A test failure, lint failure, merge conflict, review comment, or ordinary implementation uncertainty is **not** a stopping condition: diagnose, correct, and continue.

## Documentation/navigation

`docs/` is the system of record. Start from `docs/INDEX.md` and follow progressive disclosure into the relevant specialized documents. A recurring rule belongs in exactly one canonical document; other documents should link to it rather than restate it.

Update documentation when behavior or a durable decision changes. Do not rewrite historical design records merely to mirror current state. Put active state in `CURRENT-STATE.md`/`CURRENT-WORK.md`, completed execution history in `exec-plans/completed/`, and durable unresolved work in `TECH-DEBT.md`.

## Implementation discipline

- Prefer the smallest architecture that satisfies the current product need.
- Before non-trivial infrastructure experimentation, adoption, adaptation, or construction, follow [`ADR-0001-MARKET-FIRST-INFRASTRUCTURE.md`](ADR-0001-MARKET-FIRST-INFRASTRUCTURE.md); the ADR owns the mature-alternative evaluation and adopt/adapt/build decision record.
- Preserve `docs/INVARIANTS.md` and the specialized contracts for touched components.
- Make logical commits: a coherent behavior or harness change per commit, not line-count-sized commits.
- Do not amend or rewrite unrelated existing history unless explicitly required.
- Before integrating, inspect the full diff against the current base and remove accidental or speculative changes.

## Validation and evidence

When technical opinions conflict, resolve them by evidence strength rather than preference. Prefer, in order: reproducible Podium 7 results that directly test the question; primary/official technical documentation from the relevant technology provider (including OpenAI, Anthropic, and equivalent recognized organizations); established benchmarks and peer-reviewed or otherwise methodologically transparent experimental studies; recognized standards bodies and technical institutions; then engineering judgment. Weight practical experiments and reproducible measurements more heavily than theory-only material when the decision is operational. Thesis/coursework, classroom projects, toy demonstrations, and other theory-first or fictional/synthetic work are not strong operational evidence by themselves; use them only when they contain a reproducible experiment relevant to the decision or when their claims are independently corroborated by stronger primary or experimental sources. If engineering judgment is still required, label it explicitly as `ENGINEERING_CHOICE` rather than presenting it as established fact.

Before repeating an external candidate/source evaluation, reconstruct the existing evidence first. Search repository history, PR/CI artifacts, durable logs/handoffs, and `CANDIDATE-EVALUATION-LEDGER.md`. Do not rerun a historical battery merely because its chat summary is missing. Retest only the smallest decision-critical gap when no recoverable result exists, the result cannot be tied to an identifiable version/environment, the prior test was incomplete for the current decision, or a later change specifically invalidates it. Before any historical retest, inform the user of the exact test, reason, and scope. A single narrowly scoped retest may proceed after notification as routine work; a broader batch, repeated suite, or retest involving many cases requires explicit user approval before execution. Record every new/repeated candidate evaluation durably in the ledger.

For any code or harness change:

1. Run `python scripts/check_harness.py`.
2. Run the focused tests/checks for the changed behavior while iterating.
3. Run `python scripts/run_tests_one_by_one.py` before integration unless the change is documentation-only and the harness check proves no executable behavior changed. CI still runs the repository suite.
4. Use `python scripts/project_facts.py` for volatile facts; never hand-copy test totals, Python version, Git SHA, readiness booleans, benchmark counts, or scientific-reference counts into current-state docs.
5. Treat CI on the PR merge candidate as the final repository execution evidence. Do not claim PASS from reasoning alone.

If a validation command fails because of the change, fix and rerun without asking for confirmation. If infrastructure is flaky, rerun enough to distinguish infrastructure failure from code failure and record the result in the active plan/PR when material.

## Self-review

Before marking work ready:

- compare the branch against its base as one diff;
- verify acceptance criteria and task boundaries;
- check for duplicated policy, stale current-state claims, accidental public-contract changes, missing provenance, and untested behavior;
- verify new docs are reachable from `docs/INDEX.md` or a specialized index;
- verify `CURRENT-WORK.md` and the execution plan reflect the actual state.

## Git / PR / CI / merge

- Synchronize the base before starting when practical; do not repeatedly pull between small edits.
- Work in a coherent branch when branch/PR tooling is available.
- Open one PR for one coherent scope.
- Keep the PR description outcome-first: behavior, boundaries, validation, and any real blocker.
- Let CI exercise the merge candidate. Correct failures on the same branch and continue.
- Merge only after required checks are green and the PR is mergeable; use an expected head SHA when the API supports it.
- After merge, update the execution plan/current state in the same scope when possible; if the final merge commit itself is the evidence, the next task may close the active plan as its first housekeeping action.

## Definition of done

A mission is done when:

- acceptance criteria are implemented;
- relevant docs/source-of-truth artifacts are updated;
- focused validation and repository CI are green (or an external blocker is explicitly identified);
- self-review found no unresolved in-scope defect;
- commits/PR are coherent and merged when permitted;
- `CURRENT-WORK.md` does not contain a growing historical log;
- durable follow-ups are in `TECH-DEBT.md` or a new active plan, not buried in chat.

Final user reporting should be concise: outcome, executed evidence, PR/merge, and only real remaining blockers.
