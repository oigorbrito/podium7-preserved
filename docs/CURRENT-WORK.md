# Current work

Status: active
Mode: evidence rollout / hosted validation pending
Decision: `ACCEPTED = PRESERVE_FIELD_LEVEL_MULTI_SOURCE_REPLAY`
Active wave: `PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01`

## Authority
- [`PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01.md`](PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01.md) — frozen baseline/classification.
- [`PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01-POST-ATTRIBUTION.md`](PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01-POST-ATTRIBUTION.md) — executed single-source lane.
- [`PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01-MULTISOURCE-ROLLOUT.md`](PODIUM7-PRODUCTIVE-COVERAGE-WAVE-01-MULTISOURCE-ROLLOUT.md) — current executed rollout, prepared lanes and blocker register.
- [`ADR-0002-DECISION-ACCEPTANCE.md`](ADR-0002-DECISION-ACCEPTANCE.md) — accepted Option B.

## Current executed state
The only authoritative merged measurement remains:
- retained record-sides: `60`;
- replayable: `38`;
- blocked: `22`;
- `SOLE_CASE_SOURCE = 12`;
- `EXPLICIT_FIELD_ATTRIBUTION = 10`;
- `MULTISOURCE_FIELD_ATTRIBUTION_V2 = 16`;
- `MULTI_SOURCE_WITHOUT_EXPLICIT_FIELD_ATTRIBUTION = 20`;
- `MISSING_SIDE_FIELD_ATTRIBUTION = 2`;
- operational effects: 14 CREATE / 14 MATCH / 10 REVIEW / 0 failed / 14 published vehicles.

`MULTISOURCE_RUNTIME = GREEN`

No prepared or probe-only lane below changes those executed numbers.

## Prepared candidate set
All 22 currently blocked record-sides now have a bounded source-family candidate or probe. This is preparation coverage, not executed replay coverage.

`PR #302 / ADJACENT_TCROSS_RETAINED = 6 SIDES`
- clean retained candidate;
- projected after its own validation/merge: `44 / 60`;
- run `33520809588` failed before repository steps were created.

`PR #303 / ONIX_MY26_PLUS_MY25_PROBE = 6 SIDES`
- 2 adjacent MY26 review sides preserve intentionally missing mechanics;
- 4 BR MY25 sides add only temporary primary Chevrolet owner-manual evidence for `1.0 T` + `Etanol / Gasolina`, while retained price evidence continues to support Premier/hatch/MY25/six-speed automatic;
- current head `5e64c0043d03e61033b8bbddb9fd8964f21a1da7`;
- latest run `33522008754` failed pre-step;
- cumulative planning ceiling after #302 and a later clean retained Onix rollout: `50 / 60`.

`PR #304 / GLOBAL_MUSTANG_PROBE = 4 SIDES`
- all four Mustang composite sides now have explicit primary-source partitions;
- the former GT generation gap is covered by Ford Brasil evidence explicitly identifying GT Performance as seventh generation, coupe and 5.0 Coyote V8;
- current head `b0173d27f4b73bbcf098483975d88d10cdee4467`;
- latest run `33521791360` failed pre-step;
- cumulative planning ceiling after prior lanes plus a later retained Mustang rollout: `54 / 60`.

`PR #305 / TOYOTA_10G_PLUS_PORSCHE_991_PROBE = 2 SIDES`
- Toyota: retained 2006 Corolla evidence supplies tenth-generation Corolla Axio/sedan/1.8 2ZR-FE; separate Toyota technical evidence explicitly supplies gasoline fuel semantics for 2ZR-FE;
- Porsche: retained history supplies type 991 generation; official Carrera S (991) specification supplies Carrera S, horizontally opposed six-cylinder engine and coupe body;
- head `c55fca0afc0ee39e6cf5aab11e1cccb3a0c4473f`;
- run `33525155237` failed pre-step with both jobs `steps=null`;
- cumulative planning ceiling: `56 / 60`.

`PR #306 / CORSA_PUBLIC_RECORD_PROBE = 4 SIDES`
- explicitly excludes `corsa-wind-fipe-code-secondary`;
- retained FIPE source remains responsible for lookup/model-year semantics;
- official TCE-PR administrative FIPE table maps code `0040010` to `GM - CHEVROLET / Corsa Wind 1.0 MPFI / EFI 2p`;
- official DETRAN-RR public records provide concrete Corsa Wind year/code observations for the relevant year family;
- head `b74a390e5291977533eb651f5318b83a8dc8de81`;
- run `33525548760` failed pre-step with both jobs `steps=null`;
- cumulative planning ceiling if every lane is independently validated and cleanly retained: `60 / 60`.

`PREPARED_CANDIDATE_SIDES = 22 / 22 CURRENTLY_BLOCKED`

`UNMAPPED_BLOCKED_SIDES_WITHOUT_PREPARED_CANDIDATE = 0`

`THEORETICAL_PREPARED_CEILING = 60 / 60`

The ceiling is not a test result and must never be reported as current product coverage.

## Blocker register
`HOSTED_CI_PRE_STEP`
The current exact-head runs for #302 through #306 all terminate before repository steps execute. Do not merge, rerun repeatedly, or reinterpret these failures as code/test failures. Resume once a fresh exact-head job obtains a runner and creates real steps/logs.

`TOOLING / PROBE_STDOUT_EXTRACTION`
The connector did not expose #301 printed stdout. Retained tests use safe invariants and do not invent exact CREATE/MATCH/REVIEW distributions or published counts.

`EVIDENCE_VALIDATION_PENDING`
Primary/public evidence candidates have been found for every previously bounded evidence/policy line, but #303-#306 are probes. Source qualification becomes retained authority only through a clean data mutation plus real exact-head CI.

## Resume order after hosted execution returns
1. Validate exact current head of #302 with real steps; if both required jobs pass, squash-merge with expected head SHA and remeasure main.
2. Rebase/recreate a clean retained Onix rollout from the new main using only mappings proven by #303; validate exact head and squash-merge.
3. Create a clean retained Mustang rollout from then-current main using #304 evidence; validate and merge.
4. Create a clean retained Toyota/Porsche source-plus-overlay rollout using #305 evidence; validate and merge.
5. Create a clean retained Corsa public-record rollout using #306 evidence, still excluding the secondary enumeration; validate and merge.
6. Remeasure the entire 60-side corpus and operational dispositions from authoritative main. Only that execution may establish whether 60/60 is actually reached.
7. Reconcile this docs PR once to the final merged measurement, exact-head validate it, then squash-merge #298.

For every retained rollout: current-main base, exact field/source audit, exact-head CI with real steps, both jobs green, squash merge with expected head SHA, then remeasure. Never bulk-promote probes or planning counts.

Baseline closeout in [`PROJECT-STATE.md`](PROJECT-STATE.md) remains authoritative outside this controlled product-evolution wave.
