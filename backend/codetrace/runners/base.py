from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ResourceLimits:
    timeout_seconds: float = 2.0
    max_output_bytes: int = 64_000
    max_memory_mb: int | None = 256


@dataclass
class TestOutcome:
    test_id: str
    passed: bool
    runtime_ms: float
    timed_out: bool = False
    exception: str | None = None
    expected: Any = None
    actual: Any = None
    is_edge_case: bool = False
    performance_weight: float = 0
    hidden: bool = False
    stderr: str = ""


@dataclass
class ExecutionResult:
    success: bool
    outcomes: list[TestOutcome] = field(default_factory=list)
    stdout: str = ""
    stderr: str = ""
    error: str | None = None
    timed_out: bool = False
    wall_time_ms: float = 0.0


class Runner(ABC):
    """Abstraction for executing student solutions outside the API process."""

    @abstractmethod
    def run(
        self,
        solution_source: str,
        problem: dict[str, Any],
        limits: ResourceLimits,
    ) -> ExecutionResult:
        raise NotImplementedError
