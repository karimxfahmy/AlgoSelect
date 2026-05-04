"""
Pydantic models for the public API.

Kept deliberately flat — one input type per endpoint, one output type per
endpoint. No nested generics, no union gymnastics. Easier to read in the
auto-generated /docs page.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# shared problem description
# ---------------------------------------------------------------------------

class ProblemSpecModel(BaseModel):
    """The bit the selector cares about — independent of payload shape."""
    problem_type: Literal["knapsack", "routing", "sorting", "search"]
    n: int = Field(ge=0, le=10_000, description="input size")
    time_budget_ms: int = Field(ge=0, le=600_000, description="acceptable wait")
    quality: Literal["exact", "approximate", "best-effort"] = "best-effort"
    has_negative_weights: bool = False
    is_sorted: bool = False
    force_brute_force: bool = False


# ---------------------------------------------------------------------------
# problem-specific payloads (what the algorithm actually consumes)
# ---------------------------------------------------------------------------

class KnapsackPayload(BaseModel):
    weights: list[int] = Field(min_length=1)
    values: list[int] = Field(min_length=1)
    capacity: int = Field(ge=0)


class RoutingEdge(BaseModel):
    u: str
    v: str
    w: float


class RoutingGraph(BaseModel):
    nodes: list[str] = Field(min_length=1)
    edges: list[RoutingEdge]
    source: str
    directed: bool = False


class RoutingPayload(BaseModel):
    graph: RoutingGraph


class SortingPayload(BaseModel):
    array: list[int] = Field(min_length=0)


class SearchPayload(BaseModel):
    array: list[int] = Field(min_length=1)
    target: int


# ---------------------------------------------------------------------------
# request envelopes
# ---------------------------------------------------------------------------

# A single envelope keeps the API simple: callers send the spec + a payload
# whose shape matches problem_type. We validate the union by hand in the
# route handler — Pydantic discriminated unions get awkward when the
# discriminator lives in a sibling object instead of the payload.

class SolveRequest(BaseModel):
    spec: ProblemSpecModel
    payload: dict[str, Any]


class ExperimentRequest(BaseModel):
    problem_type: Literal["knapsack", "routing", "sorting", "search"]
    payload: dict[str, Any]


# ---------------------------------------------------------------------------
# response envelopes
# ---------------------------------------------------------------------------

class DecisionStepModel(BaseModel):
    question: str
    answer: str
    branch: str


class SelectionModel(BaseModel):
    algorithm: str
    justification: str
    expected_complexity: str
    quality_guarantee: str
    trace: list[DecisionStepModel]


class AlgoResultModel(BaseModel):
    algorithm: str
    problem_type: str
    solution: dict[str, Any]
    value: float
    runtime_ms: float
    trace: dict[str, Any] = {}
    note: str = ""


class SolveResponse(BaseModel):
    selection: SelectionModel
    result: AlgoResultModel | None = None
    error: str | None = None


class ExperimentRunModel(BaseModel):
    algorithm: str
    skipped: bool = False
    reason: str | None = None
    value: float | None = None
    runtime_ms: float | None = None
    solution: dict[str, Any] | None = None
    trace: dict[str, Any] | None = None
    note: str | None = None
    approximation_ratio: float | None = None


class ExperimentResponse(BaseModel):
    problem_type: str
    ranked: list[ExperimentRunModel]
    best_value: float | None = None
