"""Empirical Markov-move regression checks for current invariant layers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

import sympy as sp

from src.braid.braid_operator import BraidOperatorBuilder
from src.braid.braid_word import BraidWord
from src.rmatrix.rmatrix_base import RMatrixData

from .eyb_invariant import EYBData, compute_eyb_invariant
from .polynomial_result import InvariantResult
from .quantum_trace import compute_raw_closure_trace


RMatrixBuilder = Callable[[sp.Expr | None], RMatrixData]
EYBBuilder = Callable[[sp.Expr | None], EYBData]


def _expressions_match(left: sp.Expr | None, right: sp.Expr | None) -> bool | None:
    """Return symbolic equality information for two expressions."""

    if left is None or right is None:
        return None
    return sp.simplify(left - right) == 0


def _invert_generators(generators: tuple[int, ...]) -> tuple[int, ...]:
    """Return the inverse Artin word by reversing order and sign."""

    return tuple(-generator for generator in reversed(generators))


def _evaluate_invariant_result(
    braid_word: BraidWord,
    *,
    rmatrix_builder: RMatrixBuilder,
    eyb_builder: EYBBuilder | None = None,
    q: sp.Expr | None = None,
) -> InvariantResult:
    """Evaluate the current raw or EYB-aware invariant pipeline on one braid word."""

    parameter = q if q is not None else sp.Symbol("q", nonzero=True)
    rmatrix = rmatrix_builder(parameter)
    operator_data = BraidOperatorBuilder(braid_word=braid_word, rmatrix=rmatrix).build()
    if eyb_builder is None:
        return compute_raw_closure_trace(operator_data)
    eyb_data = eyb_builder(parameter)
    return compute_eyb_invariant(operator_data, eyb_data=eyb_data)


@dataclass(frozen=True, slots=True)
class ExpressionComparison:
    """Store two expressions and whether they match symbolically."""

    left_label: str
    right_label: str
    left_expression: sp.Expr | None
    right_expression: sp.Expr | None
    matches: bool | None
    notes: str = ""

    def summary(self) -> str:
        """Return a human-readable summary of the comparison."""

        lines = [
            f"Left label: {self.left_label}",
            f"Right label: {self.right_label}",
            "Left expression: unavailable"
            if self.left_expression is None
            else f"Left expression: {sp.simplify(self.left_expression)}",
            "Right expression: unavailable"
            if self.right_expression is None
            else f"Right expression: {sp.simplify(self.right_expression)}",
            f"Matches: {self.matches}",
        ]
        if self.notes:
            lines.append(f"Notes: {self.notes}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Return a structured representation suitable for serialization."""

        return {
            "left_label": self.left_label,
            "right_label": self.right_label,
            "left_expression": None if self.left_expression is None else str(sp.simplify(self.left_expression)),
            "right_expression": None if self.right_expression is None else str(sp.simplify(self.right_expression)),
            "matches": self.matches,
            "notes": self.notes,
        }

    def to_string(self) -> str:
        """Return a string form aligned with the summary output."""

        return self.summary()


@dataclass(frozen=True, slots=True)
class ConjugationCheckResult:
    """Store one empirical conjugation-regression check."""

    representation_name: str
    original_braid: BraidWord
    conjugator_braid: BraidWord
    conjugated_braid: BraidWord
    raw_trace_comparison: ExpressionComparison
    eyb_comparison: ExpressionComparison
    notes: str = ""

    def summary(self) -> str:
        """Return a human-readable summary of the conjugation check."""

        lines = [
            f"Representation: {self.representation_name}",
            f"Original braid: {self.original_braid.word_string()}",
            f"Conjugator: {self.conjugator_braid.word_string()}",
            f"Conjugated braid: {self.conjugated_braid.word_string()}",
            f"Raw closure trace invariant: {self.raw_trace_comparison.matches}",
            f"EYB-normalized invariant: {self.eyb_comparison.matches}",
        ]
        if self.notes:
            lines.append(f"Notes: {self.notes}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Return a structured representation suitable for serialization."""

        return {
            "representation_name": self.representation_name,
            "original_braid": self.original_braid.to_dict(),
            "conjugator_braid": self.conjugator_braid.to_dict(),
            "conjugated_braid": self.conjugated_braid.to_dict(),
            "raw_trace_comparison": self.raw_trace_comparison.to_dict(),
            "eyb_comparison": self.eyb_comparison.to_dict(),
            "notes": self.notes,
        }

    def to_string(self) -> str:
        """Return a string form aligned with the summary output."""

        return self.summary()


@dataclass(frozen=True, slots=True)
class StabilizationCheckResult:
    """Store one empirical stabilization-regression check."""

    representation_name: str
    original_braid: BraidWord
    positive_stabilized_braid: BraidWord
    negative_stabilized_braid: BraidWord
    raw_positive_comparison: ExpressionComparison
    raw_negative_comparison: ExpressionComparison
    eyb_positive_comparison: ExpressionComparison
    eyb_negative_comparison: ExpressionComparison
    notes: str = ""

    def summary(self) -> str:
        """Return a human-readable summary of the stabilization check."""

        lines = [
            f"Representation: {self.representation_name}",
            f"Original braid: {self.original_braid.word_string()}",
            f"Positive stabilization: {self.positive_stabilized_braid.word_string()}",
            f"Negative stabilization: {self.negative_stabilized_braid.word_string()}",
            f"Raw trace invariant under positive stabilization: {self.raw_positive_comparison.matches}",
            f"Raw trace invariant under negative stabilization: {self.raw_negative_comparison.matches}",
            f"EYB invariant under positive stabilization: {self.eyb_positive_comparison.matches}",
            f"EYB invariant under negative stabilization: {self.eyb_negative_comparison.matches}",
        ]
        if self.notes:
            lines.append(f"Notes: {self.notes}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Return a structured representation suitable for serialization."""

        return {
            "representation_name": self.representation_name,
            "original_braid": self.original_braid.to_dict(),
            "positive_stabilized_braid": self.positive_stabilized_braid.to_dict(),
            "negative_stabilized_braid": self.negative_stabilized_braid.to_dict(),
            "raw_positive_comparison": self.raw_positive_comparison.to_dict(),
            "raw_negative_comparison": self.raw_negative_comparison.to_dict(),
            "eyb_positive_comparison": self.eyb_positive_comparison.to_dict(),
            "eyb_negative_comparison": self.eyb_negative_comparison.to_dict(),
            "notes": self.notes,
        }

    def to_string(self) -> str:
        """Return a string form aligned with the summary output."""

        return self.summary()


@dataclass(frozen=True, slots=True)
class MarkovCheckBundle:
    """Store the empirical Markov regression checks attached to one benchmark entry."""

    representation_name: str
    conjugation: ConjugationCheckResult | None = None
    stabilization: StabilizationCheckResult | None = None
    notes: str = ""

    def summary(self) -> str:
        """Return a readable summary of the bundle."""

        lines = [f"Representation: {self.representation_name}"]
        if self.conjugation is None:
            lines.append("Conjugation check: not included")
        else:
            lines.append(f"Conjugation raw invariant: {self.conjugation.raw_trace_comparison.matches}")
            lines.append(f"Conjugation EYB invariant: {self.conjugation.eyb_comparison.matches}")
        if self.stabilization is None:
            lines.append("Stabilization check: not included")
        else:
            lines.append(
                f"Stabilization raw invariance: (+){self.stabilization.raw_positive_comparison.matches}, "
                f"(-){self.stabilization.raw_negative_comparison.matches}"
            )
            lines.append(
                f"Stabilization EYB invariance: (+){self.stabilization.eyb_positive_comparison.matches}, "
                f"(-){self.stabilization.eyb_negative_comparison.matches}"
            )
        if self.notes:
            lines.append(f"Notes: {self.notes}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Return a structured representation suitable for serialization."""

        return {
            "representation_name": self.representation_name,
            "conjugation": None if self.conjugation is None else self.conjugation.to_dict(),
            "stabilization": None if self.stabilization is None else self.stabilization.to_dict(),
            "notes": self.notes,
        }

    def to_string(self) -> str:
        """Return a string form aligned with the summary output."""

        return self.summary()


def default_conjugator_generators(num_strands: int) -> tuple[int, ...]:
    """Return a small default conjugator word for empirical checks."""

    if num_strands <= 1:
        return ()
    if num_strands == 2:
        return (1,)
    return (1, 2)


def conjugate_braid_word(beta: BraidWord, eta_generators: tuple[int, ...] | list[int]) -> tuple[BraidWord, BraidWord]:
    """Return the conjugator braid and the conjugated braid word eta beta eta^-1."""

    eta_tuple = tuple(eta_generators)
    conjugator = BraidWord.from_iterable(
        num_strands=beta.num_strands,
        generators=eta_tuple,
        label=f"{beta.label or 'braid'} conjugator",
        notes="Small Artin word used for the empirical conjugation regression check.",
    )
    conjugated = BraidWord.from_iterable(
        num_strands=beta.num_strands,
        generators=eta_tuple + beta.generators + _invert_generators(eta_tuple),
        label=f"conj({beta.label or 'braid'})",
        notes="Conjugated braid word eta beta eta^-1 used for the Markov conjugation regression check.",
    )
    return conjugator, conjugated


def stabilize_braid_word(beta: BraidWord, *, positive: bool) -> BraidWord:
    """Return the positive or negative Markov stabilization of beta."""

    generator = beta.num_strands if positive else -beta.num_strands
    sign_label = "positive" if positive else "negative"
    return BraidWord.from_iterable(
        num_strands=beta.num_strands + 1,
        generators=beta.generators + (generator,),
        label=f"{beta.label or 'braid'} {sign_label} stabilization",
        notes=(
            "Empirical Markov stabilization word formed by reinterpreting beta in B_(n+1) and appending sigma_n"
            if positive
            else "Empirical Markov stabilization word formed by reinterpreting beta in B_(n+1) and appending sigma_n^-1"
        ),
    )


def check_conjugation_invariance(
    beta: BraidWord,
    *,
    eta_generators: tuple[int, ...] | list[int] | None,
    rmatrix_builder: RMatrixBuilder,
    eyb_builder: EYBBuilder | None = None,
    q: sp.Expr | None = None,
) -> ConjugationCheckResult:
    """Empirically compare beta and eta beta eta^-1 on the current invariant layers."""

    eta_tuple = default_conjugator_generators(beta.num_strands) if eta_generators is None else tuple(eta_generators)
    conjugator, conjugated = conjugate_braid_word(beta, eta_tuple)
    original_result = _evaluate_invariant_result(beta, rmatrix_builder=rmatrix_builder, eyb_builder=eyb_builder, q=q)
    conjugated_result = _evaluate_invariant_result(
        conjugated,
        rmatrix_builder=rmatrix_builder,
        eyb_builder=eyb_builder,
        q=q,
    )
    representation_name = original_result.representation.name()

    raw_comparison = ExpressionComparison(
        left_label="beta raw closure trace",
        right_label="eta beta eta^-1 raw closure trace",
        left_expression=original_result.raw_closure_trace,
        right_expression=conjugated_result.raw_closure_trace,
        matches=_expressions_match(original_result.raw_closure_trace, conjugated_result.raw_closure_trace),
        notes="Ordinary trace is expected to stay unchanged under conjugation because the braid operator is conjugated by similarity.",
    )
    eyb_comparison = ExpressionComparison(
        left_label="beta EYB-normalized expression",
        right_label="eta beta eta^-1 EYB-normalized expression",
        left_expression=original_result.eyb_normalized_expression,
        right_expression=conjugated_result.eyb_normalized_expression,
        matches=_expressions_match(
            original_result.eyb_normalized_expression,
            conjugated_result.eyb_normalized_expression,
        ),
        notes="The EYB-normalized output should also remain unchanged under conjugation in a correct implementation.",
    )
    return ConjugationCheckResult(
        representation_name=representation_name,
        original_braid=beta,
        conjugator_braid=conjugator,
        conjugated_braid=conjugated,
        raw_trace_comparison=raw_comparison,
        eyb_comparison=eyb_comparison,
        notes="This is an empirical regression check, not a formal proof of Markov conjugation invariance.",
    )


def check_stabilization_invariance(
    beta: BraidWord,
    *,
    rmatrix_builder: RMatrixBuilder,
    eyb_builder: EYBBuilder,
    q: sp.Expr | None = None,
) -> StabilizationCheckResult:
    """Empirically compare beta with its positive and negative Markov stabilizations."""

    original_result = _evaluate_invariant_result(beta, rmatrix_builder=rmatrix_builder, eyb_builder=eyb_builder, q=q)
    positive_braid = stabilize_braid_word(beta, positive=True)
    negative_braid = stabilize_braid_word(beta, positive=False)
    positive_result = _evaluate_invariant_result(
        positive_braid,
        rmatrix_builder=rmatrix_builder,
        eyb_builder=eyb_builder,
        q=q,
    )
    negative_result = _evaluate_invariant_result(
        negative_braid,
        rmatrix_builder=rmatrix_builder,
        eyb_builder=eyb_builder,
        q=q,
    )
    representation_name = original_result.representation.name()

    return StabilizationCheckResult(
        representation_name=representation_name,
        original_braid=beta,
        positive_stabilized_braid=positive_braid,
        negative_stabilized_braid=negative_braid,
        raw_positive_comparison=ExpressionComparison(
            left_label="beta raw closure trace",
            right_label="beta sigma_n raw closure trace",
            left_expression=original_result.raw_closure_trace,
            right_expression=positive_result.raw_closure_trace,
            matches=_expressions_match(original_result.raw_closure_trace, positive_result.raw_closure_trace),
            notes="Raw closure trace is recorded here for regression visibility and is not expected to be Markov invariant in general.",
        ),
        raw_negative_comparison=ExpressionComparison(
            left_label="beta raw closure trace",
            right_label="beta sigma_n^-1 raw closure trace",
            left_expression=original_result.raw_closure_trace,
            right_expression=negative_result.raw_closure_trace,
            matches=_expressions_match(original_result.raw_closure_trace, negative_result.raw_closure_trace),
            notes="Raw closure trace is recorded here for regression visibility and is not expected to be Markov invariant in general.",
        ),
        eyb_positive_comparison=ExpressionComparison(
            left_label="beta EYB-normalized expression",
            right_label="beta sigma_n EYB-normalized expression",
            left_expression=original_result.eyb_normalized_expression,
            right_expression=positive_result.eyb_normalized_expression,
            matches=_expressions_match(
                original_result.eyb_normalized_expression,
                positive_result.eyb_normalized_expression,
            ),
            notes="This is the main positive-stabilization regression target for the current A-type fundamental EYB implementation.",
        ),
        eyb_negative_comparison=ExpressionComparison(
            left_label="beta EYB-normalized expression",
            right_label="beta sigma_n^-1 EYB-normalized expression",
            left_expression=original_result.eyb_normalized_expression,
            right_expression=negative_result.eyb_normalized_expression,
            matches=_expressions_match(
                original_result.eyb_normalized_expression,
                negative_result.eyb_normalized_expression,
            ),
            notes="This is the main negative-stabilization regression target for the current A-type fundamental EYB implementation.",
        ),
        notes="This is an empirical regression check, not a formal proof of Markov stabilization invariance.",
    )