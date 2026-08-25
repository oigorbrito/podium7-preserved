# Operational Readiness V1

Status: implementation candidate

Operational Readiness V1 is the deterministic private-operation preflight for Podium 7. It does not claim public release readiness, production-scale completeness, or external-service availability.

## Command

```bash
python scripts/run_operational_readiness.py --output docs/generated/operational-readiness.json
```

The default run executes the current Python interpreter against these repository-owned checks in sequence:

1. `python -m podium7 health`
2. `python scripts/check_harness.py`
3. `python scripts/check_repository_secrets.py`
4. `python scripts/check_package_installation.py`
5. `python scripts/run_catalog_identity_benchmark.py --compact`
6. `python scripts/project_facts.py`
7. `python scripts/run_tests_one_by_one.py`

A readiness report is `PASS` only when every check exits zero. Each command result, exit status, stdout/stderr, and JSON payload where available is retained in the machine-readable report.

## Boundary

This gate is intentionally local and deterministic. It does not perform live acquisition, destructive production mutations, public publishing, licensing changes, or runner substitutions. Live-source behavior remains governed by the existing acquisition characterization and recurring-source policy records.

GitHub Actions remains the official merge-candidate integration evidence. A local Operational Readiness `PASS` is necessary evidence for private MVP exit, but is not sufficient while repository CI cannot execute.
