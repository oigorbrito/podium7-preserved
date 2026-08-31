# Podium 7 Architecture

Status: current architecture authority

## Overview

Podium 7 is organized as an evidence pipeline with durable storage and review surfaces around a conservative catalog identity model.

## Main responsibilities

- acquisition: gather source evidence from bounded local, web, and document sources;
- extraction and normalization: convert raw evidence into structured fields;
- identity resolution: compare candidates conservatively and fail closed on ambiguity;
- fusion and conflict handling: preserve contradictory evidence and explicit review causes;
- persistence: store canonical records, evidence, and review state durably;
- export and operator workflows: expose validated operator and consumer paths;
- validation: benchmark the model, the pipeline, and operational readiness.

## Components

- `podium7.http_acquisition`, `podium7.bound_http_acquisition`, `podium7.web_acquisition`, `podium7.pdf_acquisition`, `podium7.document_extraction`
- `podium7.normalization`, `podium7.identity`, `podium7.fusion`, `podium7.catalog_resolution_precedence`
- `podium7.evidence`, `podium7.persistence`, `podium7.catalog`, `podium7.catalog_review`, `podium7.review`
- `podium7.ingestion`, `podium7.export`, `podium7.operational_disposition`, `podium7.operational_priority`
- benchmark and measurement modules under `podium7.*benchmark`

## Boundaries

- acquisition is separate from identity resolution;
- evidence is stored, not inferred away;
- quantitative enrichment does not participate in catalog matching;
- review remains a durable outcome, not a transient error;
- external source families are bounded by the documented contracts and source policies.

## Persistence and provenance

The system relies on durable SQLite-backed persistence for operator state and evidence records. Provenance must remain attached to persisted outcomes and candidate history.

## External integrations

- private operator install and readiness commands;
- source-specific acquisition paths documented in the acquisition contracts;
- validation scripts and benchmark runners;
- GitHub repository CI as the official hosted merge gate when available.

## Decision records

Architecture decisions are recorded in ADRs and specialized design docs. This file describes the current assembled architecture only; it does not restate each ADR.
