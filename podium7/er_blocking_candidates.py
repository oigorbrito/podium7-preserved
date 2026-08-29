from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .catalog import CatalogVehicleIdentity, resolve_catalog_pair
from .catalog_benchmark import CatalogBenchmarkCase, CatalogBenchmarkDataset
from .er_pipeline_benchmark import ERPipelineCase, evaluate_er_pipeline


Blocker = Callable[[CatalogVehicleIdentity, CatalogVehicleIdentity], bool]


def _norm(value: str | None) -> str | None:
    if value is None:
        return None
    return " ".join(value.casefold().split())


def retain_all(_: CatalogVehicleIdentity, __: CatalogVehicleIdentity) -> bool:
    return True


def same_make(left: CatalogVehicleIdentity, right: CatalogVehicleIdentity) -> bool:
    return _norm(left.make) == _norm(right.make)


def same_make_model(left: CatalogVehicleIdentity, right: CatalogVehicleIdentity) -> bool:
    return same_make(left, right) and _norm(left.model) == _norm(right.model)


def evaluate_catalog_blocker(
    dataset: CatalogBenchmarkDataset,
    *,
    blocker: Blocker,
) -> dict[str, Any]:
    if not isinstance(dataset, CatalogBenchmarkDataset):
        raise ValueError("dataset must be CatalogBenchmarkDataset")
    if not callable(blocker):
        raise ValueError("blocker must be callable")
    pipeline_cases: list[ERPipelineCase] = []
    for case in dataset.cases:
        retained = blocker(case.left, case.right)
        if not isinstance(retained, bool):
            raise ValueError("blocker must return boolean")
        outcome = resolve_catalog_pair(case.left, case.right).outcome if retained else None
        pipeline_cases.append(
            ERPipelineCase(
                case_id=case.id,
                expected=case.expected,
                candidate_retained=retained,
                verifier_outcome=outcome,
            )
        )
    return evaluate_er_pipeline(pipeline_cases)


def compare_bounded_blockers(dataset: CatalogBenchmarkDataset) -> dict[str, Any]:
    candidates = {
        "retain-all-current-verifier": retain_all,
        "same-make": same_make,
        "same-make-model": same_make_model,
    }
    return {
        "schema": "podium7.er-blocker-comparison.v1",
        "datasetVersion": dataset.version,
        "candidates": {
            name: evaluate_catalog_blocker(dataset, blocker=blocker)
            for name, blocker in candidates.items()
        },
    }


__all__ = [
    "compare_bounded_blockers",
    "evaluate_catalog_blocker",
    "retain_all",
    "same_make",
    "same_make_model",
]
