# Source Terms Drift Gate V1

Status: implementation prepared; integration pending repository validation.

Issue: #164
PR: #165
Parent capability: recurring acquisition #128 / PR #132

## Purpose

Add one narrowly scoped compliance-observability gate to the recurring-source coordinator: an approved source may pin the exact HTTPS locator and SHA-256 of the inspected terms/reuse artifact that governs the source operation.

This is independent from source-data schema/content drift. It does not interpret legal text and does not change evidence strength, source hierarchy, resolver behavior, fusion or publication policy.

## Contract

`SourceTermsPin` contains:

- exact HTTPS terms/reuse locator;
- exact SHA-256 digest of the inspected artifact bytes.

The locator rejects surrounding whitespace, credentials and fragments. The digest must be 64 hexadecimal characters and is canonicalized to lowercase.

A source without an applicable pin preserves the #132 behavior unchanged.

## Runtime ordering

A mutation-eligible success still requires the normal #132 one-shot authorization and source-data validation first:

1. exact authorized requested locator;
2. final source host;
3. response-body SHA integrity;
4. expected source media type;
5. expected source schema signature.

Only after those source-data gates pass is the optional terms pin evaluated. This ordering is deliberate: missing or changed terms must never mask source-data host/hash/media/schema drift.

For a pinned source, terms evidence must then:

1. be supplied as a `DirectHttpAcquisition`;
2. have the exact pinned requested locator;
3. retain the same final locator after redirects;
4. have a recorded acquisition hash matching its exact body bytes; and
5. have an exact body SHA-256 equal to the pinned digest.

A terms failure produces `REVIEW_REQUIRED` with `mutation_required=false`. It is an operational/compliance review state, not a data-fusion conflict and not a legal conclusion.

## Nonclaims

- Hash equality does not establish legal permission or compatibility.
- The gate does not parse or interpret legal text.
- The gate does not fetch terms by itself or create crawler/scheduler infrastructure.
- Software licenses, source-data reuse terms and statutory/public-sector access bases remain distinct.
- No donor code/data is imported by this capability.

## Incremental utility decision

`SOURCE_TERMS_DRIFT_GATE_UTILITY = INTEGRATE_AFTER_SYNC_AND_VALIDATION`

The branch was rebuilt on the current #132 head so the PR's incremental code surface is limited to the terms-drift capability, its focused regressions, and this document. Authorization/checkpoint/source-policy hardening remains upstream and must not be counted as #164 value.

## Validation

Focused deterministic tests cover:

- matching pinned terms preserving the normal success path;
- changed or unavailable terms requiring review and blocking mutation;
- requested/final terms locator mismatch;
- terms acquisition hash mismatch;
- malformed/non-HTTPS pins;
- no-pin compatibility;
- source-data drift taking precedence over terms review;
- retention of all upstream #132 authorization/checkpoint/runtime-input regressions.

Repository harness, sequential suite and PR merge-candidate CI remain required. Issue #112 is the external hosted-runner blocker; pre-step failures are not code-test results.
