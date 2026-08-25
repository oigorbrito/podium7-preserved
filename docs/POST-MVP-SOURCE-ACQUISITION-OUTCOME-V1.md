# Post-MVP source acquisition outcome V1

Status: implementation complete on stacked draft PRs; executable integration validation pending external runner recovery.

Parent mission: #122.

## Scope completed

### #123–#125 — evidence baseline, qualification, contracts

PR #129 establishes the measured source-gap baseline, qualifies the smallest defensible source set, and freezes source-specific contracts. NHTSA vPIC and EEA are `ADAPT`; WSDenatran remains `UNDECIDED` because legitimate automated access requires SENATRAN/SERPRO authorization. No restricted-source bypass is permitted.

### #126 — bounded adapters

PR #130 adds bounded NHTSA vPIC and EEA evidence adapters.

NHTSA vPIC:
- exact JSON bytes are hashed and bound to an external content-addressed raw-evidence reference;
- only allowlisted explicit variables are emitted;
- source-native Trim, BodyClass, Series and IDs stay namespaced;
- model year is not manufacture year;
- missing optional values emit no negative evidence;
- malformed cardinality, types, locators or raw-evidence bindings fail closed.

EEA:
- the existing strict EEA source-family extraction is converted into `RawEvidence` and `CandidateFact` records;
- type-approval/type/variant/version and registration year remain EEA regulatory semantics;
- EEA regulatory variant is not retail trim and registration year is not model/manufacture year;
- unsupported/incomplete required extraction issues fail closed;
- exact raw-content hash binding is required.

### #127 — bounded multi-source validation

PR #131 adds a deterministic measurement harness over the unchanged fusion model. The bounded corpus deliberately includes corroboration, single-source regulatory evidence, normalized conflict, year-semantic separation, unsupported retail variant and unsupported manufacture year.

The encoded expected corpus result is six cases: three canonical, one corroborated, one explicit conflict, two `REVIEW`, zero incorrect dispositions, complete candidate-to-fusion provenance, and zero resolver-policy changes. These are corpus-local expectations, not production-completeness claims.

### #128 — recurring acquisition controls

PR #132 adds a recurring-acquisition coordinator on top of the existing `RecurringSourceGate` and HTTP/network target safety implementation.

The coordinator:
- accepts only explicitly contracted source IDs;
- preserves existing HTTPS/host/robots/pacing enforcement;
- pins expected media type and source-specific schema signature;
- validates final host and response SHA integrity;
- emits `DRIFT` with no mutation on host/hash/media/schema drift;
- emits `UNCHANGED` with no mutation for identical content;
- emits `ACCEPTED` only for new valid content;
- bounds retries and surfaces `DEGRADED` after exhaustion;
- resets retry state after valid recovery.

## Invariants preserved

No source hierarchy, evidence threshold, fusion rule, ambiguity behavior, identity-resolution rule or publication principle is changed. No new `STRONG` identifier namespace is introduced. No stealth, CAPTCHA bypass, proxy rotation or undocumented restricted-source access is added.

## Validation state

Focused deterministic tests are present in PRs #130–#132. Repository-required executable validation is not complete because GitHub Actions hosted-runner execution remains broken under #112.

On run `32907790324`, both `tests` and `minimum-python` completed as failures with `steps=null`; the jobs did not execute repository commands. Earlier PR #130 showed the same no-step failure pattern. Therefore no executable PR in this stack is marked PASS or merge-ready merely from static inspection.

## Integration order after runner recovery

1. validate and squash-merge #129;
2. rebase/retarget, validate and squash-merge #130;
3. rebase/retarget, validate and squash-merge #131;
4. rebase/retarget, validate and squash-merge #132;
5. run the mission-level readiness/quality gates and close #126, #127, #128 and #122 only if all required executable checks are green.

Until then the correct mission state is `IMPLEMENTATION_COMPLETE / INTEGRATION_PENDING_EXTERNAL_CI`.
