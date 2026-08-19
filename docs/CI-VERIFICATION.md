# CI Verification

This branch exists only to trigger and verify the repository-native sequential test workflow.

The workflow executes every discovered `unittest` case one by one, using an isolated Python process per case and stopping on the first failure.

This verification is an `ENGINEERING_CHOICE` for reproducibility hardening. It does not change the scientific baseline or domain semantics.
