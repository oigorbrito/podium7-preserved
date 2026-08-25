# MVP Exit Gate V1

Status: implementation candidate

This is the formal technical gate for declaring the current private Podium 7 MVP complete. It is deliberately narrower than public/commercial release readiness.

## Required criteria

The repository gate requires a `PASS` Operational Readiness V1 report containing all required checks: runtime health, harness integrity, repository secret hygiene, package installation, catalog identity golden benchmark, derived project facts, and sequential tests.

The derived project facts must also show:

- runtime health ready;
- at least one discovered repository test;
- non-empty catalog identity benchmark coverage.

The overall MVP exit additionally requires independently verified executable green GitHub Actions on the merge candidate. `scripts/check_mvp_exit.py` therefore returns:

- `FAIL` when repository readiness is incomplete or unsafe;
- `PENDING` when repository readiness passes but official CI is not yet green;
- `PASS` only when repository readiness passes and the caller explicitly attests verified green CI with `--ci-green`.

Example:

```bash
python scripts/run_operational_readiness.py --output /tmp/podium7-readiness.json
python scripts/check_mvp_exit.py /tmp/podium7-readiness.json
# after independently verifying executable green merge-candidate CI:
python scripts/check_mvp_exit.py /tmp/podium7-readiness.json --ci-green
```

## Noncriteria

Private MVP exit does not require a public software license, package publication, open-source release, production-scale market coverage, or weakening fail-closed review behavior. The repository remains private/proprietary until a later explicit owner decision.

## Decision rule

When this gate reports `PASS` using a readiness report produced from the intended merge candidate and independently verified green repository CI, Podium 7 may be declared technically out of MVP for private operation. Later scale, commercialization, public distribution, and broader market coverage are post-MVP programs.
