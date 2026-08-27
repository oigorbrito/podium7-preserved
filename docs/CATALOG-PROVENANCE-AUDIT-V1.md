# Catalog Provenance Audit V1

Status: implementation prepared; executable validation pending

Issue: #152
Parent: #141

Podium 7 treats provenance as persisted product data. Production Quality Measurement V2 previously verified source/evidence locator shape, but locator shape alone does not prove that the stored catalog remains connected to its evidence.

This audit verifies the persisted links that can be proven from the current Catalog V2 store:

- each canonical catalog vehicle has persisted candidate observations;
- each candidate observation references raw evidence that exists;
- each raw-evidence record references a source that exists;
- each open review task references raw evidence and source that exist;
- each canonical vehicle is readable through the existing consumer API and resolves to the same canonical ID.

The report is `podium7.catalog-provenance-audit.v1` and includes checked-link count, complete-link count, incomplete-link count, completeness ratio, pass/fail and explicit incomplete-link records.

## Utility disposition

`CATALOG_PROVENANCE_AUDIT_UTILITY = INTEGRATE_AFTER_SYNC_AND_VALIDATION`

This is not redundant with input-locator or benchmark-provenance checks. Those checks establish that incoming records name defensible sources; this audit verifies that the **persisted catalog graph after ingestion** still resolves canonical vehicle → candidate → raw evidence → source and that open review evidence remains reachable.

The audit therefore catches storage/link corruption and consumer/persistence divergence that source-shape validation cannot detect. It is complementary to #154/#155: this block verifies internal persisted completeness, while evidence traceability exposes a consumer-facing projection.

An empty store now fails explicitly with `EMPTY_AUDIT_SCOPE` rather than passing by vacuity. If synchronization reveals an equivalent full persisted-link audit upstream, classify this block `REDUNDANT`; otherwise current evidence supports integration after executable validation.

The audit does not reconstruct missing provenance, infer evidence from labels, or alter identity/fusion/publication rules. A missing persisted link is reported as incomplete.

This is a bounded operating-corpus audit, not a universal completeness claim. Repository-required executable validation remains pending while #112 prevents hosted workflow steps from executing.
