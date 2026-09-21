"""Structured invariant result objects for raw and future normalized outputs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import sympy as sp

from src.algebra.representations import RepresentationSpec
from src.braid.braid_word import BraidWord


@dataclass(frozen=True, slots=True)
class InvariantResult:
    """Store a raw or normalized invariant expression together with conventions.

    Notes
    -----
    In the current MVP this object is used for the raw closure trace only.
    normalized_expression is intentionally left as None until a consistent
    normalization convention is implemented.
    """

    representation: RepresentationSpec
    braid_word: BraidWord
    operator_dimension: int
    raw_closure_trace: sp.Expr | None
    eyb_normalized_expression: sp.Expr | None
    future_rt_quantum_trace_expression: sp.Expr | None
    trace_mode: str
    convention_notes: str
    framing_notes: str
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def raw_expression(self) -> sp.Expr | None:
        """Backward-compatible alias for the raw closure trace."""

        return self.raw_closure_trace

    @property
    def normalized_expression(self) -> sp.Expr | None:
        """Backward-compatible alias for the EYB-normalized expression."""

        return self.eyb_normalized_expression

    def summary(self) -> str:
        """Return a human-readable summary of the invariant result."""

        lines = [
            f"Representation: {self.representation.name()}",
            f"Braid word: {self.braid_word.word_string()}",
            f"Number of strands: {self.braid_word.num_strands}",
            f"Writhe: {self.braid_word.writhe()}",
            f"Operator dimension: {self.operator_dimension}",
            f"Trace mode: {self.trace_mode}",
            "Raw closure trace: not available"
            if self.raw_closure_trace is None
            else f"Raw closure trace: {sp.simplify(self.raw_closure_trace)}",
            "EYB-normalized expression: not yet implemented"
            if self.eyb_normalized_expression is None
            else f"EYB-normalized expression: {sp.simplify(self.eyb_normalized_expression)}",
            "Future RT quantum-trace expression: not yet implemented"
            if self.future_rt_quantum_trace_expression is None
            else (
                "Future RT quantum-trace expression: "
                f"{sp.simplify(self.future_rt_quantum_trace_expression)}"
            ),
            f"Convention notes: {self.convention_notes}",
            f"Framing notes: {self.framing_notes}",
        ]
        if self.metadata:
            lines.append(f"Metadata: {self.metadata}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Return a structured representation suitable for serialization."""

        return {
            "representation": self.representation.to_dict(),
            "braid_word": self.braid_word.to_dict(),
            "operator_dimension": self.operator_dimension,
            "raw_closure_trace": None
            if self.raw_closure_trace is None
            else str(sp.simplify(self.raw_closure_trace)),
            "eyb_normalized_expression": None
            if self.eyb_normalized_expression is None
            else str(sp.simplify(self.eyb_normalized_expression)),
            "future_rt_quantum_trace_expression": None
            if self.future_rt_quantum_trace_expression is None
            else str(sp.simplify(self.future_rt_quantum_trace_expression)),
            "raw_expression": None
            if self.raw_closure_trace is None
            else str(sp.simplify(self.raw_closure_trace)),
            "normalized_expression": None
            if self.eyb_normalized_expression is None
            else str(sp.simplify(self.eyb_normalized_expression)),
            "trace_mode": self.trace_mode,
            "convention_notes": self.convention_notes,
            "framing_notes": self.framing_notes,
            "metadata": dict(self.metadata),
        }

    def to_string(self) -> str:
        """Return a string form aligned with the summary output."""

        return self.summary()
