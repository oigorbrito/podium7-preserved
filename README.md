# Podium 7

Podium 7 is an evidence-driven automotive knowledge acquisition, integration, reconciliation, and export system.

The V1 roadmap now covers scientific foundation, persistence/evidence storage, real structured ingestion, normalization, entity resolution, fusion/conflicts, JSON export, repeatable web extraction, document extraction, validated extraction artifacts, selective review, autonomous enrichment primitives, and multi-source end-to-end acceptance.

Architecture principles and the scientific baseline are recorded under `docs/`.

## Reproducible checkout

```bash
git clone https://github.com/tihotm/podium7.git
cd podium7
```

The current implementation uses the Python standard library only.

## Tests — one at a time

Run every discovered test case in its own Python process:

```bash
python scripts/run_tests_one_by_one.py
```

The GitHub Actions workflow `.github/workflows/sequential-tests.yml` uses the same command so local and CI execution follow the same isolation rule.

For normal unittest discovery without process isolation:

```bash
python -m unittest discover -s tests -v
```
