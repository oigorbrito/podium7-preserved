# Execution plans

Execution plans are first-class repository artifacts for work that is too large or decision-heavy to live only in a prompt.

## Active

Use `active/` for work currently in progress. Each plan should contain:

- outcome and acceptance criteria;
- boundaries/non-goals;
- relevant source-of-truth links;
- implementation steps at a useful granularity;
- decisions made during execution;
- validation evidence and remaining blockers.

Keep progress concise. Do not duplicate the full development workflow here; link to [`../DEVELOPMENT-WORKFLOW.md`](../DEVELOPMENT-WORKFLOW.md).

## Completed

Move or recreate the final execution record under `completed/` after the work is integrated. Completed plans are historical evidence and should not be used as current state.

## Technical debt

Durable unresolved follow-ups belong in [`../TECH-DEBT.md`](../TECH-DEBT.md), not in completed plans or chat history.
