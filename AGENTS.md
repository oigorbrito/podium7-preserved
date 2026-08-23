# Podium 7 — Agent Execution Map

This file defines the execution style for coding agents working in this repository.

## Default mode: bounded autonomy

- Execute routine, reversible, low-risk repository work without stopping for repeated approval.
- Batch coherent implementation, tests, CI, and integration work into meaningful units.
- Do not split work into tiny commits, tiny PRs, or artificial checkpoints unless isolation is needed to diagnose a real failure.
- Iterate on implementation and tests until the requested product slice works or a real blocking decision is reached.
- Prefer the smallest architecture that makes the product work; do not add speculative infrastructure, documentation, or hardening.

## When to stop for human review

Stop only when the next action is materially high-risk or cannot be inferred safely, for example:

- destructive or irreversible data/repository operations;
- credential, secret, permission, or external-system changes;
- legal/licensing decisions;
- product decisions where two materially different behaviors are both plausible and existing evidence does not resolve the choice.

Normal coding, test fixes, branch/PR creation, CI reruns, and merging a validated feature branch are expected to proceed without repeated prompts when already authorized by the task.

## Testing

- Add tests for real product behavior and regression risk, not for line-count targets.
- Run the repository's complete sequential CI runner after a coherent implementation batch.
- If CI fails for a code defect, fix it and rerun without asking for confirmation.
- Report `PASS`, `FAIL`, or `REPEAT REQUIRED` from execution evidence; do not claim PASS from reasoning alone.

## Podium 7 product constraints

- False merges are more harmful than missed duplicates.
- Provenance is data.
- Preserve stable canonical vehicle IDs and redirects.
- Keep Catalog V2 evolution additive unless a proven product need requires otherwise.
- Use existing `DecisionStatus` semantics; do not present hypotheses or unknowns as evidence-backed facts.

## OpenAI operating references

This execution model follows OpenAI's published guidance that coding agents should move quickly on low-risk work inside clear boundaries, while higher-risk actions become explicit review points, and that agents perform best with structure, context, and room to iterate.

- https://openai.com/index/running-codex-safely/
- https://openai.com/business/guides-and-resources/how-openai-uses-codex/
- https://openai.com/index/harness-engineering/
