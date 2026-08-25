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
