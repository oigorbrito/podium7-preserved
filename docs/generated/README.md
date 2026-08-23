# Generated repository facts

Volatile repository facts are generated, not manually transcribed into current-state documentation.

Run:

```bash
python scripts/project_facts.py
```

By default the command prints JSON. With `--output artifacts/project-facts.json` it writes the same machine-readable report. CI publishes that file together with test execution evidence.

The report derives:

- current Git commit when available;
- Python runtime version;
- runtime health/readiness from `python -m podium7 health`;
- discovered unittest count;
- software release-readiness result/message;
- catalog benchmark dataset/case/label counts;
- scientific-reference count parsed from the canonical scientific foundation.

Generated outputs under `artifacts/` are intentionally not committed. This prevents stale counters from becoming documentation claims.
