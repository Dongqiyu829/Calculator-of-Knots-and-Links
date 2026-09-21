"""Unified branch-level result objects for the current invariant program skeleton."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import sympy as sp

from src.braid.braid_word import BraidWord


@dataclass(frozen=True, slots=True)
class InvariantBranchResult:
    """Store one branch evaluation in a uniform program-facing structure."""

    branch_id: str
    representation_name: str
    braid_word: BraidWord
    status: str
    raw_trace: sp.Expr | None
    primary_output: sp.Expr | None
    primary_output_label: str
    normalization_label: str
    variable_convention: str
    notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def display_name(self) -> str:
        """Return the preferred user-facing branch name."""

        value = self.metadata.get("user_facing_branch_name")
        return self.branch_id if value is None else str(value)

    def summary(self) -> str:
        lines = [
            f"Branch: {self.display_name}",
            f"Representation: {self.representation_name}",
            f"Braid word: {self.braid_word.word_string()}",
            f"Status: {self.status}",
            "Raw trace: not available"
            if self.raw_trace is None
            else f"Raw trace: {sp.simplify(self.raw_trace)}",
            f"Primary output label: {self.primary_output_label}",
            "Primary output: not available"
            if self.primary_output is None
            else f"Primary output: {sp.simplify(self.primary_output)}",
            f"Normalization label: {self.normalization_label}",
            f"Variable convention: {self.variable_convention}",
        ]
        if self.notes:
            lines.append(f"Notes: {self.notes}")
        if self.metadata:
            lines.append(f"Metadata: {self.metadata}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        return {
            "branch_id": self.branch_id,
            "display_name": self.display_name,
            "representation_name": self.representation_name,
            "braid_word": self.braid_word.to_dict(),
            "status": self.status,
            "raw_trace": None if self.raw_trace is None else str(sp.simplify(self.raw_trace)),
            "primary_output": None if self.primary_output is None else str(sp.simplify(self.primary_output)),
            "primary_output_label": self.primary_output_label,
            "normalization_label": self.normalization_label,
            "variable_convention": self.variable_convention,
            "notes": self.notes,
            "metadata": dict(self.metadata),
        }

    def to_string(self) -> str:
        return self.summary()