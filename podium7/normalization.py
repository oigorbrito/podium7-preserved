from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any


@dataclass(frozen=True)
class NormalizationResult:
    value: Any
    unit: str | None
    rule: str


def _finite_number(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("numeric value is required") from exc
    if not math.isfinite(number):
        raise ValueError("numeric value must be finite")
    return number


def _finite_identity(value: Any) -> Any:
    _finite_number(value)
    return value


def _round(value: float) -> float:
    if not math.isfinite(value):
        raise ValueError("normalized numeric value must be finite")
    return round(value, 6)


def normalize_fact(attribute: str, value: Any, unit: str | None) -> NormalizationResult:
    if attribute == "power":
        if unit == "kW":
            return NormalizationResult(_finite_identity(value), "kW", "power.kw.identity.v1")
        if unit in {"hp", "bhp"}:
            return NormalizationResult(_round(_finite_number(value) * 0.7456998716), "kW", "power.hp_to_kw.v1")
        if unit in {"cv", "PS"}:
            return NormalizationResult(_round(_finite_number(value) * 0.73549875), "kW", "power.metric_hp_to_kw.v1")

    if attribute == "torque":
        if unit == "Nm":
            return NormalizationResult(_finite_identity(value), "Nm", "torque.nm.identity.v1")
        if unit in {"lb-ft", "lbft"}:
            return NormalizationResult(_round(_finite_number(value) * 1.3558179483314), "Nm", "torque.lbft_to_nm.v1")
        if unit == "kgfm":
            return NormalizationResult(_round(_finite_number(value) * 9.80665), "Nm", "torque.kgfm_to_nm.v1")

    if attribute == "displacement":
        if unit == "cc":
            return NormalizationResult(_finite_identity(value), "cc", "displacement.cc.identity.v1")
        if unit in {"L", "l"}:
            return NormalizationResult(_round(_finite_number(value) * 1000.0), "cc", "displacement.l_to_cc.v1")

    if attribute in {"length", "width", "height", "wheelbase"}:
        if unit == "mm":
            return NormalizationResult(_finite_identity(value), "mm", f"{attribute}.mm.identity.v1")
        if unit in {"in", "inch", "inches"}:
            return NormalizationResult(_round(_finite_number(value) * 25.4), "mm", f"{attribute}.in_to_mm.v1")

    if attribute == "curb_weight":
        if unit == "kg":
            return NormalizationResult(_finite_identity(value), "kg", "curb_weight.kg.identity.v1")
        if unit in {"lb", "lbs"}:
            return NormalizationResult(_round(_finite_number(value) * 0.45359237), "kg", "curb_weight.lb_to_kg.v1")

    if attribute == "fuel_economy_combined":
        if unit == "L/100km":
            return NormalizationResult(_finite_identity(value), "L/100km", "consumption.l100km.identity.v1")
        if unit == "mpg-US":
            mpg = _finite_number(value)
            if mpg <= 0:
                raise ValueError("mpg must be greater than zero")
            return NormalizationResult(_round(235.214583 / mpg), "L/100km", "consumption.mpg_us_to_l100km.v1")

    if attribute == "fuel_type":
        token = str(value).strip().casefold()
        aliases = {
            "gasoline": "gasoline", "petrol": "gasoline", "diesel": "diesel",
            "electric": "electric", "electricity": "electric", "hybrid": "hybrid",
            "plug-in hybrid": "plug_in_hybrid", "phev": "plug_in_hybrid",
        }
        return NormalizationResult(aliases.get(token, token.replace(" ", "_")), None, "fuel_type.token.v1")

    if attribute == "transmission":
        token = " ".join(str(value).strip().casefold().split())
        return NormalizationResult(token, None, "transmission.token.v1")

    if attribute == "drivetrain":
        token = " ".join(str(value).strip().casefold().split())
        aliases = {
            "front wheel drive": "fwd", "rear wheel drive": "rwd",
            "all wheel drive": "awd", "four wheel drive": "4wd", "4 wheel drive": "4wd",
        }
        return NormalizationResult(aliases.get(token, token.replace(" ", "_")), None, "drivetrain.token.v1")

    return NormalizationResult(value, unit, "identity.unspecified.v1")
