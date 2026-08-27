# Measurement Artifact V1

Status: implementation prepared; executable validation pending.

## Purpose

Make Production Quality Measurement V2 reproducible as a versioned artifact rather than relying on transient test stdout.

## Contract

A measurement artifact binds already-produced quality/operational reports to the exact benchmark inputs used to produce them. Each dataset entry records a stable dataset name, declared `datasetVersion`, byte length, and SHA-256 over the exact file bytes.

The artifact also records `measurementContractVersion = production-quality-measurement-v2` and requires the known report schemas:

- `podium7.production-identity-quality.v1`;
- `podium7.production-operational-measurement.v1`.

The identity-quality report's declared dataset versions must exactly match the artifact input descriptors. Reports must be strict JSON-compatible; NaN/infinity are rejected.

The artifact contains no wall-clock timestamp or absolute path, so identical inputs and identical supplied reports produce byte-for-byte identical JSON with the canonical writer.

## Execution boundary

Artifact construction does **not** run the identity-quality or operational measurement functions. It only binds reports that were produced by an independently valid measurement execution.

This separation is required because the current 72-record V3 operational replay is blocked by #166/#142 provenance. The artifact layer must not re-run that invalidated path or turn its output into apparently durable evidence. Once the production root is valid, the validated measurement workflow may pass its execution-derived reports into this artifact writer.

## Utility disposition

`MEASUREMENT_ARTIFACT_UTILITY = INTEGRATE_AFTER_SYNC_AND_VALIDATION`

This capability is not redundant with stdout or documentation: it provides a deterministic receipt binding exact input bytes, dataset versions, measurement contract version, and the actual supplied result objects. It makes later comparison/audit possible without pretending that the artifact itself validates the underlying run.

The original design, in which `build_measurement_artifact()` directly executed the current V3 measurement functions, is `REJECTED` because artifact generation must not independently rerun a semantically blocked corpus. The corrected capture-only design is the integration candidate.

If synchronization reveals an equivalent deterministic measurement receipt upstream, classify this block `REDUNDANT`; otherwise current evidence supports integration after executable validation.

## Safety

This artifact records measurement evidence only. It does not change resolver, evidence, fusion, source, review, ambiguity or publication policy, and it does not pre-fill or manufacture unexecuted numerical results.

## Validation

Focused tests prove deterministic serialization, exact input digest binding, malformed/non-object dataset rejection, duplicate-input/name rejection, report-schema enforcement, strict-JSON enforcement, and dataset-version/report binding independently of the blocked V3 replay. A production artifact may only be produced from a measurement run that is itself valid under the repository's current provenance and execution gates.
