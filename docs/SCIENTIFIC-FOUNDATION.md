# Podium 7 Scientific Foundation

**Consolidation date:** 2026-08-19  
**Work unit:** `PODIUM7_SCIENTIFIC_FOUNDATION_AND_DOMAIN_V1`

This document records the scientific baseline supplied by the Podium 7 handoff. It does not add a new horizontal research round and does not extrapolate beyond the handoff's stated conclusions.

## Canonical references

| ID | Reference | Recorded project consequence |
|---|---|---|
| REF-01 | Hu, Li, Yang, Kang. *SODIUM: From Open Web Data to Queryable Databases*. 2026. arXiv:2603.18447 | Open-web to structured databases is multi-stage; generic agents are not automatically reliable. |
| REF-02 | Bohra et al. *WebLists: Extracting Structured Information From Complex Interactive Websites Using Executable LLM Agents*. 2025. arXiv:2504.12682 | Discover/configure once and reuse executable extraction where structure repeats. |
| REF-03 | Wong et al. *WideSearch: Benchmarking Agentic Broad Info-Seeking*. 2025. arXiv:2508.07999 | Collection success does not imply adequate coverage. |
| REF-04 | Polshkov et al. *WANDR: A Benchmark for Wide and Deep Research*. 2026. arXiv:2608.14747 | Discovery, enrichment, and verifiable evidence remain bottlenecks; facts need inspectable evidence. |
| REF-05 | Hsu et al. *WebDS: An End-to-End Benchmark for Web-based Data Science*. 2025 / ICLR 2026. arXiv:2508.01222 | Navigation benchmark performance is insufficient evidence for data-acquisition reliability. |
| REF-06 | Steiner, Peeters, Bizer. *MaDI-Bench: An End-to-End Data Integration Benchmark*. 2026. arXiv:2606.30371 | Schema matching, normalization, entity matching, and fusion/conflict resolution are distinct stages. |
| REF-07 | Steiner, Bizer. *Automatic End-to-End Data Integration using Large Language Models*. 2026. arXiv:2603.10547 | LLMs can configure deterministic integration components instead of executing every operation. |
| REF-08 | Mesquita et al. *KnowledgeNet: A Benchmark Dataset for Knowledge Base Population*. EMNLP-IJCNLP 2019. DOI: 10.18653/v1/D19-1069 | Fact extraction and entity identification are distinct; correct facts attached to wrong entities are still wrong. |
| REF-09 | Wang et al. *Match, Compare, or Select? An Investigation of Large Language Models for Entity Matching*. COLING 2025. ACL 2025.coling-main.8 | Candidate context can improve entity matching; automotive application remains a hypothesis until measured locally. |
| REF-10 | Karapiperis et al. *ALER: An Active Learning Hybrid System for Efficient Entity Resolution*. PVLDB 19(8), 2026. DOI: 10.14778/3811243.3811251 | Human review can be selective rather than uniformly applied. |
| REF-11 | Shrimal et al. *PARSE: LLM Driven Schema Optimization for Reliable Entity Extraction*. EMNLP 2025 Industry Track. DOI: 10.18653/v1/2025.emnlp-industry.184 | Schema and deterministic validation are active parts of structured extraction. |
| REF-12 | Guo et al. *DTBench: A Synthetic Benchmark for Document-to-Table Extraction*. 2026. arXiv:2602.13812 | Document-to-table extraction needs validation and evidence preservation; conflict/faithfulness remain hard. |
| REF-13 | W3C. *PROV-O: The PROV Ontology*. W3C Recommendation, 30 April 2013. | Provenance can explicitly represent entities, activities, agents, generation, association, and derivation. |

## Convergent principles

### Pipeline, not black box — `EVIDENCE_BACKED`

Acquisition, extraction, normalization, entity resolution, and fusion must be observable as separate logical responsibilities.

### Generic agent is not proof of reliability — `EVIDENCE_BACKED`

Successful browsing or answering does not establish completeness or correctness of acquisition.

### Discover once, reuse — `EVIDENCE_BACKED` direction

Stable repeated operations should prefer validated reusable artifacts where possible.

### Entity resolution is first-class — `EVIDENCE_BACKED`

Identity resolution requires explicit representation and independent tests. String equality is not sufficient evidence of identity.

### Provenance is part of the data — `EVIDENCE_BACKED`

The system must be able to trace a value to evidence, source, acquisition context, transformations, and canonical-selection activity.

### Conflict must be preserved — `EVIDENCE_BACKED`

Conflicting candidates must remain inspectable. Silent last-write-wins is not an acceptable default policy.

## What remains undetermined

The baseline does not scientifically determine language, database, crawler, browser agent, ORM, physical architecture, API style, exact automotive canonical schema, source authority, automotive ER algorithm, or confidence thresholds.

Those items remain `ENGINEERING_CHOICE`, `HYPOTHESIS`, or `UNKNOWN` until Podium 7 produces local evidence.
