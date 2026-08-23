# ADR-0001: Market-first evaluation before infrastructure construction

- Status: Accepted
- Date: 2026-08-23
- Decision class: `ENGINEERING_CHOICE`

## Context

Podium 7 already requires evidence before adding infrastructure and rejects unnecessary complexity. A complementary architectural principle is needed for cases where the project considers experimenting with or building infrastructure capabilities that may already exist as mature products, managed services, libraries, platforms, or open-source solutions.

The risk is not only technical complexity. Building infrastructure prematurely can create avoidable maintenance burden, operational risk, lock-in to an internal design, duplicated effort, and delayed product validation.

This ADR does not change product scope. It defines how infrastructure choices must be evaluated and recorded.

## Decision

Before Podium 7 experiments with, prototypes, or builds a non-trivial infrastructure capability, the team MUST first evaluate relevant mature market solutions.

The evaluation MUST determine whether the need is better served by:

1. adopting an existing solution;
2. integrating or adapting an existing solution;
3. building the capability internally.

The decision to adopt, adapt, or build MUST be documented with enough evidence to reconstruct the reasoning later.

At minimum, the record MUST capture:

- the capability or problem being addressed;
- the mature alternatives considered;
- relevant constraints and decision criteria;
- why the selected option is sufficient or necessary;
- why rejected alternatives were not selected;
- material trade-offs, risks, and reversibility concerns;
- whether the conclusion is evidence-backed, locally verified, or an engineering choice.

Absence of a perfect market solution is not, by itself, justification to build. The comparison must be against the actual requirements and constraints of Podium 7.

## Principle

**Evaluate mature solutions before creating infrastructure. Document the adoption-or-build decision.**

Infrastructure experimentation is justified only after the project understands the available mature alternatives and can state why experimentation is still necessary.

## Consequences

### Positive

- reduces unnecessary internal infrastructure;
- improves reuse of mature operational knowledge;
- makes build-vs-buy decisions auditable;
- exposes hidden costs and lock-in earlier;
- preserves engineering effort for differentiated product capabilities;
- makes later reversals or migrations easier to reason about.

### Costs

- adds a small amount of up-front research and documentation;
- may delay implementation when the market landscape is unclear;
- requires periodically revisiting decisions when assumptions materially change.

## Relationship to existing architecture principles

This ADR extends the existing minimality rule. The current rule asks whether a real problem exists and whether a simpler solution is insufficient. This ADR adds another required question before infrastructure is created:

> Does a mature external solution already satisfy the need well enough?

Both gates apply. Passing one does not waive the other.

## Review trigger

Revisit this ADR if Podium 7 reaches a scale or operating model where systematic internal platform development becomes a deliberate product or organizational capability rather than an incidental implementation choice.
