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

The audit does not reconstruct missing provenance, infer evidence from labels, or alter identity/fusion/publication rules. A missing persisted link is reported as incomplete.

This is a bounded operating-corpus audit, not a universal completeness claim. Repository-required executable validation remains pending while #112 prevents hosted workflow steps from executing.
