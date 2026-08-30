# Podium 7 Operator Installation V1

Status: validated closeout runbook

This is the canonical private operator runbook for a fresh Podium 7 checkout.
It documents only commands that were validated in this repository.

## Supported Python

Podium 7 requires Python `3.11` or newer.

## Installation

Validated install path:

```bash
python -m venv .venv
.venv\Scripts\python -m pip install .
```

The direct install path above was validated in a clean virtual environment.
For a repository-owned install check that also builds sdist and wheel and then
installs the wheel into a fresh venv, run:

```bash
python scripts/check_package_installation.py
```

The repository also declares the optional `pbev` extra for `pdfplumber`-backed
PBEV work. That extra is not required for install, health, or operational
readiness.

## First run

After installation, validate the runtime:

```bash
.venv\Scripts\python -m podium7 health
```

Run the deterministic private-operation preflight:

```bash
python scripts/run_operational_readiness.py --output docs/generated/operational-readiness.json
```

The smallest self-contained functional smoke currently validated in-repo is
the durable review-operator CLI exercised against a temporary SQLite database:

```bash
python -m unittest tests.test_catalog_review_operator_cli_v1.CatalogReviewOperatorCliV1Tests.test_list_and_show_expose_review_candidate_and_evidence_context -v
```

That smoke seeds a temporary database, runs `python -m podium7 review list`,
and runs `python -m podium7 review show` against the same database.

For the operator CLI itself, the canonical commands are documented in
[`CATALOG-REVIEW-OPERATOR-V1.md`](CATALOG-REVIEW-OPERATOR-V1.md).

## Persistence

Durable application state is SQLite-backed.

- `python -m podium7 health` uses an in-memory `EvidenceStore` only to verify
  the runtime and schema wiring.
- Real operator usage requires an existing SQLite database file that already
  contains the Podium evidence, Catalog V2, and catalog-review schemas.
- The review CLI fails closed if the database file is missing, empty, or does
  not contain the supported schema.
- The repository does not create a backup or restore service.

To preserve data, keep the SQLite database file(s) used by the operator.
If you want to preserve the generated readiness artifact, keep
`docs/generated/operational-readiness.json` as well.

## Backup and restore boundary

There is no repository-owned backup/restore command.

- Backup means preserving the SQLite database file(s) and any generated
  artifacts you want to retain.
- Restore means putting those files back in place before starting the
  application or operator CLI again.
- If the database path changes, update the operator command to point to the new
  file.

## Update procedure

To update a private installation:

```bash
git fetch --all --prune
git switch main
git pull --ff-only
.venv\Scripts\python -m pip install .
.venv\Scripts\python -m podium7 health
python scripts/run_operational_readiness.py --output docs/generated/operational-readiness.json
```

If the virtual environment becomes stale or incompatible, recreate it and
repeat the install and validation commands above.

## Troubleshooting

- Python older than 3.11: install a supported interpreter before continuing.
- `health` fails: rerun `python -m podium7 health` and inspect the JSON error.
- Package installation fails: rerun
  `python scripts/check_package_installation.py` and inspect the wheel/build
  stage that failed.
- Operational readiness fails: inspect the failing check in
  `docs/generated/operational-readiness.json`.
- Review CLI says the database is invalid or missing schema: point it at an
  existing SQLite database that already contains the supported Podium review
  schema.
- Optional PBEV work fails because `pdfplumber` is unavailable: install the
  declared `pbev` extra before running PBEV-specific commands.

## Cleanup

To remove only the software:

```bash
deactivate
rmdir /s /q .venv
```

Or, if you want to keep the virtual environment and remove only the package:

```bash
.venv\Scripts\python -m pip uninstall podium7
```

Do not delete the SQLite database file if you intend to keep the preserved
operator data.
