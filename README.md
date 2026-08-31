# Podium 7

Podium 7 is a private, evidence-driven automotive knowledge system for acquisition, integration, reconciliation, review, and export.

## Status

- private/proprietary;
- local operation and operator installation are validated;
- hosted certification remains externally pending.

## Install

```bash
python -m venv --system-site-packages .venv
.venv\Scripts\python -m ensurepip --upgrade
.venv\Scripts\python -m pip install --no-build-isolation .
.venv\Scripts\python -m podium7 health
python scripts/run_operational_readiness.py --output docs/generated/operational-readiness.json
```

## Start here

- [Project charter](docs/PROJECT-CHARTER.md)
- [Current state](docs/PROJECT-STATE.md)
- [Operations](docs/OPERATIONS.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Requirements](docs/REQUIREMENTS.md)
- [Quality gates](docs/QUALITY-GATES.md)
- [Closeout plan](docs/CLOSEOUT-PLAN.md)
- [Documentation map](docs/INDEX.md)

## Validation and workflow

The canonical development workflow, validation commands, Git/PR/CI policy, autonomy boundaries, definition of done, and stopping rules live in [`docs/DEVELOPMENT-WORKFLOW.md`](docs/DEVELOPMENT-WORKFLOW.md).

For development or agent work, start with [`AGENTS.md`](AGENTS.md).

## Repository policies

- [`CONTRIBUTING.md`](CONTRIBUTING.md)
- [`SECURITY.md`](SECURITY.md)
- [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md)
