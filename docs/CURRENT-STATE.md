# Current state

Last verified: 2026-08-23

Podium 7 is an evidence-driven automotive knowledge integration system with a working Catalog Identity V2 path: evidence-backed ingestion, conservative identity resolution, canonical persistence/redirects, consumer reads, regression benchmarks, durable review, and batch ingestion.

## Stable facts

- Default branch: `main`.
- Repository: `tihotm/podium7`; GitHub visibility is private.
- Primary implementation language: Python.
- Catalog identity evolution is additive over the established evidence/persistence model.
- Ambiguous identity decisions route to durable `REVIEW`; false merges are treated as more harmful than missed duplicates.
- Manufacture year and model year remain separate catalog dimensions, aligned with Senatran/RENAVAM field semantics. Explicit non-overlap in either dimension is a contradiction; incomplete model-year evidence routes an otherwise structural auto-match to `REVIEW` unless stronger identity evidence establishes the match.
- The historical scientific corpus and decision-relevant benchmark evidence have been reconstructed sufficiently for current engineering decisions; unrecoverable old software-candidate execution details are archived and are not a current development blocker.
- Software status is `PRIVATE_PROPRIETARY`: no public license is granted and package/public release remains intentionally blocked until a later explicit owner decision. Development, testing and private operation are not blocked.

## Volatile facts

Do not maintain test counts, Python/runtime versions, Git SHA, benchmark counters, scientific-reference counts, or release-readiness booleans here. Derive them with:

```bash
python scripts/project_facts.py
```

CI also publishes the derived facts as an artifact.

## Navigation

- Active mission: [`CURRENT-WORK.md`](CURRENT-WORK.md)
- Operating workflow: [`DEVELOPMENT-WORKFLOW.md`](DEVELOPMENT-WORKFLOW.md)
- Product invariants: [`INVARIANTS.md`](INVARIANTS.md)
- Documentation map: [`INDEX.md`](INDEX.md)
