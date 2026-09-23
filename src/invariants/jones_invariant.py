"""Formal sl2 fundamental reduced-P2 and Jones-compatible output layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any

import sympy as sp

from src.braid.braid_operator import BraidOperatorBuilder, BraidOperatorData
from src.braid.braid_word import BraidWord
from src.rmatrix.sl2_rmatrix import build_sl2_fundamental_rmatrix

from .eyb_invariant import build_sl2_fundamental_eyb_data, compute_eyb_invariant
from .quantum_trace import compute_raw_closure_trace


DEFAULT_JONES_VARIABLE_CONVENTION = "Default comparison convention is t = q^-2."


@dataclass(frozen=True, slots=True)
class JonesInvariantResult:
    """Store the current formal sl2 reduced-P2 / Jones-compatible output data."""

    representation_name: str
    braid_word: BraidWord
    raw_trace: sp.Expr
    unreduced_p2_output: sp.Expr
    unknot_normalization: sp.Expr
    reduced_p2_output: sp.Expr
    jones_compatible_output: sp.Expr
    variable_convention: str
    notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def summary(self) -> str:
        lines = [
            f"Representation: {self.representation_name}",
            f"Braid word: {self.braid_word.word_string()}",
            f"Raw trace: {sp.simplify(self.raw_trace)}",
            f"Unreduced P2 output: {sp.simplify(self.unreduced_p2_output)}",
            f"Unknot normalization: {sp.simplify(self.unknot_normalization)}",
            f"Reduced P2 output: {sp.simplify(self.reduced_p2_output)}",
            f"Jones-compatible output: {sp.simplify(self.jones_compatible_output)}",
            f"Variable convention: {self.variable_convention}",
        ]
        if self.notes:
            lines.append(f"Notes: {self.notes}")
        if self.metadata:
            lines.append(f"Metadata: {self.metadata}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        return {
            "representation_name": self.representation_name,
            "braid_word": self.braid_word.to_dict(),
            "raw_trace": str(sp.simplify(self.raw_trace)),
            "unreduced_p2_output": str(sp.simplify(self.unreduced_p2_output)),
            "unknot_normalization": str(sp.simplify(self.unknot_normalization)),
            "reduced_p2_output": str(sp.simplify(self.reduced_p2_output)),
            "jones_compatible_output": str(sp.simplify(self.jones_compatible_output)),
            "variable_convention": self.variable_convention,
            "notes": self.notes,
            "metadata": dict(self.metadata),
        }

    def to_string(self) -> str:
        return self.summary()


def _coerce_sl2_operator_data(
    braid: BraidWord | BraidOperatorData,
    *,
    q: sp.Expr,
) -> BraidOperatorData:
    if isinstance(braid, BraidOperatorData):
        return braid
    rmatrix = build_sl2_fundamental_rmatrix(q)
    return BraidOperatorBuilder(braid_word=braid, rmatrix=rmatrix).build()


def current_sl2_unknot_normalization(q: sp.Expr | None = None) -> sp.Expr:
    """Return the current unreduced P2-type value on the 1-strand unknot."""

    parameter = q if q is not None else sp.Symbol("q", nonzero=True)
    return _sl2_unknot_scalar(parameter)


@lru_cache(maxsize=64)
def _sl2_unknot_scalar(q: sp.Expr) -> sp.Expr:
    # The one-strand identity has rho = I, writhe = 0, beta = 1; its
    # unreduced EYB value is exactly Tr(mu), with no local R construction.
    return sp.simplify(sp.trace(build_sl2_fundamental_eyb_data(q).mu))


def compute_sl2_reduced_p2(
    braid: BraidWord | BraidOperatorData,
    *,
    q: sp.Expr | None = None,
) -> tuple[sp.Expr, sp.Expr, sp.Expr]:
    """Return unreduced P2, unknot normalization, and reduced P2 for sl2 fundamental."""

    parameter = q if q is not None else sp.Symbol("q", nonzero=True)
    operator_data = _coerce_sl2_operator_data(braid, q=parameter)
    invariant_result = compute_eyb_invariant(operator_data, eyb_data=build_sl2_fundamental_eyb_data(parameter))
    unreduced_p2 = sp.simplify(invariant_result.eyb_normalized_expression)
    unknot_normalization = current_sl2_unknot_normalization(parameter)
    reduced_p2 = sp.simplify(unreduced_p2 / unknot_normalization)
    return unreduced_p2, unknot_normalization, reduced_p2


def compute_sl2_jones_compatible_output(
    braid: BraidWord | BraidOperatorData,
    *,
    q: sp.Expr | None = None,
) -> JonesInvariantResult:
    """Return the current formal sl2 Jones-compatible output layer.

    The current project convention is: take the sl2 fundamental current P2-type
    EYB output and reduce it by the current unknot value. This is the formal
    Jones-compatible layer in the present codebase.
    """

    parameter = q if q is not None else sp.Symbol("q", nonzero=True)
    operator_data = _coerce_sl2_operator_data(braid, q=parameter)
    raw_result = compute_raw_closure_trace(operator_data)
    unreduced_p2, unknot_normalization, reduced_p2 = compute_sl2_reduced_p2(operator_data, q=parameter)

    return JonesInvariantResult(
        representation_name=operator_data.rmatrix.rep.name(),
        braid_word=operator_data.braid_word,
        raw_trace=sp.simplify(raw_result.raw_closure_trace),
        unreduced_p2_output=unreduced_p2,
        unknot_normalization=unknot_normalization,
        reduced_p2_output=reduced_p2,
        jones_compatible_output=reduced_p2,
        variable_convention=DEFAULT_JONES_VARIABLE_CONVENTION,
        notes=(
            "This formal layer keeps the current braid-side EYB pipeline intact and exposes its reduced sl2 "
            "fundamental output as the project's Jones-compatible branch."
        ),
        metadata={
            "branch": "sl2 fundamental",
            "normalization_kind": "current P2 reduced by current unknot value",
            "unknot_example_label": "unknot_1",
        },
    )
