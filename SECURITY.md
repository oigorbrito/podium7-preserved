# Security Policy

## Reporting a vulnerability

Do not publish exploit details, credentials, private data, or sensitive reproduction material in a public issue or pull request.

For now, report a suspected vulnerability privately to the repository owner through an existing private communication channel associated with the project. Include the affected component, impact, minimal reproduction steps, and any relevant commit or version identifiers.

## Scope

Security-sensitive areas include network acquisition, URL and redirect handling, persistence integrity, evidence/provenance handling, package/build boundaries, CI configuration, and accidental credential exposure.

## Handling

Security reports should be reproduced against the smallest affected surface, fixed with a regression test where feasible, and validated through the canonical CI workflow before integration. Do not weaken fail-closed behavior merely to make a failing case pass.
