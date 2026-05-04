"""
HTTP routes — thin wrappers around the engine.

The pattern for every endpoint is the same: validate the request with
Pydantic, call into the engine, repackage the dataclass result as a dict
the response model can serialize. No business logic lives here.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.schemas import (
    ExperimentRequest, ExperimentResponse,
    SolveRequest, SolveResponse,
    SelectionModel,
)
from app.engine import runner, selector


router = APIRouter()


# ---------------------------------------------------------------------------
# health / metadata
# ---------------------------------------------------------------------------

@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/algorithms")
def list_algorithms() -> dict[str, list[str]]:
    """Map of problem type -> algorithms the engine knows about."""
    return {
        "knapsack": ["knapsack_dp", "brute_force_knapsack"],
        "routing":  ["dijkstra_greedy", "brute_force_routing"],
        "sorting":  ["merge_sort", "brute_force_sort"],
        "search":   ["binary_search", "brute_force_search"],
    }


# ---------------------------------------------------------------------------
# selection only — useful for the UI to preview the recommendation card
# without actually running anything yet
# ---------------------------------------------------------------------------

@router.post("/select", response_model=SelectionModel)
def select_only(spec: SolveRequest) -> dict[str, Any]:
    sel = selector.select(_to_problem_spec(spec))
    return selector.selection_to_dict(sel)


# ---------------------------------------------------------------------------
# main solve endpoint
# ---------------------------------------------------------------------------

@router.post("/solve", response_model=SolveResponse)
def solve(req: SolveRequest) -> dict[str, Any]:
    sel = selector.select(_to_problem_spec(req.spec.model_dump()))

    # if the selector bailed out (e.g. negative-weight routing) tell the
    # client gracefully — don't 500.
    if sel.algorithm == "unsupported":
        return {
            "selection": selector.selection_to_dict(sel),
            "result": None,
            "error": "no implemented algorithm fits this problem instance",
        }

    try:
        result = runner.run_one(sel.algorithm, req.payload)
    except ValueError as exc:
        # algorithm refused the input (negative weight slipped through, etc.)
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "selection": selector.selection_to_dict(sel),
        "result": _algo_result_to_dict(result),
        "error": None,
    }


# ---------------------------------------------------------------------------
# experiment mode
# ---------------------------------------------------------------------------

@router.post("/experiment", response_model=ExperimentResponse)
def experiment(req: ExperimentRequest) -> dict[str, Any]:
    try:
        return runner.run_experiment(req.problem_type, req.payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _to_problem_spec(spec: Any) -> selector.ProblemSpec:
    """Build the engine-side dataclass from either a dict or a Pydantic model."""
    if hasattr(spec, "model_dump"):
        spec = spec.model_dump()
    return selector.ProblemSpec(
        problem_type=spec["problem_type"],
        n=spec["n"],
        time_budget_ms=spec["time_budget_ms"],
        quality=spec.get("quality", "best-effort"),
        has_negative_weights=spec.get("has_negative_weights", False),
        is_sorted=spec.get("is_sorted", False),
        force_brute_force=spec.get("force_brute_force", False),
    )


def _algo_result_to_dict(res) -> dict[str, Any]:
    return asdict(res)
