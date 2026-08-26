# Measurement Artifact V1

Status: active

Parent: #141
Parent mission: #139

## Outcome

Produce a deterministic, versioned measurement artifact for the expanded production-quality run, binding execution-derived metrics to the exact benchmark bytes that produced them.

## Boundaries

- artifact metadata must include datasetVersion and SHA-256 for every input dataset;
- no generated timestamp or environment-specific path may affect deterministic serialization;
- numerical metrics must be computed by existing measurement functions, never copied into code or documentation;
- malformed or missing datasetVersion fails closed;
- do not alter resolver, evidence, source, fusion, review, ambiguity or publication policy.

## Acceptance

Focused tests prove deterministic serialization, exact digest binding, malformed-version rejection, and four-dataset V3 coverage. Repository-required executable validation remains mandatory.
