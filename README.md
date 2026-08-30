# Podium 7

Podium 7 is an evidence-driven automotive knowledge acquisition, integration, reconciliation, review, and export system.

## Checkout

```bash
git clone https://github.com/gestbrito/podium7.git
cd podium7
```

The implementation currently uses Python and is designed around inspectable evidence, conservative identity reconciliation, canonical persistence, and repeatable validation.

## Repository navigation

For development or agent work, start with [`AGENTS.md`](AGENTS.md). The repository knowledge base and product/design documentation are indexed at [`docs/INDEX.md`](docs/INDEX.md).

The canonical development workflow, validation commands, Git/PR/CI policy, autonomy boundaries, definition of done, and stopping rules live only in [`docs/DEVELOPMENT-WORKFLOW.md`](docs/DEVELOPMENT-WORKFLOW.md).

Collaboration and security expectations are documented in [`CONTRIBUTING.md`](CONTRIBUTING.md), [`SECURITY.md`](SECURITY.md), and [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).

Volatile repository facts such as current test count, Python runtime, release readiness, benchmark counters, and scientific-reference count are generated with `python scripts/project_facts.py`; they are not maintained manually in this README or current-state documentation.