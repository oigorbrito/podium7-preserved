# Current state

Last verified: 2026-08-30

Podium 7 is an evidence-driven automotive knowledge integration system with a working Catalog Identity V2 path: evidence-backed ingestion, conservative identity resolution, canonical persistence/redirects, consumer reads, regression benchmarks, durable review, batch ingestion, bounded external-source acquisition, provenance controls, quantitative-enrichment contracts, and production-oriented validation gates.

## Stable facts

- Default branch: `main`.
- Repository: `gestbrito/podium7`; GitHub visibility is private.
- Primary implementation language: Python.
- Catalog identity evolution is additive over the established evidence/persistence model.
- Ambiguous identity decisions route to durable `REVIEW`; false merges are treated as more harmful than missed duplicates.
- Independent explicit structural contradictions take precedence over lexical partial-label overlap; partial-label ambiguity remains `REVIEW` when no independent contradiction establishes `NO_MATCH`.
- Manufacture year and model year remain separate catalog dimensions, aligned with Senatran/RENAVAM field semantics.
- Software status is `PRIVATE_PROPRIETARY`: no public license is granted and package/public release remains intentionally blocked until a later explicit owner decision. Development, testing and private operation are not blocked.
- Hosted GitHub Actions execution is restored; normal repository CI with real steps/logs is the official merge validation gate. #112 is historical/closed.
- Private operator installation and first-run closeout is validated with a clean `pip install .`, `python -m podium7 health`, repository readiness, and the durable review-operator smoke.

## Current readiness boundary

The private technical MVP is complete. The repository-wide post-MVP functional audit #236 found and corrected the reproducible code/operational defects discovered in its scope. Its durable disposition is:

`POST_MVP_FUNCTIONAL_AUDIT = PENDING_EXTERNAL_EVIDENCE`

Within the audited implementation contracts, no known reproducible code/operational defect remains. This does not authorize a `100% functional post-MVP` or universal-data-completeness claim.

The historical PDF evidence/retrievability gate #214 is completed: the exact retained Inmetro PBEV fixture verifies against SHA-256 `cb8ab26789b75a596f75ebf5f6454f30950d31ff8fff1de99ad56a502679db2b`.

The PDF-to-structured benchmark #168 is completed. On the retained page-1 gold slice, after fixing the transmission extraction defects found by the benchmark, the current pdfplumber path and Camelot lattice each reproduced 21/21 authorized fields with no material measured gain from replacement. The bounded disposition is `NO_MATERIAL_GAIN`; pdfplumber remains selected.

The source-bound quantitative benchmark for #232 is complete and merged. The retained digest-bound PBEV bytes remain available as a repository fixture; #232 is closed.

Operator installation and first-run closeout #267 is complete and integrated by PR #268. The validated private runbook covers clean installation, package installation, health, operational readiness, first-run smoke, persistence, backup/restore boundary, durable review operation, update, troubleshooting, cleanup, and separation of optional integrations.

`PRIVATE_PROJECT_ENGINEERING_CLOSURE = PASS`

`OPERATOR_INSTALLATION_CLOSEOUT = PASS`

The current private engineering scope is complete and validated by the documented gates. Public/package release readiness remains intentionally blocked by private/proprietary policy. Paid, contractual, credentialed, new-region, and new-source integrations remain `OPTIONAL_FUTURE_CAPABILITY` unless a separately approved scope makes them required.

## Operating mode

The project is in `MAINTENANCE / OPTIONAL PRODUCT EVOLUTION`. Do not create work solely to preserve project activity; open new work when a measured defect, maintenance requirement, or approved product expansion exists.

## Volatile facts

Do not maintain test counts, Python/runtime versions, Git SHA, benchmark counters, scientific-reference counts, or release-readiness booleans here. Derive them with:

```bash
python scripts/project_facts.py
```

CI also publishes the derived facts as an artifact.

## Navigation

- Resume context: [`HANDOFF.md`](HANDOFF.md)
- Active mission: [`CURRENT-WORK.md`](CURRENT-WORK.md)
- Operator installation/runbook: [`OPERATOR-INSTALLATION-V1.md`](OPERATOR-INSTALLATION-V1.md)
- Operating workflow: [`DEVELOPMENT-WORKFLOW.md`](DEVELOPMENT-WORKFLOW.md)
- Product invariants: [`INVARIANTS.md`](INVARIANTS.md)
- Documentation map: [`INDEX.md`](INDEX.md)
