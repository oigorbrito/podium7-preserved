# Podium 7 Operations

Status: current operational authority

## Prerequisites

- Python 3.11 or newer;
- a private checkout of this repository;
- a writable local environment for the operator database and generated artifacts.
- local access to `setuptools` in the install environment, or a virtual
  environment created with `--system-site-packages` for offline installation.

## Install

Follow `docs/OPERATOR-INSTALLATION-V1.md` for the validated private install path.

## First run

- install the package in a clean virtual environment;
- if the virtual environment is offline, create it with
  `python -m venv --system-site-packages .venv`, bootstrap `pip` with
  `python -m ensurepip --upgrade`, and install with
  `python -m pip install --no-build-isolation .`;
- run `python -m podium7 health`;
- run `python scripts/run_operational_readiness.py --output docs/generated/operational-readiness.json`.

## Core workflow

- acquire evidence;
- normalize and resolve identity conservatively;
- inspect review items when needed;
- persist and export canonical outcomes;
- validate the repository with the documented scripts.

## Review

Use the canonical review operator documented in `docs/CATALOG-REVIEW-OPERATOR-V1.md`. The operator works against an existing SQLite database and fails closed on unsupported or missing schema state.

## Storage

- operator state is SQLite-backed;
- evidence and provenance are durable data, not logs;
- generated operational artifacts belong under `docs/generated/`.

## Backup and restore

- preserve the SQLite database file(s) used by the operator;
- restore means putting those files back before rerunning the operator or health checks;
- there is no repository-owned automated backup service.

## Update

- fetch and fast-forward the repository;
- reinstall the package in the private environment;
- rerun health and readiness checks.

## Troubleshooting

- unsupported Python version: install Python 3.11+;
- health failure: inspect the JSON failure payload;
- package installation failure: rerun the package-installation check;
- review CLI schema failure: point it at an existing database that already contains the supported schemas.

## Recovery

Recovery is documented through the same install, health, and readiness path used for first-run validation. Do not conflate local operator recovery with hosted certification.
