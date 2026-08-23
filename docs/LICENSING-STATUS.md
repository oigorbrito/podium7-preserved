# Podium 7 Licensing Status

**Status:** `PRIVATE_PROPRIETARY`

Podium 7 is currently a private, proprietary project. No public software license is granted at this stage.

The GitHub repository is private. Source access by an authorized collaborator does not grant redistribution, modification, sublicensing, publication, or public-use rights beyond the owner's explicit authorization.

## Current owner decision

Keep the software private/proprietary until the product is operational. A later decision may consider open-source publication and, if appropriate, a license such as MIT or Apache-2.0. That future choice must be explicit and reviewable; it is not implied by the current repository, dependencies, source provenance, or tooling.

## Packaging and release rule

While status is `PRIVATE_PROPRIETARY`:

- `pyproject.toml` must not claim a public SPDX license or public license text;
- no public `LICENSE` grant should be generated from assumption;
- package/public release readiness must remain blocked intentionally;
- internal development, testing, and private operation may continue;
- source-specific acquisition and evidence provenance remain separate from software licensing.

Changing this status to an open-source or other distribution license requires a new explicit owner decision.
