# Public web acquisition characterization V1

Status: completed — integrated by PR #59 on 2026-08-23

## Outcome

Measure the existing dependency-free direct HTTP acquisition contract against the exact public HTTPS URLs already represented by the frozen Autoevolution and FuelEconomy.gov benchmark inventories.

## Scope

This unit is measurement, not crawler selection. It:

- derived a deduplicated live inventory from the two existing frozen source-family benchmark files;
- attempted one bounded direct-HTTP GET per exact URL with the existing fail-closed policy;
- recorded PASS metadata or the existing explicit acquisition error code per URL;
- aggregated success/failure metrics by source family;
- ran one GitHub-hosted live characterization and preserved the observed evidence in durable documentation;
- removed the temporary live-network workflow after the observation so public reachability is not a permanent required CI gate.

It did not add browser/JavaScript automation, source discovery, robots/rate scheduling, generic retries, proxy rotation, anti-bot bypass, or production-wide precision/recall claims.

## Measured live result

Observed live run `32653023995`, job `97227431730`, GitHub-hosted Ubuntu 24.04 / Python 3.13.15:

- 13 unique exact HTTPS URLs representing 16 retained benchmark cases;
- overall direct HTTP PASS: 4/13 = 30.8%;
- FuelEconomy.gov: 4/4 PASS;
- Autoevolution: 0/9 PASS;
- all 9 failures: `HTTP_STATUS`, HTTP 403;
- no retries, browser fallback, proxy rotation, alternate identity or user-agent impersonation;
- live-characterization artifact ID `9496702454`;
- uploaded ZIP SHA-256 `91d20af27a9ab8676004304934d66e5031dabd4f18ad6f53ba14052b8e540919`.

`docs/PUBLIC-WEB-ACQUISITION-CHARACTERIZATION-V1.md` preserves the policy, per-family interpretation and successful-response hashes. The measurement is `LOCALLY_VERIFIED` only for that runner/time/sample/policy and is not a heterogeneous-web success-rate estimate.

## Final validation evidence

- PR: #59 `Characterize direct HTTP against retained public URLs`;
- validated branch head: `56edc8a53cb81ababa3e6d939a6cc8464054b3b3`;
- final merge-candidate run: `32653162036`, job `97227770538`;
- PR merge ref SHA: `d7111d3255598c9a129dbbd106de1215341e5d1a`;
- Python `3.13.15`;
- `HARNESS PASS`;
- runtime health `PASS`;
- repository isolated suite `379/379` PASS;
- validation artifact ID `9496747916`, ZIP SHA-256 `761a2e423e81d20ec062ed2645d3367ef4256b880e273843d5749de23cab90a4`;
- clean pre-merge concurrency check: branch behind `0` commits;
- PR #59 squash merge commit: `fa564d9f6ed228c963e651cc72da51e79c4e84af`.

## Decision classification

- exact retained-URL inventory as the first live sample: `ENGINEERING_CHOICE` constrained by current reproducible evidence;
- direct-HTTP success/failure observed in run `32653023995`: `LOCALLY_VERIFIED` only for that runner/time/sample;
- broader public-web compatibility, source discovery, JavaScript navigation and production distribution: `UNKNOWN` unless separately measured.

## Remaining debt

None for this bounded characterization work unit. `TECH-DEBT.md` retains source-family-specific live acquisition where direct HTTP is refused, JavaScript/browser navigation only when demonstrably required, source discovery, robots/rate/politeness policy, and broader production source distribution/corpus coverage as separate future measurement problems.
