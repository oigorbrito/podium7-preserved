# MVP Exit Gate V1

Status: implementation candidate

This is the formal technical gate for declaring the current private Podium 7 MVP complete. It is deliberately narrower than public/commercial release readiness.

## Required criteria

The repository gate requires a `PASS` Operational Readiness V1 report containing all required checks: runtime health, harness integrity, repository secret hygiene, package installation, catalog identity golden benchmark, derived project facts, and sequential tests.

The derived project facts must also show:

- runtime health ready;
- at least one discovered repository test;
- non-empty catalog identity benchmark coverage.

The overall MVP exit additionally requires independently verified executable validation on the exact merge candidate. GitHub Actions remains the preferred repository CI evidence, but while issue #112 prevents GitHub-hosted jobs from creating executable steps/logs, an equivalent independent validation may satisfy the execution-evidence requirement.

Equivalent independent validation must:

- use the exact intended merge-candidate commit;
- run in a clean or disposable environment independent of the working development process;
- install/resolve the repository from that commit rather than relying on a dirty working tree;
- run the repository harness, full sequential test suite, and Operational Readiness V1;
- preserve all fail-closed benchmark and safety criteria;
- record the commit identity and test/readiness result in a reproducible evidence artifact;
- not treat a locally edited or partially executed test run as equivalent evidence.

The repository provides `scripts/run_independent_validation.py` to produce `podium7.independent-validation.v1` evidence. The artifact records the exact Git commit, whether tracked files are clean, the full Operational Readiness result, whether sequential tests passed, and basic runtime environment metadata.

`scripts/check_mvp_exit.py` therefore returns:

- `FAIL` when repository readiness is incomplete or unsafe;
- `PENDING` when repository readiness passes but neither verified GitHub Actions nor valid equivalent independent execution evidence is available;
- `PASS` when repository readiness passes and one accepted execution source is verified.

Examples:

```bash
python scripts/run_operational_readiness.py --output /tmp/podium7-readiness.json
python scripts/check_mvp_exit.py /tmp/podium7-readiness.json

# Preferred path, after independently verifying executable green merge-candidate CI:
python scripts/check_mvp_exit.py /tmp/podium7-readiness.json --ci-green

# Temporary equivalent path while issue #112 blocks GitHub-hosted execution.
# Run from a clean/disposable checkout of the exact candidate:
python scripts/run_independent_validation.py --output /tmp/podium7-independent.json
python scripts/check_mvp_exit.py /tmp/podium7-readiness.json \
  --independent-validation-report /tmp/podium7-independent.json
```

The two evidence paths are mutually exclusive. The independent report is rejected if its commit does not match the checkout running the MVP gate, if tracked files were dirty, if Operational Readiness was not `PASS`, or if the full sequential tests did not pass. `official_ci` remains `PENDING` when this path is used; the gate instead records `execution_validation=PASS` and `validation_source=independent-equivalent`. Issue #112 remains open until GitHub Actions itself executes normally again.

## Noncriteria

Private MVP exit does not require a public software license, package publication, open-source release, production-scale market coverage, or weakening fail-closed review behavior. The repository remains private/proprietary until a later explicit owner decision.

## Decision rule

When this gate reports `PASS` using a readiness report produced from the intended merge candidate and independently verified execution evidence from one of the accepted sources above, Podium 7 may be declared technically out of MVP for private operation. Later scale, commercialization, public distribution, and broader market coverage are post-MVP programs.
