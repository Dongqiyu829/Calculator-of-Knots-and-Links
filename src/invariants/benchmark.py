"""Benchmark evaluation helpers for catalog-based braid experiments."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable

import sympy as sp

from src.braid.braid_operator import BraidOperatorBuilder
from src.braid.braid_word import BraidWord
from src.catalog.braid_examples import BraidExample
from src.rmatrix.rmatrix_base import RMatrixData

from .eyb_invariant import EYBData, compute_eyb_invariant
from .polynomial_result import InvariantResult
from .quantum_trace import compute_raw_closure_trace


RMatrixBuilder = Callable[[sp.Expr | None], RMatrixData]
EYBBuilder = Callable[[sp.Expr | None], EYBData]


@dataclass(frozen=True, slots=True)
class BenchmarkEntry:
    """Store one standardized benchmark result entry."""

    example_label: str
    representation_name: str
    braid_word: BraidWord
    raw_closure_trace: sp.Expr | None
    eyb_normalized_expression: sp.Expr | None
    trace_mode: str
    convention_notes: str
    framing_notes: str
    markov_checks: dict[str, Any] = field(default_factory=dict)
    notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def summary(self) -> str:
        """Return a human-readable summary of the benchmark result."""

        lines = [
            f"Example label: {self.example_label}",
            f"Representation: {self.representation_name}",
            f"Braid word: {self.braid_word.word_string()}",
            "Raw closure trace: not available"
            if self.raw_closure_trace is None
            else f"Raw closure trace: {sp.simplify(self.raw_closure_trace)}",
            "EYB-normalized expression: not available"
            if self.eyb_normalized_expression is None
            else f"EYB-normalized expression: {sp.simplify(self.eyb_normalized_expression)}",
            f"Trace mode: {self.trace_mode}",
            f"Convention notes: {self.convention_notes}",
            f"Framing notes: {self.framing_notes}",
        ]
        if self.markov_checks:
            lines.append(f"Markov checks: {self.markov_checks}")
        if self.notes:
            lines.append(f"Notes: {self.notes}")
        if self.metadata:
            lines.append(f"Metadata: {self.metadata}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Return a structured representation suitable for serialization."""

        return {
            "example_label": self.example_label,
            "representation_name": self.representation_name,
            "braid_word": self.braid_word.to_dict(),
            "raw_closure_trace": None
            if self.raw_closure_trace is None
            else str(sp.simplify(self.raw_closure_trace)),
            "eyb_normalized_expression": None
            if self.eyb_normalized_expression is None
            else str(sp.simplify(self.eyb_normalized_expression)),
            "trace_mode": self.trace_mode,
            "convention_notes": self.convention_notes,
            "framing_notes": self.framing_notes,
            "markov_checks": dict(self.markov_checks),
            "notes": self.notes,
            "metadata": dict(self.metadata),
        }

    def to_string(self) -> str:
        """Return a string form aligned with the summary output."""

        return self.summary()


def _compute_invariant_result(
    braid_word: BraidWord,
    *,
    rmatrix_builder: RMatrixBuilder,
    eyb_builder: EYBBuilder | None = None,
    q: sp.Expr | None = None,
) -> InvariantResult:
    """Run the current invariant pipeline on a braid word."""

    parameter = q if q is not None else sp.Symbol("q", nonzero=True)
    rmatrix = rmatrix_builder(parameter)
    operator_data = BraidOperatorBuilder(braid_word=braid_word, rmatrix=rmatrix).build()
    if eyb_builder is None:
        return compute_raw_closure_trace(operator_data)
    eyb_data = eyb_builder(parameter)
    return compute_eyb_invariant(operator_data, eyb_data=eyb_data)


def evaluate_braid_example(
    example: BraidExample,
    *,
    rmatrix_builder: RMatrixBuilder,
    eyb_builder: EYBBuilder | None = None,
    q: sp.Expr | None = None,
    include_markov_checks: bool = False,
    conjugator_generators: tuple[int, ...] | list[int] | None = None,
) -> BenchmarkEntry:
    """Evaluate one catalog example on one local model and optional EYB layer."""

    braid_word = example.to_braid_word()
    invariant_result = _compute_invariant_result(
        braid_word,
        rmatrix_builder=rmatrix_builder,
        eyb_builder=eyb_builder,
        q=q,
    )
    markov_data: dict[str, Any] = {}
    if include_markov_checks:
        from .markov_checks import (
            MarkovCheckBundle,
            check_conjugation_invariance,
            check_stabilization_invariance,
        )

        conjugation = check_conjugation_invariance(
            braid_word,
            eta_generators=conjugator_generators,
            rmatrix_builder=rmatrix_builder,
            eyb_builder=eyb_builder,
            q=q,
        )
        stabilization = None
        if eyb_builder is not None:
            stabilization = check_stabilization_invariance(
                braid_word,
                rmatrix_builder=rmatrix_builder,
                eyb_builder=eyb_builder,
                q=q,
            )
        bundle = MarkovCheckBundle(
            representation_name=invariant_result.representation.name(),
            conjugation=conjugation,
            stabilization=stabilization,
            notes="Empirical Markov regression checks attached to this benchmark entry.",
        )
        markov_data = bundle.to_dict()

    return BenchmarkEntry(
        example_label=example.label,
        representation_name=invariant_result.representation.name(),
        braid_word=braid_word,
        raw_closure_trace=invariant_result.raw_closure_trace,
        eyb_normalized_expression=invariant_result.eyb_normalized_expression,
        trace_mode=invariant_result.trace_mode,
        convention_notes=invariant_result.convention_notes,
        framing_notes=invariant_result.framing_notes,
        markov_checks=markov_data,
        notes=example.notes,
        metadata={
            "expected_components": example.expected_components,
            "expected_crossing_count": example.expected_crossing_count,
            "example_metadata": example.metadata,
        },
    )


def evaluate_catalog(
    examples: Iterable[BraidExample],
    *,
    rmatrix_builder: RMatrixBuilder,
    eyb_builder: EYBBuilder | None = None,
    q: sp.Expr | None = None,
    include_markov_checks: bool = False,
    conjugator_generators: tuple[int, ...] | list[int] | None = None,
) -> list[BenchmarkEntry]:
    """Evaluate a catalog slice on one local model and optional EYB layer."""

    return [
        evaluate_braid_example(
            example,
            rmatrix_builder=rmatrix_builder,
            eyb_builder=eyb_builder,
            q=q,
            include_markov_checks=include_markov_checks,
            conjugator_generators=conjugator_generators,
        )
        for example in examples
    ]