# OpenAI Codex / harness engineering references

Last verified: 2026-08-22

These official OpenAI sources are the external normative references used to shape the Podium 7 development harness. This file records references and project consequences; the actual recurring execution rules live only in [`../DEVELOPMENT-WORKFLOW.md`](../DEVELOPMENT-WORKFLOW.md).

## Harness engineering

- https://openai.com/index/harness-engineering/

Project consequence: keep `AGENTS.md` short and map-like; use structured repository documentation as the system of record; use progressive disclosure; version active/completed plans and debt; mechanically validate documentation structure, freshness, and cross-links where practical.

## How OpenAI uses Codex

- https://openai.com/business/guides-and-resources/how-openai-uses-codex/

Project consequence: prompts should resemble outcome-first GitHub Issues and rely on persistent repository context instead of restating recurring instructions.

## Introducing Codex / AGENTS.md behavior

- https://openai.com/index/introducing-codex/

Project consequence: repository instructions should tell an agent how to navigate, test, and follow project practices, and programmatic checks named by the repository should be executed after changes.

## Unrolling the Codex agent loop

- https://openai.com/index/unrolling-the-codex-agent-loop/

Project consequence: approval boundaries are environment/permission concerns and instruction precedence matters; Podium 7 keeps repository-level recurring policy in one canonical location rather than scattering it across prompts and docs.

No external reference overrides system/developer/user instructions supplied by the runtime. This repository harness defines project defaults within those higher-level boundaries.
