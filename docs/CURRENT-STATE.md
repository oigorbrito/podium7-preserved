# Current state

Last verified: 2026-08-29

Podium 7 is an evidence-driven automotive knowledge integration system with a working Catalog Identity V2 path: evidence-backed ingestion, conservative identity resolution, canonical persistence/redirects, consumer reads, regression benchmarks, durable review, batch ingestion, bounded external-source acquisition, provenance controls, quantitative-enrichment contracts, and production-oriented validation gates.

## Stable facts

- Default branch: `main`.
- Repository: `gestbrito/podium7`; GitHub visibility is private.
- Primary implementation language: Python.
- Catalog identity evolution is additive over the established evidence/persistence model.
- Ambiguous identity decisions route to durable `REVIEW`; false merges are treated as more harmful than missed duplicates.
- Independent explicit structural contradictions take precedence over lexical partial-label overlap; partial-label ambiguity remains `REVIEW` when no independent contradiction establishes `NO_MATCH`.
- Manufacture year and model year remain separate catalog dimensions, aligned with Senatran/RENAVAM field semantics. Explicit non-overlap in either dimension is a contradiction; incomplete model-year evidence routes an otherwise structural auto-match to `REVIEW` unless stronger identity evidence establishes the match.
- The historical scientific corpus and decision-relevant benchmark evidence have been reconstructed sufficiently for current engineering decisions; unrecoverable old software-candidate execution details are archived and are not a current development blocker.
- Software status is `PRIVATE_PROPRIETARY`: no public license is granted and package/public release remains intentionally blocked until a later explicit owner decision. Development, testing and private operation are not blocked.
- Hosted GitHub Actions execution is restored; normal repository CI with real steps/logs is the official merge validation gate.

## Current readiness boundary

The private technical MVP is complete. Post-MVP functionality is undergoing the repository-wide functional audit tracked by #236 before any `100% functional post-MVP` claim.

Remaining open evidence/scientific gates are #214, #168, and #232. They concern reproducible historical PDF bytes and evidence-bound extraction/quantitative semantic benchmarking. They must remain fail-closed and are not equivalent to a runtime code failure.

## Volatile facts

Do not maintain test counts, Python/runtime versions, Git SHA, benchmark counters, scientific-reference counts, or release-readiness booleans here. Derive them with:

```bash
python scripts/project_facts.py
```

CI also publishes the derived facts as an artifact.

## Navigation

- Resume context: [`HANDOFF.md`](HANDOFF.md)
- Active mission: [`CURRENT-WORK.md`](CURRENT-WORK.md)
- Operating workflow: [`DEVELOPMENT-WORKFLOW.md`](DEVELOPMENT-WORKFLOW.md)
- Product invariants: [`INVARIANTS.md`](INVARIANTS.md)
- Documentation map: [`INDEX.md`](INDEX.md)
