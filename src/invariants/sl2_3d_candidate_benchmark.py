"""Benchmark helpers for the sl2 3-dimensional 9x9 candidate branch."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

import sympy as sp

from src.catalog.braid_examples import BraidExample, get_braid_example

from .sl2_3d_colored_jones_candidate import Sl2ThreeDimCandidateResult, compute_sl2_3d_candidate_output


DEFAULT_SL2_3D_CANDIDATE_BENCHMARK_LABELS = ("unknot_1", "trefoil", "figure_eight")


@dataclass(frozen=True, slots=True)
class Sl2ThreeDimCandidateBenchmarkEntry:
    """Store one benchmark example evaluated through the sl2 3-dimensional candidate branch."""

    example_label: str
    result: Sl2ThreeDimCandidateResult
    notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def summary(self) -> str:
        lines = [
            f"Example label: {self.example_label}",
            f"Status: {self.result.status}",
            f"Raw trace: {sp.simplify(self.result.raw_trace)}",
            f"Quantum trace before normalization: {sp.simplify(self.result.quantum_trace_before_normalization)}",
            f"Unreduced candidate output: {sp.simplify(self.result.unreduced_candidate_output)}",
            f"Unknot normalization: {sp.simplify(self.result.unknot_normalization)}",
            f"Reduced candidate output: {sp.simplify(self.result.reduced_candidate_output)}",
        ]
        if self.notes:
            lines.append(f"Notes: {self.notes}")
        if self.metadata:
            lines.append(f"Metadata: {self.metadata}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        return {
            "example_label": self.example_label,
            "result": self.result.to_dict(),
            "notes": self.notes,
            "metadata": dict(self.metadata),
        }

    def to_string(self) -> str:
        return self.summary()


def evaluate_sl2_3d_candidate_example(
    example: BraidExample,
    *,
    q: sp.Expr | None = None,
) -> Sl2ThreeDimCandidateBenchmarkEntry:
    """Evaluate one braid example through the sl2 3-dimensional candidate branch."""

    result = compute_sl2_3d_candidate_output(example.to_braid_word(), q=q)
    return Sl2ThreeDimCandidateBenchmarkEntry(
        example_label=example.label,
        result=result,
        notes=example.notes,
        metadata={
            "expected_components": example.expected_components,
            "expected_crossing_count": example.expected_crossing_count,
            "example_metadata": dict(example.metadata),
        },
    )


def evaluate_sl2_3d_candidate_examples(
    examples: Iterable[BraidExample],
    *,
    q: sp.Expr | None = None,
) -> list[Sl2ThreeDimCandidateBenchmarkEntry]:
    """Evaluate a list of examples through the sl2 3-dimensional candidate branch."""

    return [evaluate_sl2_3d_candidate_example(example, q=q) for example in examples]


def evaluate_default_sl2_3d_candidate_benchmark(
    *,
    q: sp.Expr | None = None,
) -> list[Sl2ThreeDimCandidateBenchmarkEntry]:
    """Evaluate the default candidate benchmark set: unknot_1, trefoil, figure_eight."""

    return evaluate_sl2_3d_candidate_examples(
        (get_braid_example(label) for label in DEFAULT_SL2_3D_CANDIDATE_BENCHMARK_LABELS),
        q=q,
    )