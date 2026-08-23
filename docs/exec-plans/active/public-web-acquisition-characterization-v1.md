# Public web acquisition characterization V1

Status: active — live characterization complete; final repository validation/integration pending

## Outcome

Measure the existing dependency-free direct HTTP acquisition contract against the exact public HTTPS URLs already represented by the frozen Autoevolution and FuelEconomy.gov benchmark inventories.

## Scope

This unit is measurement, not crawler selection. It will:

- derive a deduplicated live inventory from the two existing frozen source-family benchmark files;
- attempt one bounded direct-HTTP GET per exact URL with the existing fail-closed policy;
- record PASS metadata or the existing explicit acquisition error code per URL;
- aggregate success/failure metrics by source family;
- run one GitHub-hosted live characterization and preserve the observed evidence in durable documentation;
- keep the live network probe out of the permanent required CI gate after the measurement is captured.

It will not add browser/JavaScript automation, source discovery, robots/rate scheduling, generic retries, proxy rotation, anti-bot bypass, or production-wide precision/recall claims.

## Acceptance criteria

- deterministic inventory derivation from the existing benchmark case inventories;
- exactly one observation per unique exact source URL, retaining all benchmark case IDs that share it;
- strict HTTPS inventory validation;
- deterministic report schema and aggregation tests without live network access;
- live acquisition failures remain data, not false test failures;
- unexpected implementation/reporting exceptions still fail the characterization workflow;
- one observed GitHub-hosted live measurement is recorded with run/job evidence;
- repository harness, runtime health and isolated test suite pass on the final documented merge candidate;
- clean main concurrency check before squash merge;
- plan archived and `CURRENT-WORK` cleared after integration.

## Measured live result

The temporary PR-only measurement workflow ran once and was then removed from the branch so live public endpoints do not become a permanent required test dependency.

Observed run `32653023995`, job `97227431730`, GitHub-hosted Ubuntu 24.04 / Python 3.13.15:

- 13 unique exact HTTPS URLs representing 16 retained benchmark cases;
- overall direct HTTP PASS: 4/13 = 30.8%;
- FuelEconomy.gov: 4/4 PASS;
- Autoevolution: 0/9 PASS;
- all 9 failures: `HTTP_STATUS`, HTTP 403;
- no retries, browser fallback, proxy rotation, alternate identity or user-agent impersonation;
- artifact ID `9496702454`;
- uploaded ZIP SHA-256 `91d20af27a9ab8676004304934d66e5031dabd4f18ad6f53ba14052b8e540919`.

`docs/PUBLIC-WEB-ACQUISITION-CHARACTERIZATION-V1.md` preserves the policy, per-family interpretation and successful-response hashes. The measurement is `LOCALLY_VERIFIED` only for that runner/time/sample/policy and is not a heterogeneous-web success-rate estimate.

## Decision classification

- exact retained-URL inventory as the first live sample: `ENGINEERING_CHOICE` constrained by current reproducible evidence;
- direct-HTTP success/failure observed in run `32653023995`: `LOCALLY_VERIFIED` only for that runner/time/sample;
- broader public-web compatibility, source discovery, JavaScript navigation and production distribution: `UNKNOWN` unless separately measured.
