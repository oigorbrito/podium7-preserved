# Production Evidence Enrichment V1

Status: implemented

This cycle reduces measured catalog `REVIEW` load only when stronger source-backed evidence exists. It does not weaken Catalog Identity V2, infer identity from labels alone, or turn public internet access into a CI dependency.

## Block 1 — controlled evidence work

The retained 60-record replay initially produced 22 open review tasks. `podium7.evidence_enrichment.build_source_backed_enrichment_work` converts those tasks into explicit enrichment work while recovering every source locator declared by each source-backed benchmark case, including cases backed by more than one official source.

Bounded baseline:

- 13 `MISSING_IDENTITY_EVIDENCE` tasks -> acquire an explicit deterministic identity field from source evidence;
- 9 `LABEL_AMBIGUITY` tasks -> acquire source-backed canonical model/alias evidence;
- zero unknown or provenance-less tasks;
- zero resolver-policy changes.

Official-source revalidation on 2026-08-23 confirmed that the retained Toyota Corolla source explicitly describes the new Corolla as sedan models and separately states hybrid availability. This makes the Corolla body-style review a valid extraction/enrichment experiment: a field may be added only when the source evidence explicitly supports that field for the replay record. The Ford Mustang technical specification likewise confirms that GT and Dark Horse are distinct trims while both use 5.0-litre V8 configurations; therefore a Mustang record missing trim evidence must remain `REVIEW` rather than having a variant guessed.

The enrichment mechanism preserves these two different outcomes: evidence can close an extraction omission, but evidence showing multiple plausible identities preserves abstention.

## Block 2 — fail-closed enrichment application

`benchmarks/source_backed_enrichment_v1.json` records bounded source-backed observations separately from the original gold labels. `podium7.source_backed_enrichment` permits an identity field to be added only when the target field is currently missing, the observation references a source already declared by that benchmark case, and the field type is supported. Existing identity fields cannot be overwritten.

The first bounded observations produce:

- Toyota Corolla body-style re-extraction: `REVIEW -> MATCH` after explicit `body_style=sedan` evidence;
- Ford Mustang missing variant: remains `REVIEW` because the official specification contains both GT and Dark Horse 5.0-litre V8 configurations;
- Porsche 911 partial Carrera label: remains `REVIEW` because generic Carrera evidence does not establish Carrera 4S identity;
- resolver-policy changes: zero.

Label enrichment is therefore evidence-gated as well: the current source-backed label example correctly abstains rather than adding an unsupported alias.

## Block 3 — enriched replay and quality gate

`PRODUCTION-QUALITY-GATE-V3.md` integrates the enrichment observations into the retained operational replay. The 60-record result changes from 19 `CREATED` / 19 `MATCHED` / 22 `REVIEW` to 19 `CREATED` / 20 `MATCHED` / 21 `REVIEW`, with zero ingestion failures. Remaining causes are 12 `MISSING_IDENTITY_EVIDENCE` and 9 `LABEL_AMBIGUITY`.

The companion 30-case source-backed identity quality corpus remains at auto-match precision 1.0 and recall 1.0 with zero false merges and zero ambiguous overcommit. The one-review reduction is therefore attributed to added evidence, not a resolver-policy change.

## Nonclaims

The source-backed benchmarks are bounded evidence, not a production-completeness or market-coverage claim. Official discovery candidates such as NHTSA vPIC and FuelEconomy.gov remain discovery evidence unless a stronger source-specific contract explicitly proves an identity field. The remaining 21 reviews are not assumed to be safely resolvable.
