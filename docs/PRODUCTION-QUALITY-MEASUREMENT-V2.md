# Production Quality Measurement V2

Status: implementation prepared; executable results pending

Issue: #141
Parent mission: #139
Depends on: #140 / Production Corpus Run V3

## Purpose

Measure identity safety and operational review load on the expanded 72-record / 36-case source-backed corpus without changing resolver, evidence, fusion, ambiguity or publication policy merely to improve metrics.

## Measurement surfaces

The V2 gate composes the repository's existing measurement paths over the same four datasets used by Production Corpus Run V3:

- identity quality through `evaluate_identity_quality`;
- operational load and durable review causes through `measure_source_backed_operational_corpus`;
- provenance completeness through `build_source_backed_operational_records`.

The executable report must expose:

- auto-match precision and recall;
- false-merge count;
- missed-match count;
- ambiguous-overcommit count;
- identity review rate;
- CREATED / MATCHED / REVIEW / failure distribution;
- durable review causes and open review-task count;
- HTTPS source/evidence locators and benchmark raw-content references for every replay record.

## Source-contribution granularity

The retained `podium7.catalog-identity-golden.v1` schema associates `sourceIds` with a case. It does not associate individual catalog fields with individual source IDs. Therefore a claim such as “source X contributed dimension Y” cannot be reconstructed exactly from these gold files without inventing provenance.

This block records that limitation explicitly. It may report case-level source participation already present in the corpus, but it must not fabricate field-level attribution. A future instrumentation change is justified only if an executed #141 result establishes that this missing granularity blocks a product decision.

## Safety gate

The measurement test requires zero false merges and zero ambiguous overcommit across the retained 36 source-backed identity cases. Precision/recall and review-load values must come from executable output; they are not pre-filled in this document.

## Nonclaims

- The 36 cases are not universal market coverage.
- A green result does not establish production completeness.
- Review volume is not reduced by weakening identity safety.
- Missing per-dimension source attribution is not filled by inference.

## Validation state

Implementation is committed, but numerical results remain pending while issue #112 prevents GitHub-hosted jobs from executing workflow steps. Do not publish guessed measurements or derive follow-up source/resolver issues before executable evidence exists.
