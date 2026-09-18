from __future__ import annotations

import os

from fastapi import APIRouter, HTTPException

from codetrace import __version__
from codetrace.algorithms.registry import get_algorithm, meta_to_dict
from codetrace.problems.registry import get_problem
from codetrace.schemas.api import CompareRequest, EvaluateRequest, HealthResponse, VisualizeRequest
from codetrace.services import algorithms as algo_service
from codetrace.services import evaluation as eval_service

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    eval_enabled = os.environ.get("CODETRACE_ENABLE_EVAL", "true").lower() not in {
        "0",
        "false",
        "no",
    }
    return HealthResponse(status="ok", version=__version__, eval_enabled=eval_enabled)


@router.get("/algorithms")
def list_algorithms() -> list[dict]:
    return algo_service.algorithm_catalog()


@router.get("/algorithms/{algorithm_id}")
def get_algo(algorithm_id: str) -> dict:
    try:
        return meta_to_dict(get_algorithm(algorithm_id))
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/visualize")
def visualize(body: VisualizeRequest) -> dict:
    try:
        result = algo_service.visualize(body.algorithm, body.data)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return result.model_dump()


@router.post("/compare")
def compare(body: CompareRequest) -> dict:
    try:
        if body.sizes:
            return algo_service.compare_scaling(
                body.algorithms[0],
                body.algorithms[1],
                body.sizes,
            )
        return {
            "points": [algo_service.compare_pair(body.algorithms[0], body.algorithms[1], body.data)],
            "disclaimer": (
                "Browser/server timing is affected by the environment and is not a formal benchmark."
            ),
        }
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/problems")
def problems() -> list[dict]:
    return eval_service.problems_catalog()


@router.get("/problems/{problem_id}")
def problem_detail(problem_id: str) -> dict:
    try:
        return get_problem(problem_id, include_hidden=False)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/evaluate")
def evaluate(body: EvaluateRequest) -> dict:
    result = eval_service.evaluate_solution(body.problem_id, body.source)
    if not result.get("ok") and "Unknown problem" in str(result.get("error", "")):
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.post("/generate-array")
def generate_array(size: int = 10, mode: str = "random", seed: int | None = None) -> dict:
    try:
        arr = algo_service.generate_array(size, mode=mode, seed=seed)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"array": arr}
