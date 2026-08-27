# Identity Safety Regression Baseline V1

Status: implementation prepared; executable validation pending

Issue: #150
Parent: #141 / mission #139

## Purpose

Make the #141 requirement to compare against retained identity-safety benchmarks explicit and reproducible.

`PRODUCTION-QUALITY-GATE-V3.md` records the retained 30-case baseline at auto-match precision 1.0, recall 1.0, zero false merges and zero ambiguous overcommit. This block freezes only those already-documented values in `benchmarks/production_identity_safety_baseline_v3.json`.

## Contract

The baseline is bound to dataset versions `1.0`, `br-1.0`, and `br-adjacent-incomplete-1.0`, in that order, and to exactly 30 cases. A dataset or case-count mismatch fails closed before metric comparison.

Precision and recall may not fall below baseline. False merges and ambiguous overcommit may not exceed baseline. The comparator reports current value, baseline value, delta and pass/fail for every metric.

The six cases added by Production Corpus Run V3 remain part of the independent 36-case current measurement. They do not rewrite the retained 30-case baseline.

## Utility disposition

`IDENTITY_SAFETY_BASELINE_UTILITY = INTEGRATE_AFTER_SYNC_AND_VALIDATION`

This is not redundant with the prose quality-gate document. The document records accepted historical results; this block turns those retained results into a machine-checkable non-regression oracle bound to exact dataset versions and case count.

Its decision value is to distinguish two questions that must remain separate:

- whether the expanded/current corpus performs well; and
- whether previously accepted identity-safety behavior has regressed.

A new corpus result must not silently redefine the retained baseline. If an equivalent executable baseline comparator appears upstream during synchronization, classify this block `REDUNDANT`; otherwise current evidence supports integration after executable validation.

## Fail-closed hardening

- baseline version and source-document metadata are required;
- dataset identifiers must be non-empty and unique;
- case counts must be positive non-boolean integers;
- rate metrics reject booleans, out-of-range values, NaN and infinity;
- count metrics remain non-negative non-boolean integers;
- malformed quality-report dataset/count contracts fail before comparison.

## Nonclaims

This baseline does not alter resolver thresholds, evidence rules, ambiguity handling, source hierarchy, fusion or publication policy. It is a regression oracle for retained behavior, not a claim of universal completeness.

## Validation

Focused tests cover exact baseline pass, deliberate metric regression, dataset mismatch, case-count mismatch, malformed metadata/contracts, and non-finite metric rejection. Repository-required execution remains pending while #112 prevents GitHub-hosted workflow steps from running.
