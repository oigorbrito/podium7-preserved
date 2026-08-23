from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable
from urllib.parse import quote, urlencode


NHTSA_VPIC_SOURCE_ID = "nhtsa_vpic"
FUELECONOMY_SOURCE_ID = "fueleconomy_gov"
DISCOVERY_ROLE = "discovery_candidate"


@dataclass(frozen=True)
class DiscoveryCandidate:
    source_id: str
    make: str
    model: str
    model_year: int
    source_locator: str
    source_make_id: int | None = None
    source_model_id: int | None = None
    source_model_key: str | None = None
    source_vehicle_id: int | None = None
    source_label: str | None = None
    evidence_role: str = DISCOVERY_ROLE
    identity_proof: bool = False

    def __post_init__(self) -> None:
        if self.evidence_role != DISCOVERY_ROLE:
            raise ValueError("official discovery candidates must use discovery_candidate evidence role")
        if self.identity_proof:
            raise ValueError("official discovery candidates cannot assert identity proof")
        if not self.source_id.strip() or not self.make.strip() or not self.model.strip():
            raise ValueError("source_id, make, and model are required")
        if not self.source_locator.startswith("https://"):
            raise ValueError("source_locator must be an https URL")
        if self.model_year < 1886:
            raise ValueError("model_year is invalid")


def _required_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value.strip()


def _required_positive_int(value: Any, field: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be a positive integer")
    if isinstance(value, int):
        parsed = value
    elif isinstance(value, str) and value.strip().isdigit():
        parsed = int(value.strip())
    else:
        raise ValueError(f"{field} must be a positive integer")
    if parsed <= 0:
        raise ValueError(f"{field} must be a positive integer")
    return parsed


def _year(value: Any, *, minimum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("model_year must be an integer")
    if value < minimum or value > 2100:
        raise ValueError(f"model_year must be between {minimum} and 2100")
    return value


def build_nhtsa_models_locator(make: str, model_year: int) -> str:
    normalized_make = _required_text(make, "make")
    year = _year(model_year, minimum=1996)
    return (
        "https://vpic.nhtsa.dot.gov/api/vehicles/GetModelsForMakeYear/make/"
        f"{quote(normalized_make, safe='')}/modelyear/{year}?format=json"
    )


def build_fueleconomy_model_menu_locator(make: str, model_year: int) -> str:
    normalized_make = _required_text(make, "make")
    year = _year(model_year, minimum=1984)
    return "https://www.fueleconomy.gov/ws/rest/vehicle/menu/model?" + urlencode(
        {"year": year, "make": normalized_make}
    )


def build_fueleconomy_options_menu_locator(make: str, model: str, model_year: int) -> str:
    normalized_make = _required_text(make, "make")
    normalized_model = _required_text(model, "model")
    year = _year(model_year, minimum=1984)
    return "https://www.fueleconomy.gov/ws/rest/vehicle/menu/options?" + urlencode(
        {"year": year, "make": normalized_make, "model": normalized_model}
    )


def discover_nhtsa_models(payload: dict[str, Any], *, make: str, model_year: int) -> tuple[DiscoveryCandidate, ...]:
    if not isinstance(payload, dict):
        raise ValueError("NHTSA payload must be an object")
    normalized_make = _required_text(make, "make")
    year = _year(model_year, minimum=1996)
    locator = build_nhtsa_models_locator(normalized_make, year)

    results = payload.get("Results")
    if not isinstance(results, list):
        raise ValueError("NHTSA Results must be a list")
    count = payload.get("Count")
    if not isinstance(count, int) or isinstance(count, bool) or count != len(results):
        raise ValueError("NHTSA Count must equal the Results length")

    by_model_id: dict[int, DiscoveryCandidate] = {}
    make_ids: set[int] = set()
    for index, item in enumerate(results):
        if not isinstance(item, dict):
            raise ValueError(f"NHTSA result {index} must be an object")
        item_make = _required_text(item.get("Make_Name"), f"NHTSA result {index} Make_Name")
        if item_make.casefold() != normalized_make.casefold():
            raise ValueError(f"NHTSA result {index} Make_Name does not match requested make")
        model = _required_text(item.get("Model_Name"), f"NHTSA result {index} Model_Name")
        make_id = _required_positive_int(item.get("Make_ID"), f"NHTSA result {index} Make_ID")
        model_id = _required_positive_int(item.get("Model_ID"), f"NHTSA result {index} Model_ID")
        make_ids.add(make_id)
        candidate = DiscoveryCandidate(
            source_id=NHTSA_VPIC_SOURCE_ID,
            make=item_make,
            model=model,
            model_year=year,
            source_locator=locator,
            source_make_id=make_id,
            source_model_id=model_id,
            source_label=model,
        )
        prior = by_model_id.get(model_id)
        if prior is not None and prior != candidate:
            raise ValueError(f"NHTSA model ID {model_id} has conflicting records")
        by_model_id[model_id] = candidate

    if len(make_ids) > 1:
        raise ValueError("NHTSA Results contain multiple make IDs for one requested make")
    return tuple(by_model_id[key] for key in sorted(by_model_id))


def _menu_items(payload: dict[str, Any], *, source_name: str) -> tuple[dict[str, Any], ...]:
    if not isinstance(payload, dict):
        raise ValueError(f"{source_name} payload must be an object")
    raw = payload.get("menuItem")
    if isinstance(raw, dict):
        items: Iterable[Any] = (raw,)
    elif isinstance(raw, list):
        items = raw
    else:
        raise ValueError(f"{source_name} menuItem must be an object or list")
    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"{source_name} menuItem {index} must be an object")
        normalized.append(item)
    return tuple(normalized)


def discover_fueleconomy_models(
    payload: dict[str, Any], *, make: str, model_year: int
) -> tuple[DiscoveryCandidate, ...]:
    normalized_make = _required_text(make, "make")
    year = _year(model_year, minimum=1984)
    locator = build_fueleconomy_model_menu_locator(normalized_make, year)
    items = _menu_items(payload, source_name="FuelEconomy model menu")

    by_key: dict[str, DiscoveryCandidate] = {}
    for index, item in enumerate(items):
        text = _required_text(item.get("text"), f"FuelEconomy model menu item {index} text")
        value = _required_text(item.get("value"), f"FuelEconomy model menu item {index} value")
        candidate = DiscoveryCandidate(
            source_id=FUELECONOMY_SOURCE_ID,
            make=normalized_make,
            model=text,
            model_year=year,
            source_locator=locator,
            source_model_key=value,
            source_label=text,
        )
        prior = by_key.get(value)
        if prior is not None and prior != candidate:
            raise ValueError(f"FuelEconomy model key {value!r} has conflicting records")
        by_key[value] = candidate
    return tuple(by_key[key] for key in sorted(by_key, key=str.casefold))


def discover_fueleconomy_vehicle_options(
    payload: dict[str, Any], *, make: str, model: str, model_year: int
) -> tuple[DiscoveryCandidate, ...]:
    normalized_make = _required_text(make, "make")
    normalized_model = _required_text(model, "model")
    year = _year(model_year, minimum=1984)
    locator = build_fueleconomy_options_menu_locator(normalized_make, normalized_model, year)
    items = _menu_items(payload, source_name="FuelEconomy options menu")

    by_vehicle_id: dict[int, DiscoveryCandidate] = {}
    for index, item in enumerate(items):
        text = _required_text(item.get("text"), f"FuelEconomy options menu item {index} text")
        vehicle_id = _required_positive_int(
            item.get("value"), f"FuelEconomy options menu item {index} value"
        )
        candidate = DiscoveryCandidate(
            source_id=FUELECONOMY_SOURCE_ID,
            make=normalized_make,
            model=normalized_model,
            model_year=year,
            source_locator=locator,
            source_model_key=normalized_model,
            source_vehicle_id=vehicle_id,
            source_label=text,
        )
        prior = by_vehicle_id.get(vehicle_id)
        if prior is not None and prior != candidate:
            raise ValueError(f"FuelEconomy vehicle ID {vehicle_id} has conflicting records")
        by_vehicle_id[vehicle_id] = candidate
    return tuple(by_vehicle_id[key] for key in sorted(by_vehicle_id))
