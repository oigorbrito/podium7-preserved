# Current work

Status: active

The current private technical MVP is complete. PR #119 integrated the independent-equivalent validation path, and the intended merge-candidate head passed Operational Readiness V1 and MVP Exit Gate V1 with `validation_source=independent-equivalent`.

Current post-MVP reconciliation work is active. PR #261 was squash-merged into `main` as `a4f45a3` and closes #168. Issue #232 remains open as `BLOCKED_EXTERNAL` pending acceptance of the quantitative PBEV benchmark against the retained current source artifact.

Issue #112, `Restore GitHub Actions hosted-runner execution`, remains open as an infrastructure/operations debt item. GitHub-hosted Actions jobs are still failing before any workflow step is created (`steps=null`, no job logs). This no longer blocks the private MVP because the accepted independent-equivalent execution path produced a passing gate without pretending official CI was green.

Owner action for #112 remains limited to GitHub account/repository Actions settings: verify Actions usage/minutes, payment method and budget/spending limits, and repository Actions enablement. Do not change runner architecture or add infrastructure workarounds merely to bypass this condition; ADR-0001 remains in force.
