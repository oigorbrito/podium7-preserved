# Podium 7 agent map

Start here, then follow the repository sources of truth. Do not turn this file into a manual.

1. Read [`docs/HANDOFF.md`](docs/HANDOFF.md) first when starting or resuming a chat/session; refresh the live repository state it points to before acting.
2. Read [`docs/INDEX.md`](docs/INDEX.md) for the documentation map.
3. Read [`docs/CURRENT-STATE.md`](docs/CURRENT-STATE.md) and [`docs/CURRENT-WORK.md`](docs/CURRENT-WORK.md) before changing code.
4. Follow [`docs/DEVELOPMENT-WORKFLOW.md`](docs/DEVELOPMENT-WORKFLOW.md) for autonomy, approvals, Git/PR/CI, validation, self-review, done, and stopping rules.
5. Preserve [`docs/INVARIANTS.md`](docs/INVARIANTS.md); read the specialized design/product docs linked from the index for the area you touch.
6. For non-trivial work, use the execution-plan structure under [`docs/exec-plans/`](docs/exec-plans/README.md). Record durable debt in [`docs/TECH-DEBT.md`](docs/TECH-DEBT.md), not in prompts.
7. Derive volatile repository facts with `python scripts/project_facts.py`; do not copy test counts, runtime readiness, benchmark counters, or scientific-reference counts into hand-maintained state docs.
8. Before integration run `python scripts/check_harness.py` and the validation commands required by the development workflow.

The repository documentation is the system of record. If a recurring instruction is missing, fix the canonical document instead of repeating it in a prompt. Keep `docs/HANDOFF.md` as a compact resume point, not a duplicate policy manual.

## Project closure checklist activation

The reusable closure template is `.project/closure/PROJECT-CLOSURE-DOCUMENTATION-TEMPLATE.md`.

Do not instantiate, execute, or populate it merely because it exists. Activate it only when the user explicitly requests project closure, readiness/release closure, a final checklist, a closure audit, or equivalent assessment.

Before using it:

1. Read the template together with the current repository sources of truth above.
2. Classify the template as `VALID_AS_IS`, `NEEDS_ADAPTATION`, or `NOT_APPLICABLE` for the requested scope.
3. Identify concrete Podium 7 facts that justify any checklist adaptation.
4. Present proposed additions/removals/changes explicitly; do not silently rewrite criteria to fit a desired outcome.
5. Instantiate a working project-specific checklist only after scope and applicability are established.
6. Do not run tests, create/close issues, merge PRs, or perform implementation solely because the template exists.

Because this repository is preserved, do not rewrite or normalize historical evidence, old results, or preserved artifacts merely to satisfy a current closure checklist. A closure assessment must be additive and keep historical material bound to its original revision/context.

```text
DOCUMENTED != IMPLEMENTED
IMPLEMENTED != EXECUTED
EXECUTED != ACCEPTED
ISSUE_CLOSED != PROJECT_CLOSED
PR_MERGED != PROJECT_CLOSED
BLOCKED != PASS
NOT_EXECUTED != PASS
HISTORICAL_EVIDENCE != CURRENT_REVALIDATION
```
