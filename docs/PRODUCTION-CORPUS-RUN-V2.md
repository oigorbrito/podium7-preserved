# Production Corpus Run V2

Status: implemented

This block replays the three retained source-backed catalog identity gold sets through the real batch-ingestion, identity-resolution, evidence-persistence and consumer-read path.

The replay contains 60 source-backed records derived from 30 curated identity pairs and at least 10 primary-source documents. It is intentionally offline and reproducible: it measures product-path behavior on a materially larger corpus than the six-record V1 operational fixture without making a production-completeness claim or adding a new acquisition family.

Acceptance gate:

- all 60 records parse and execute through batch ingestion;
- zero record-level ingestion failures;
- the run exercises CREATED, MATCHED and REVIEW outcomes;
- persisted catalog records remain readable through the consumer API;
- every replay record retains an HTTPS primary-source locator and deterministic benchmark provenance.

This block does not change resolver policy. Any measured REVIEW or failure is input to the subsequent operational-gap analysis block.
