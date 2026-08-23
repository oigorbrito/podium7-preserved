# Browser acquisition characterization V1

Status: completed — integrated by PR #61 on 2026-08-23

## Outcome

Measure whether a controlled headless Chromium browser can acquire source-relevant Autoevolution content for the exact 9 retained HTTPS URLs that returned HTTP 403 under the existing direct-HTTP policy.

## Scope

This unit was characterization, not a production browser fallback. It:

- derived the exact Autoevolution URL inventory from the retained public-web inventory;
- used Playwright with Chromium in one temporary GitHub-hosted measurement workflow;
- kept default browser identity: no stealth plugins, proxy rotation, custom user-agent, cookie seeding or anti-bot bypass;
- classified success conservatively using 2xx main-document status, non-empty body text and multiple retained Autoevolution specification labels;
- recorded final URL, status, title, byte/hash metadata, relevance markers and elapsed time without retaining full live page content;
- preserved per-URL failures as measurement data while unexpected implementation failures fail the workflow;
- removed the temporary live browser workflow after the observation was captured.

It did not add Playwright to package runtime dependencies, implement generic crawling/navigation, interact with consent/captcha challenges, evade site controls, discover new sources, or claim production-web success rates.

## Measured live result

Observed GitHub Actions run `32654062805`, job `97229988048`, Ubuntu 24.04.4 / Python 3.13.15:

- Playwright `1.62.0`;
- Chromium / Chrome for Testing `151.0.7922.34`;
- 9 unique exact Autoevolution URLs representing 12 retained cases;
- browser acquisition PASS: **0/9 = 0%**;
- all 9 failures: `HTTP_STATUS`, HTTP 403;
- all 9 titles: `Just a moment...`;
- 8/9 body observations contained the configured `cloudflare` indicator; the ninth exposed zero body-text bytes while still returning HTTP 403;
- zero retained specification relevance markers on every URL;
- summed navigation time 2,795 ms; mean 310.6 ms;
- no stealth, proxy, custom user-agent, cookie seeding, challenge interaction, retry or alternate identity;
- live artifact ID `9496973842`;
- uploaded ZIP SHA-256 `1fa79f6e1b0608da380f0049bbc6bb4ebf07ce201ea413c995372788f1aafb00`.

Observed setup cost included a 47.7 MB Playwright wheel, 184.3 MiB Chromium download, 2.3 MiB FFmpeg download, roughly 22.5 seconds for browser/dependency installation and roughly 5.6 seconds wall-clock for the nine-URL measurement step. These values are runner-specific observations.

## Decision

Do **not** add a permanent Playwright/Chromium fallback for this observed Autoevolution refusal. Candidate posture: `REJECT/UNDECIDED` — rejected for this bounded failure mode because it added substantial setup with 0/9 acquisition gain; globally undecided for future independently measured source families that genuinely require JavaScript and succeed under a normal browser identity.

`docs/BROWSER-ACQUISITION-CHARACTERIZATION-V1.md` preserves the measurement, limits and decision. Playwright remains outside runtime/package dependencies.

## Final validation evidence

- PR: #61 `Characterize controlled browser acquisition on refused source URLs`;
- validated branch head: `07b58ac1cf76f9843a939b60b113fa4acc8c4a71`;
- final merge-candidate ref: `7f346f612626d7db1dfa1a84debc7277e703d3a9`;
- final validation run: `32654313054`, job `97230589573`;
- Python `3.13.15`;
- `HARNESS PASS`;
- runtime health `PASS`;
- repository isolated suite **389/389 PASS**;
- validation artifact ID `9497041986`;
- validation ZIP SHA-256 `ab95a7c0a2e26984a0f2d898338768cac79813e3b0ae33d7483a887a8d963480`;
- clean pre-merge concurrency check: branch behind `0` commits;
- PR #61 squash merge commit: `6e9f26598ced90acad06374523a3279a0a77cc7f`.

## Decision classification

- retained 9-URL failure sample: `ENGINEERING_CHOICE` constrained by prior live evidence;
- observed browser results: `LOCALLY_VERIFIED` for run `32654062805` and its recorded runner/time/browser/sample;
- permanent browser fallback for the current observed Autoevolution refusal: `ENGINEERING_CHOICE` not selected because the measured gain was zero;
- browser utility for other source families: `UNKNOWN` until separately measured.

## Remaining debt

None for this bounded browser-characterization work unit. `TECH-DEBT.md` retains compliant alternative live source paths for refused sources, source discovery, robots/rate/politeness policy, broader production source distribution/corpus coverage and stronger SSRF/DNS-rebinding defenses as separate future problems.
