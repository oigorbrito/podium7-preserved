# Measurement Artifact V1

Status: implementation prepared; executable validation pending.

## Purpose

Make Production Quality Measurement V2 reproducible as a versioned artifact rather than relying on transient test stdout.

## Contract

A measurement artifact binds the computed quality/operational result to the exact benchmark inputs used to produce it. Each dataset entry records repository-relative name, declared `datasetVersion`, byte length, and SHA-256 over the exact file bytes.

The artifact contains no wall-clock timestamp, so identical inputs and identical measurement code produce byte-for-byte identical JSON when serialized with the canonical writer.

## Safety

This artifact records measurement evidence only. It does not change resolver, evidence, fusion, source, review, ambiguity or publication policy, and it does not pre-fill unexecuted numerical results.

## Validation

Focused tests must prove deterministic serialization, exact input digest binding, rejection of malformed dataset-version metadata, and that the V3 artifact references the four authorized datasets while keeping numerical values execution-derived.
