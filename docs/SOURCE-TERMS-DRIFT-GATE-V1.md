# Source Terms Drift Gate V1

Status: implementation prepared; integration pending repository validation.

Issue: #164
PR: #165
Depends on: #132

## Purpose

Pin the exact inspected terms/reuse artifact for a recurring source so terms drift can block mutation independently of source schema/content drift, without interpreting legal text.

## Contract

An optional `SourceTermsPin` contains an exact HTTPS locator and the SHA-256 digest of the inspected terms artifact bytes.

For pinned sources, successful source data is mutation-eligible only when terms evidence is supplied and its requested locator, final locator, acquisition hash and actual body digest match the pin. Missing or changed terms produce `REVIEW_REQUIRED` with `mutation_required=false`.

Source-data authorization, host, hash, media-type and schema drift are checked first and remain `DRIFT`; terms review cannot mask those failures.

## Utility decision

`SOURCE_TERMS_DRIFT_GATE_UTILITY = INTEGRATE_AFTER_VALIDATION`.

This closes a distinct governance gap: governing terms/reuse artifacts can change independently of source schema/content. The gate records the evidence state but makes no legal conclusion.

## Synchronization

#165 was rebuilt directly on the synchronized current #132 head. Upstream authorization/checkpoint/source-policy hardening is no longer part of the #165 delta. Previous state is preserved as `backup/source-license-drift-164-presync2-20260827`.

Focused terms regressions are isolated in `tests/test_source_terms_drift.py`; #132's recurring-acquisition regression file is unchanged.

## Nonclaims

- Hash equality does not establish legal permission.
- The gate does not interpret license/terms text.
- No donor code/data import or crawler infrastructure is introduced.
- No evidence/resolver/fusion/publication policy changes.

## Validation

Focused deterministic regressions cover matching terms, missing/changed terms, locator/final-locator/hash mismatch, source-data-drift precedence and invalid pins. Repository validation remains blocked by #112.
