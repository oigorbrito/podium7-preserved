# Public Web Acquisition Characterization V1

Status: `LOCALLY_VERIFIED` for one GitHub-hosted live observation on 2026-08-23

## Purpose

Measure the existing Direct HTTP Acquisition V1 contract against the exact public HTTPS source URLs already represented by the retained web-extraction benchmarks. This is an operational compatibility observation, not a heterogeneous-web success estimate and not a permanent live-network test gate.

## Frozen inventory basis

The inventory is derived at runtime from the existing benchmark case inventories rather than maintained as a second URL list:

- Autoevolution dataset: `autoevolution-source-family-1.0`;
- FuelEconomy.gov dataset: `fueleconomy-find-a-car-source-family-1.0`;
- 16 benchmark cases represented;
- 13 unique exact HTTPS URLs after deduplication;
- 9 Autoevolution URLs and 4 FuelEconomy.gov URLs.

Shared URLs retain every benchmark case ID that depends on them.

## Acquisition policy measured

The live run used the existing dependency-free `DirectHttpPolicy` defaults:

- HTTPS only;
- private/non-global network targets blocked by DNS preflight;
- 15 second timeout per request;
- 2,000,000 byte response limit;
- at most 5 redirects, with every redirect target revalidated;
- accepted media types: HTML, plain text, JSON and XHTML;
- `Accept-Encoding: identity` and rejection of unsupported response encodings;
- user agent `Podium7/0.1 direct-http-acquisition`;
- no retry, proxy rotation, browser fallback, JavaScript execution or user-agent impersonation.

Acquisition failures are observations in the report. Unexpected implementation/reporting exceptions still fail the characterization execution.

## Observed result

GitHub Actions run `32653023995`, job `97227431730`, on Ubuntu 24.04 / Python 3.13.15 in the hosted `centralus` runner region completed successfully.

Aggregate result:

- total exact URLs: 13;
- PASS: 4/13 = 30.8%;
- FAIL: 9/13 = 69.2%;
- represented benchmark cases: 16;
- FuelEconomy.gov: 4/4 PASS = 100%;
- Autoevolution: 0/9 PASS = 0%;
- all 9 failures were `HTTP_STATUS` with HTTP 403.

Successful FuelEconomy.gov observations:

| Benchmark case | HTTP | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `chevrolet-bolt-ev-2017` | 200 | 60,073 | `e5c0d4a72108c96fc1f78eb8b57bad5f2738de8ae1fe677af499746021171ef8` |
| `toyota-rav4-prime-2021` | 200 | 62,554 | `be24e34091292b5da101bf9bafb106621b932926834aee24b7d5402ef92e50dc` |
| `tesla-model-3-long-range-awd-2022` | 200 | 60,783 | `7f91b9a18839b38379efbbe2e3d9e89bb4913937b350a15aba0c6ffaeb325d08` |
| `ford-f150-hev-2025` | 200 | 59,033 | `3c165185277b5ffd933bfec55b146c09c333b04434f6a873c6ffd902bc5964fd` |

All nine unique Autoevolution source URLs returned HTTP 403 under the measured policy. No alternate identity, browser emulation or bypass was attempted.

The workflow artifact was `public-web-acquisition-characterization`, artifact ID `9496702454`; the uploaded ZIP SHA-256 was `91d20af27a9ab8676004304934d66e5031dabd4f18ad6f53ba14052b8e540919`.

## Interpretation

The direct HTTP implementation is operationally compatible with all four measured FuelEconomy.gov URLs in this observation. The same policy is not operationally compatible with the nine measured Autoevolution URLs because that source family returned HTTP 403 to every request.

This does **not** mean Autoevolution extraction is invalid: the frozen source-family corpus remains independently reproducible. It means direct live reacquisition from a GitHub-hosted runner using the current explicit Podium7 HTTP identity was refused at the HTTP boundary on this date.

The result also does not justify a generic browser/crawler dependency. It narrows the next decision: if live reacquisition of sources that reject direct HTTP becomes product-critical, that source family needs a separate, policy-aware acquisition experiment. JavaScript/browser navigation, source discovery, robots/rate/politeness behavior, anti-bot policy, production source distribution and heterogeneous-web compatibility remain separately unmeasured.

## Reproduction

The deterministic inventory/report behavior is covered by repository tests and requires no network. A deliberate live observation can be run from repository root with:

`PYTHONPATH=. python scripts/run_public_web_acquisition_characterization.py`

Because public endpoints change, a later live run is a new observation and must not silently replace this historical result.

## Decision classification

- retained exact-URL sample: `ENGINEERING_CHOICE` constrained to already-reproducible source evidence;
- run `32653023995` result: `LOCALLY_VERIFIED` for that runner/time/sample/policy;
- direct HTTP compatibility with arbitrary public sources: `UNKNOWN`;
- selecting a browser/crawler/agent layer: `UNDECIDED` and not justified by this measurement alone.
