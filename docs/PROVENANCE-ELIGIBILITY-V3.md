# V3 Provenance Eligibility

Status: fixture-derived boundary; executable confirmation pending
Issue: #166

The retained V3 benchmark contains 36 curated cases / 72 record sides across four files.

Current provenance eligibility before historical field-attribution reconstruction:

- 6 cases / 12 record sides: replayable because each case declares exactly one source (`SOLE_CASE_SOURCE`);
- 30 cases / 60 record sides: blocked because they are multi-source and have no populated historical `fieldSourceIds`;
- structural replayable rate: 12 / 72 = 16.67%.

This count is derived from the retained benchmark structure and is frozen by a regression in `tests/test_catalog_operational_field_provenance.py`. It is not an executed operational-quality result, does not claim production completeness, and does not permit silently excluding the blocked 60 sides from a full-V3 measurement.

Multi-source cases remain fail-closed until retained evidence supports explicit field attribution or a separately reviewed evidence-envelope design is adopted.
