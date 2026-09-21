"""Legacy fast multibranch benchmark helpers preserved alongside the newer candidate pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

import sympy as sp

from src.catalog.braid_examples import BraidExample

from .branch_results import InvariantBranchResult
from .legacy_branch_registry import evaluate_all_legacy_branches


@dataclass(frozen=True, slots=True)
class LegacyMultiBranchBenchmarkEntry:
    """Store one catalog example evaluated across the preserved legacy branch set."""

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


def evaluate_legacy_example_across_branches(
    example: BraidExample,
    *,
    q: sp.Expr | None = None,
) -> LegacyMultiBranchBenchmarkEntry:
    """Evaluate one catalog example across the preserved legacy branch set."""

    return LegacyMultiBranchBenchmarkEntry(
        example_label=example.label,
        branch_results=tuple(evaluate_all_legacy_branches(example, q=q)),
        notes=example.notes,
        metadata={
            "expected_components": example.expected_components,
            "expected_crossing_count": example.expected_crossing_count,
            "example_metadata": dict(example.metadata),
            "program_mode": "legacy_fast",
        },
    )


def evaluate_legacy_catalog_across_branches(
    examples: Iterable[BraidExample],
    *,
    q: sp.Expr | None = None,
) -> list[LegacyMultiBranchBenchmarkEntry]:
    """Evaluate a catalog slice across the preserved legacy branch set."""

    return [evaluate_legacy_example_across_branches(example, q=q) for example in examples]