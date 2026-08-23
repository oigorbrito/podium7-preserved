# Contributing to Podium 7

Podium 7 uses an evidence-first development process. Changes should preserve conservative semantics, reproducibility, and explicit provenance.

## Before changing code

1. Read `AGENTS.md` and `docs/DEVELOPMENT-WORKFLOW.md`.
2. Check `docs/CURRENT-WORK.md` and `docs/TECH-DEBT.md` to avoid duplicating active work.
3. For non-trivial infrastructure, follow `docs/ADR-0001-MARKET-FIRST-INFRASTRUCTURE.md` before building a new capability.

## Change expectations

- Keep changes bounded to one coherent work unit.
- Add or update tests for behavior changes.
- Preserve source-native evidence and do not silently strengthen semantic claims.
- Keep permanent CI deterministic and independent of the public internet.
- Do not commit secrets, credentials, local environment files, or generated validation artifacts.

## Validation

Run the repository harness, health check, and the relevant test suite before opening a pull request. The canonical GitHub workflow is `.github/workflows/sequential-tests.yml`.

## Pull requests

Use a focused branch, describe what changed and what is intentionally out of scope, and keep evidence in repository paths or CI artifacts rather than chat transcripts. Merge only after required validation is green and the branch is current with `main`.
