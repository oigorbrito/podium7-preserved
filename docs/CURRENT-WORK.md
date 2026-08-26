# Current work

Status: active

Parent mission: #139 — production-scale evidence-backed catalog operation.

Current block: #148 — persist versioned review-cause snapshots required by #141's durable review-cause measurement.

Dependency: #141 / PR #143 defines the production-quality measurement surface. This block closes a durability gap in that surface: raw comparison reasons were persisted, but operational cause categories were previously recomputed at measurement time.

Acceptance for this block:

- persist immutable review-cause snapshots derived only from the task's persisted candidate comparison reasons;
- record the classifier version used for each snapshot;
- preserve multiple and unknown causes without choosing a silent winner;
- write snapshots in the same ingestion transaction as review-task creation;
- make repeated ingestion/snapshot writes idempotent only for identical content;
- report legacy review tasks without snapshots explicitly rather than retroactively classifying them;
- make operational measurement consume the persisted snapshots while retaining raw reason counts;
- preserve resolver/evidence/fusion/source/publication/review-resolution semantics.

Plan: `docs/exec-plans/active/REVIEW-CAUSE-SNAPSHOT-V1.md`.

Issue #112 remains external GitHub Actions debt. Implementation may be prepared, but PASS/merge still requires executable repository validation.
