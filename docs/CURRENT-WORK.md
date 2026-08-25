# Current work

Status: external blocker active

Repository implementation work remains complete through PR #111. The only currently declared active item is issue #112, `Restore GitHub Actions hosted-runner execution`.

GitHub-hosted Actions jobs are failing before any workflow step is created (`steps=null`, no job logs) across independent PR heads. A diagnostic re-run of workflow run `32856816240` reproduced the same pre-step failure on new job IDs. This is tracked as an external account/repository execution blocker, not observable code-test failure.

Owner action is limited to GitHub account/repository Actions settings: verify Actions usage/minutes, payment method and budget/spending limits, and repository Actions enablement. Do not change runner architecture or add infrastructure workarounds merely to bypass this condition; ADR-0001 remains in force.

Closure criterion: a normal repository GitHub-hosted workflow run creates and executes actual job steps and produces logs; preferably it is green. After that, close #112 and refresh this file.

Durable unresolved work remains tracked in `TECH-DEBT.md`; completed execution history belongs under `exec-plans/completed/`.
