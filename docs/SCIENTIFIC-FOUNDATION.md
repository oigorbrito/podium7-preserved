# Podium 7 Scientific Foundation

**Consolidation date:** 2026-08-19  
**Primary-source verification:** 2026-08-22  
**Work unit:** `PODIUM7_SCIENTIFIC_FOUNDATION_AND_DOMAIN_V1`

This document records the scientific baseline supplied by the Podium 7 handoff. It does not add a new horizontal research round and does not extrapolate beyond the handoff's stated conclusions. The 2026-08-22 reconstruction verified the canonical bibliography and the decision-relevant experimental claims against primary publication pages where available.

## Canonical references

| ID | Reference | Verified experimental/normative evidence | Recorded project consequence |
|---|---|---|---|
| REF-01 | Hu, Li, Yang, Kang. *SODIUM: From Open Web Data to Queryable Databases*. arXiv:2603.18447v1, 2026. https://arxiv.org/abs/2603.18447 | SODIUM-Bench: 105 tasks, 6 domains, 6 advanced agents; strongest baseline 46.5% accuracy; SODIUM-Agent 91.1%. | Open-web to structured databases is multi-stage; generic agents are not automatically reliable. |
| REF-02 | Bohra et al. *WebLists: Extracting Structured Information From Complex Interactive Websites Using Executable LLM Agents*. arXiv:2504.12682v1, 2025. https://arxiv.org/abs/2504.12682 | 200 extraction tasks across 4 use cases; LLM+search 3% recall, SOTA web agents 31%, BardeenAgent 66%; about 3x lower cost per output row. | Discover/configure once and reuse executable extraction where structure repeats. |
| REF-03 | Wong et al. *WideSearch: Benchmarking Agentic Broad Info-Seeking*. arXiv:2508.07999v2, 2025. https://arxiv.org/abs/2508.07999 | 200 questions (100 English, 100 Chinese), 15+ domains, 10+ systems; most near 0% success, best 5%; cross-validated humans near 100%. | Collection success does not imply adequate coverage. |
| REF-04 | Polshkov et al. *WANDR: A Benchmark for Wide and Deep Research*. arXiv:2608.14747v1, 2026. https://arxiv.org/abs/2608.14747 | 500 realistic tasks; 6 production research systems; strongest high-effort system 0.363 soft F1 and 0.133 hard F1; evidence completeness remains a bottleneck. | Discovery, enrichment, and verifiable evidence remain bottlenecks; facts need inspectable evidence. |
| REF-05 | Hsu et al. *WebDS: An End-to-End Benchmark for Web-based Data Science*. arXiv:2508.01222v2, ICLR 2026. https://arxiv.org/abs/2508.01222 | 870 tasks across 29 websites; Browser Use 80% on WebVoyager but 15% on WebDS; humans around 90%. | Navigation benchmark performance is insufficient evidence for data-acquisition reliability. |
| REF-06 | Steiner, Peeters, Bizer. *MaDI-Bench: An End-to-End Data Integration Benchmark*. arXiv:2606.30371v1, 2026. https://arxiv.org/abs/2606.30371 | End-to-end tasks span schema matching, value normalization, entity matching and conflict resolution; validated with human-engineered, best-of-breed and LLM pipelines, with step-wise and end-to-end evaluation. | Schema matching, normalization, entity matching, and fusion/conflict resolution are distinct stages. |
| REF-07 | Steiner, Bizer. *Automatic End-to-End Data Integration using Large Language Models*. arXiv:2603.10547v1, ICDE 2026 Beyond SQL Workshop. https://arxiv.org/abs/2603.10547 | GPT-5.2 generates schema/value mappings, ER training data and conflict-resolution validation data; 3 case studies; results comparable to human-designed pipelines; about US$10 per case study. | LLMs can configure deterministic integration components instead of executing every operation. |
| REF-08 | Mesquita et al. *KnowledgeNet: A Benchmark Dataset for Knowledge Base Population*. EMNLP-IJCNLP 2019. DOI: 10.18653/v1/D19-1069. https://aclanthology.org/D19-1069/ | 5 baseline approaches; best baseline F1 0.50 versus human 0.82; supports reproducible end-to-end KB population evaluation. | Fact extraction and entity identification are distinct; correct facts attached to wrong entities are still wrong. |
| REF-09 | Wang et al. *Match, Compare, or Select? An Investigation of Large Language Models for Entity Matching*. COLING 2025, ACL 2025.coling-main.8. https://aclanthology.org/2025.coling-main.8/ | 8 ER datasets and 10 LLMs; selecting strategy improves F1 by 16.02% on average over conventional matching; ComEM further improves effectiveness/cost. | Candidate context can improve entity matching; automotive application remains a hypothesis until measured locally. |
| REF-10 | Karapiperis et al. *ALER: An Active Learning Hybrid System for Efficient Entity Resolution*. PVLDB 19(8), 2026. DOI: 10.14778/3811243.3811251; arXiv:2601.20664v1. | Frozen bi-encoder plus lightweight classifier and active learning; 1.3x faster training loop and 3.8x lower resolution latency than the fastest compared baseline in the reported large-scale evaluation. | Human review can be selective rather than uniformly applied. |
| REF-11 | Shrimal et al. *PARSE: LLM Driven Schema Optimization for Reliable Entity Extraction*. EMNLP 2025 Industry Track. DOI: 10.18653/v1/2025.emnlp-industry.184. https://aclanthology.org/2025.emnlp-industry.184/ | Evaluated on SGD, SWDE and internal retail data; up to 64.7% improvement in extraction accuracy on SWDE; 92% of extraction errors reduced within the first retry. | Schema and deterministic validation are active parts of structured extraction. |
| REF-12 | Guo et al. *DTBench: A Synthetic Benchmark for Document-to-Table Extraction*. arXiv:2602.13812v3, KDD 2026. https://arxiv.org/abs/2602.13812 | 5 major capability categories, 13 subcategories; model evaluations show persistent reasoning, faithfulness and conflict-resolution gaps. | Document-to-table extraction needs validation and evidence preservation; conflict/faithfulness remain hard. |
| REF-13 | W3C. *PROV-O: The PROV Ontology*. W3C Recommendation, 30 April 2013. https://www.w3.org/TR/2013/REC-prov-o-20130430/ | Normative recommendation representing provenance through classes/properties including entities, activities, agents and derivation/generation/association relations. | Provenance can explicitly represent entities, activities, agents, generation, association, and derivation. |

## Evidence interpretation boundary

The numbers above are evidence reported by the cited works, not Podium 7 benchmark results. They establish problem characteristics and design direction. They do not prove that Podium 7 must copy any paper's implementation, use a particular framework, or reproduce the same measured performance.

The historical handoff and the primary-source reconstruction agree on the project-relevant conclusions. Practical measured evidence is weighted more strongly than purely theoretical argument when both address the same operational engineering question.

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
