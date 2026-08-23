# EEA Semantic Expansion V2

Status: implemented bounded semantic expansion.

## Current official evidence

The EEA passenger-car Datahub currently exposes the 2025 provisional dataset, published 2026-06-25. The official statistical metadata classifies fuel types as Diesel, Diesel/Electric, Petrol, Petrol/Electric, LPG, NG, E85, Electric and Hydrogen, and fuel modes as Bifuel (B), Hybrid (H), Monofuel (M), Flexfuel (F), Plug-in hybrid (P) and Electric (E).

Primary evidence:
- https://www.eea.europa.eu/en/datahub/datahubitem-view/fa8b1229-3db6-495d-b18e-9c9b3267c02b
- https://sdi.eea.europa.eu/catalogue/srv/api/records/bae40349-0618-411a-996a-1eb3bfa14b3c/attachments/CO2%20from%20cars%20and%20vans_Statistical%20metadata_2024.pdf

## Decision

V2 expands the explicitly enumerated EEA `Ft/Fm` contract with diesel and diesel/electric semantics:

- Diesel + M -> `diesel`;
- Diesel + H -> `hybrid`;
- Diesel/Electric + H -> `hybrid`;
- Diesel/Electric + P -> `plug_in_hybrid`.

Petrol/Electric + H is also admitted as `hybrid`, consistent with the same official classifications. Unknown combinations still fail closed as `UNSUPPORTED_FUEL_SEMANTICS`.

## Retail identity boundary

EEA type approval, type, variant and version remain valuable regulatory identity evidence, but V2 explicitly does **not** promote them to canonical retail identity proof. `EEA_RETAIL_IDENTITY_PROOF` is fixed to `False`. This is a deliberate evidence decision, not an unresolved implementation gap.

## Validation

The frozen semantic benchmark is offline and source-backed by the official classification metadata. It verifies the new diesel/diesel-electric mappings, fail-closed behavior for unknown combinations, and the non-proof retail-identity boundary.
