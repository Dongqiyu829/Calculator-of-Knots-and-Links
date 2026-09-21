"""Benchmark helpers for evaluating catalog examples across multiple invariant branches."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

import sympy as sp

from src.catalog.braid_examples import BraidExample

from .branch_registry import evaluate_all_current_branches
from .branch_results import InvariantBranchResult


@dataclass(frozen=True, slots=True)
class MultiBranchBenchmarkEntry:
    """Store one catalog example evaluated across the current invariant branches."""

    example_label: str
    branch_results: tuple[InvariantBranchResult, ...]
    notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def summary(self) -> str:
        lines = [f"Example label: {self.example_label}"]
        if self.notes:
            lines.append(f"Notes: {self.notes}")
        if self.metadata:
            lines.append(f"Metadata: {self.metadata}")
        lines.append("Branch results:")
        for branch_result in self.branch_results:
            lines.append(f"  - {branch_result.display_name}: {branch_result.primary_output_label}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        return {
            "example_label": self.example_label,
            "branch_results": [item.to_dict() for item in self.branch_results],
            "notes": self.notes,
            "metadata": dict(self.metadata),
        }

    def to_string(self) -> str:
        return self.summary()


def evaluate_example_across_branches(
    example: BraidExample,
    *,
    q: sp.Expr | None = None,
) -> MultiBranchBenchmarkEntry:
    """Evaluate one catalog example across the current three branch families."""

    return MultiBranchBenchmarkEntry(
        example_label=example.label,
        branch_results=tuple(evaluate_all_current_branches(example, q=q)),
        notes=example.notes,
        metadata={
            "expected_components": example.expected_components,
            "expected_crossing_count": example.expected_crossing_count,
            "example_metadata": dict(example.metadata),
        },
    )


def evaluate_catalog_across_branches(
    examples: Iterable[BraidExample],
    *,
    q: sp.Expr | None = None,
) -> list[MultiBranchBenchmarkEntry]:
    """Evaluate a catalog slice across all current invariant branches."""

    return [evaluate_example_across_branches(example, q=q) for example in examples]