# Production Evidence Enrichment V1

Status: active

This cycle reduces measured catalog `REVIEW` load only when stronger source-backed evidence exists. It does not weaken Catalog Identity V2, infer identity from labels alone, or turn public internet access into a CI dependency.

## Block 1 — controlled evidence work

The retained 60-record replay currently produces 22 open review tasks. `podium7.evidence_enrichment.build_source_backed_enrichment_work` converts those tasks into explicit enrichment work while recovering every source locator declared by each source-backed benchmark case, including cases backed by more than one official source.

Expected bounded baseline:

- 13 `MISSING_IDENTITY_EVIDENCE` tasks -> acquire an explicit deterministic identity field from source evidence;
- 9 `LABEL_AMBIGUITY` tasks -> acquire source-backed canonical model/alias evidence;
- zero unknown or provenance-less tasks;
- zero resolver-policy changes.

Official-source revalidation on 2026-08-23 confirmed that the retained Toyota Corolla source explicitly describes the new Corolla as sedan models and separately states hybrid availability. This makes the Corolla body-style review a valid extraction/enrichment experiment: a field may be added only when the source evidence explicitly supports that field for the replay record. The Ford Mustang technical specification likewise confirms that GT and Dark Horse are distinct trims while both use 5.0-litre V8 configurations; therefore a Mustang record missing trim evidence must remain `REVIEW` rather than having a variant guessed.

The enrichment mechanism must preserve these two different outcomes: evidence can close an extraction omission, but evidence showing multiple plausible identities must preserve abstention.

## Nonclaims

The source-backed benchmarks are bounded evidence, not a production-completeness or market-coverage claim. Official discovery candidates such as NHTSA vPIC and FuelEconomy.gov remain discovery evidence unless a stronger source-specific contract explicitly proves an identity field.
