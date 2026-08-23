# Browser acquisition characterization V1

Status: `LOCALLY_VERIFIED` bounded characterization; no permanent browser fallback selected

## Question

Does a controlled JavaScript-capable Chromium browser acquire source-relevant Autoevolution content for the exact retained URLs that the dependency-free direct-HTTP layer observed as HTTP 403?

This record answers only that bounded question. It does not estimate browser success across the public web and does not authorize anti-bot bypass.

## Frozen sample

The sample is derived from the existing retained source-family inventories rather than chosen after seeing browser results:

- source family: Autoevolution;
- 9 unique exact HTTPS URLs;
- 12 retained benchmark cases represented by those URLs;
- every URL had already returned HTTP 403 in direct-HTTP live run `32653023995`.

No new source URLs were added for this measurement.

## Browser policy

Observed GitHub Actions run `32654062805`, job `97229988048`, on Ubuntu 24.04.4 / Python 3.13.15 used:

- Playwright `1.62.0`;
- Chromium / Chrome for Testing `151.0.7922.34`;
- headless Chromium channel;
- JavaScript enabled;
- default browser identity;
- no stealth plugin or fingerprint modification;
- no proxy or proxy rotation;
- no custom user-agent;
- no cookie/session seeding;
- no captcha/challenge interaction;
- no retry or alternate acquisition identity.

Each URL received one navigation to `domcontentloaded`. A page counts as acquisition PASS only when the main-document status is 2xx, body text is non-empty, no configured block-page indicator is present, and at least four retained Autoevolution specification markers are present. Unexpected implementation exceptions fail the measurement workflow rather than becoming false site failures.

## Observed result

The controlled browser did **not** improve acquisition on this sample:

- browser acquisition PASS: **0/9 = 0%**;
- explicit failures: **9/9**;
- all 9 failure codes: `HTTP_STATUS`;
- all 9 main-document statuses: HTTP **403**;
- all 9 page titles: `Just a moment...`;
- 8/9 body-text observations contained the configured `cloudflare` block indicator;
- the remaining Volkswagen T-Cross response exposed zero body-text bytes while still returning HTTP 403 and the same `Just a moment...` title;
- source-relevance markers: **0 on every URL**;
- final URL remained the requested source URL for every observation;
- summed navigation time: **2,795 ms**;
- mean measured navigation time: **310.6 ms**.

The measurement artifact is `9496973842`; uploaded ZIP SHA-256 is `1fa79f6e1b0608da380f0049bbc6bb4ebf07ce201ea413c995372788f1aafb00`.

The report preserves only observation metadata, byte counts and SHA-256 values rather than retaining full live page content.

## Cost observation

The browser experiment added materially more setup than direct HTTP without increasing acquisition coverage in this sample:

- Playwright Python wheel download observed at about **47.7 MB**;
- Chromium download observed at about **184.3 MiB**;
- FFmpeg download observed at about **2.3 MiB**;
- browser/dependency installation step took roughly **22.5 seconds** in the measured runner;
- the nine-URL measurement step took roughly **5.6 seconds wall-clock**, with **2.795 seconds** summed navigation time.

These are runner-specific observations, not universal performance guarantees.

## Decision

**Do not adopt Playwright/Chromium as a permanent fallback for the currently observed Autoevolution HTTP-403 failure mode.**

Candidate posture: `REJECT/UNDECIDED`:

- `REJECT` for this bounded purpose: controlled Chromium added dependency/setup cost and produced 0/9 source-relevant acquisitions where direct HTTP had already produced 0/9;
- `UNDECIDED` globally: this experiment does not show that browser automation is never appropriate for another independently measured source family that genuinely requires JavaScript and succeeds under a normal browser identity.

Playwright therefore remains outside Podium 7 runtime/package dependencies. A future browser work unit must be triggered by new measured evidence, not by the assumption that a browser inherently bypasses public-site refusal.

## Limits

This result is `LOCALLY_VERIFIED` only for the recorded runner, time, browser version, exact nine URLs and declared policy. It does not prove that Autoevolution is permanently inaccessible, that all browsers receive the same response in all networks, or that browser acquisition is ineffective on unrelated sites.

No attempt was made to evade or defeat site controls. Stealth tooling, proxy rotation, user-agent impersonation, challenge solving and other bypass mechanisms are outside this work unit.
