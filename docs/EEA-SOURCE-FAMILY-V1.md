# EEA Source Family V1

Status: `LOCALLY_VERIFIED` bounded third structured source family.

## Decision boundary

This adapter uses the European Environment Agency (EEA) passenger-car CO2 monitoring dataset as official structured evidence. It does not treat EEA registration/type-approval monitoring rows as canonical retail configurations and does not infer semantic equivalence from matching units alone.

Primary dataset: <https://www.eea.europa.eu/en/datahub/datahubitem-view/fa8b1229-3db6-495d-b18e-9c9b3267c02b>

Discodata API documentation: <https://discodata.eea.europa.eu/Help.html>

Selected table at V1 freeze: `[CO2Emission].[latest].[co2cars_2025Pv31]`, the 2025 provisional passenger-car dataset published 2026-06-25 under Regulation (EU) 2019/631.

The EEA data viewer and metadata identify fields including make, commercial name, manufacturer, type-approval number, type, variant, version, mass in running order, fuel type/mode, engine capacity, engine power, electric energy consumption and registration year. Fuel-mode metadata identifies Hybrid (`H`), Monofuel (`M`) and Plug-in hybrid (`P`); the frozen electric row uses the source combination `Ft=electric`, `Fm=E`.

## Frozen acquisition evidence

The exact bounded source locator is pinned in `benchmarks/eea_source_family_v1.json`. Acquisition used the existing `DirectHttpPolicy` defaults with no proxy, browser, retry, stealth or alternate identity.

Observed GitHub Actions run `32656518259`, job `97235995006`, Ubuntu 24.04.4 / Python 3.13.15:

- HTTP 200;
- `application/json`, UTF-8;
- zero redirects;
- 4 requested/returned source record IDs: `162744190`, `162744191`, `162744196`, `162744197`;
- exact response size: 1,165 bytes;
- exact SHA-256: `847fa97a46ae32d60673fe63b5ebeeb2d35575771c607b806e3bdedd1c7d2ec9`;
- frozen bytes: `data/raw/web/eea-v1/eea-passenger-cars-2025-bounded-v1.json`.

The snapshot is committed directly in Git and the benchmark loader verifies both byte size and SHA-256 before evaluating any row. The temporary live workflow was removed after capture; public network access is not a permanent CI dependency.

## V1 fact mapping

Only mappings with aligned source meaning and a frozen inspected case are promoted to Podium facts:

| EEA evidence | Podium fact | V1 behavior |
|---|---|---|
| `Ep (KW)` engine power | `power` | kW identity normalization; required |
| `Ec (cm3)` engine capacity | `displacement` | cc identity normalization for non-electric rows; absent electric capacity is not invented |
| `Ft=petrol`, `Fm=M` | `fuel_type=gasoline` | supported |
| `Ft=petrol`, `Fm=H` | `fuel_type=hybrid` | supported |
| `Ft=petrol/electric`, `Fm=P` | `fuel_type=plug_in_hybrid` | supported |
| `Ft=electric`, `Fm=E` | `fuel_type=electric` | supported for the frozen V1 combination |

Unknown fuel type/mode pairs fail explicitly with `UNSUPPORTED_FUEL_SEMANTICS`; there is no generic string fallback.

## Preserved evidence that is deliberately not promoted

`M (kg)` is EEA **mass in running order**. V1 retains it as `mass_in_running_order_kg` regulatory evidence but does **not** map it to Podium `curb_weight`. Equal units do not establish equal semantics.

`Ewltp (g/km)` and `Z (Wh/km)` are also retained as source regulatory evidence. V1 does not add new normalized emissions or electric-efficiency facts merely because the fields are present.

Member state, make, commercial name, manufacturer, type-approval number, type, variant, version, registration year and status are preserved as EEA identity/support evidence. Type/variant/version are not declared equivalent to a globally unique retail trim.

## Independently inspected benchmark slice

The gold file `benchmarks/eea_source_family_v1.json` classifies four source rows independently from extraction code:

1. Polestar 4 electric — power + electric fuel type; source displacement is null;
2. Mercedes-Benz C 300 4MATIC — power + displacement + hybrid fuel type;
3. Volvo XC60 — power + displacement + plug-in-hybrid fuel type;
4. Volkswagen Taigo — power + displacement + gasoline fuel type.

Across these four rows there are 11 promoted source target fields.

Expected deterministic characterization:

- strict: 4/4 cases, 11/11 emitted target fields correct, zero incorrect emitted fields, precision 1.0, recall 1.0;
- partial-evidence: 11/11 retained target fields correct, zero unresolved targets and zero issues on the frozen slice.

These numbers characterize only this bounded inspected slice. They are not production-wide European precision/recall estimates.

## Failure semantics covered by tests

The deterministic suite additionally verifies:

- duplicate source record IDs are rejected;
- malformed/non-standard JSON constants are rejected;
- missing required engine power produces an explicit `MISSING_FACT` issue while other partial evidence remains available;
- unsupported fuel-mode combinations produce `UNSUPPORTED_FUEL_SEMANTICS` and are not normalized by guesswork;
- an electric row with null engine capacity does not invent displacement;
- mass in running order remains preserved source evidence and never appears as `curb_weight`.

## Reproduction

Strict frozen benchmark:

```bash
python scripts/run_eea_source_family.py
```

Partial evidence benchmark:

```bash
python scripts/run_eea_source_family.py --partial-evidence
```

Both operate only on committed deterministic evidence.

## What this establishes

- a third official, structurally different frozen source family can be acquired and evaluated through Podium's evidence discipline;
- exact source bytes, locator, source IDs and hash are reproducible;
- EEA power, engine capacity and the four benchmarked fuel type/mode combinations can be mapped without silent semantic widening;
- useful regulatory evidence can be retained without forcing it into an incompatible canonical attribute.

## What this does not establish

- production-wide EEA coverage or error rates;
- that one EEA row equals one canonical retail trim;
- canonical identity resolution from EEA type/variant/version alone;
- `mass in running order == curb_weight`;
- diesel/diesel-electric fuel-mode mappings in this V1 artifact;
- generalized emissions or electric-efficiency normalization;
- source discovery completeness or recurring-operation acquisition policy.

## Decision classification

- EEA ownership, publication scope, table/interface and field semantics: `EVIDENCE_BACKED`;
- exact four-row network response and snapshot pin: `LOCALLY_VERIFIED`;
- selected promoted/non-promoted mappings: `ENGINEERING_CHOICE` constrained by evidence;
- production-wide quality/generalization: `UNKNOWN`.
