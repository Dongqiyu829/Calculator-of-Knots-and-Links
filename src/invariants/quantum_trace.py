"""Raw closure-trace computations for the current MVP stage."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import sympy as sp

from src.braid.braid_operator import BraidOperatorData

from .polynomial_result import InvariantResult


@dataclass(frozen=True, slots=True)
class BraidClosureData:
    """Represent the basic closure of a braid operator before normalization.

    Notes
    -----
    This object does not yet implement a ribbon or Markov normalization. It
    only records that we are interpreting the braid operator via ordinary trace
    under the standard braid-closure picture.
    """

    braid_operator: BraidOperatorData
    closure_type: str
    closure_notes: str
    convention_notes: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def summary(self) -> str:
        """Return a human-readable summary of the closure interpretation."""

        lines = [
            f"Closure type: {self.closure_type}",
            f"Braid word: {self.braid_operator.braid_word.word_string()}",
            f"Number of strands: {self.braid_operator.num_strands}",
            f"Writhe: {self.braid_operator.writhe}",
            f"Operator dimension: {self.braid_operator.total_dimension}",
            f"Closure notes: {self.closure_notes}",
            f"Convention notes: {self.convention_notes}",
        ]
        if self.metadata:
            lines.append(f"Metadata: {self.metadata}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Return a structured representation suitable for serialization."""

        return {
            "closure_type": self.closure_type,
            "braid_word": self.braid_operator.braid_word.to_dict(),
            "num_strands": self.braid_operator.num_strands,
            "writhe": self.braid_operator.writhe,
            "operator_dimension": self.braid_operator.total_dimension,
            "closure_notes": self.closure_notes,
            "convention_notes": self.convention_notes,
            "metadata": dict(self.metadata),
        }

    def to_string(self) -> str:
        """Return a string form aligned with the summary output."""

        return self.summary()


def make_braid_closure_data(braid_operator: BraidOperatorData) -> BraidClosureData:
    """Build the current MVP closure descriptor from a braid operator."""

    return BraidClosureData(
        braid_operator=braid_operator,
        closure_type="ordinary braid closure",
        closure_notes=(
            "The current closure layer interprets the braid by ordinary matrix trace of the global braid operator."
        ),
        convention_notes=(
            "This is a raw closure model only. No Markov normalization, ribbon correction, or quantum trace "
            "correction has been applied."
        ),
        metadata={
            "trace_mode": "ordinary_trace",
            "normalized": False,
        },
    )


def compute_raw_closure_trace(braid_operator: BraidOperatorData) -> InvariantResult:
    """Compute the ordinary trace of the global braid operator.

    Parameters
    ----------
    braid_operator:
        Global braid operator constructed from a braid word and local braiding
        data.

    Returns
    -------
    InvariantResult
        Result object labeled explicitly as a raw closure trace.
    """

    closure_data = make_braid_closure_data(braid_operator)
    raw_expression = sp.simplify(sp.trace(braid_operator.operator))

    return InvariantResult(
        representation=braid_operator.rmatrix.rep,
        braid_word=braid_operator.braid_word,
        operator_dimension=braid_operator.total_dimension,
        raw_closure_trace=raw_expression,
        eyb_normalized_expression=None,
        future_rt_quantum_trace_expression=None,
        trace_mode="ordinary_trace",
        convention_notes=(
            "Current result is the ordinary trace of the global braid operator. "
            "It is not yet a standard Jones, HOMFLY, or Kauffman polynomial. "
            "No Markov normalization or ribbon/quantum-trace correction has been applied."
        ),
        framing_notes=(
            "This raw closure trace may differ from standard literature invariants by overall factors, "
            "variable substitutions, and framing-dependent corrections."
        ),
        metadata={
            "closure": closure_data.to_dict(),
            "operator_shape": list(braid_operator.operator.shape),
            "operator_summary": braid_operator.to_dict(),
        },
    )

