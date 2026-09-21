"""Construct global braid operators from local braiding data."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import sympy as sp

from src.rmatrix.rmatrix_base import RMatrixData

from .braid_word import BraidWord


def _matrix_to_string_grid(matrix: sp.Matrix) -> list[list[str]]:
    """Convert a SymPy matrix into a nested list of string entries."""

    return [[str(matrix[row, col]) for col in range(matrix.cols)] for row in range(matrix.rows)]


def _embed_adjacent_local_operator(
    operator: sp.Matrix,
    local_dim: int,
    num_factors: int,
    start: int,
) -> sp.Matrix:
    """Embed a local operator acting on adjacent tensor legs."""

    if num_factors < 2:
        raise ValueError("num_factors must be at least 2")
    if start < 0 or start + 1 >= num_factors:
        raise ValueError("start must identify a valid adjacent tensor pair")

    left = sp.eye(local_dim ** start)
    right = sp.eye(local_dim ** (num_factors - start - 2))
    return sp.kronecker_product(left, operator, right)


@dataclass(frozen=True, slots=True)
class BraidOperatorStep:
    """Record one local insertion used to build the global braid operator."""

    step_index: int
    generator: int
    strand_pair: tuple[int, int]
    used_inverse: bool
    embedded_operator_shape: tuple[int, int]
    local_operator_shape: tuple[int, int]

    def summary(self) -> str:
        """Return a readable one-line description of the construction step."""

        inverse_text = "yes" if self.used_inverse else "no"
        return (
            f"Step {self.step_index}: generator={self.generator}, "
            f"strand_pair={self.strand_pair}, used_inverse={inverse_text}, "
            f"local_shape={self.local_operator_shape}, embedded_shape={self.embedded_operator_shape}"
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a structured representation of the construction step."""

        return {
            "step_index": self.step_index,
            "generator": self.generator,
            "strand_pair": list(self.strand_pair),
            "used_inverse": self.used_inverse,
            "local_operator_shape": list(self.local_operator_shape),
            "embedded_operator_shape": list(self.embedded_operator_shape),
        }

    def to_string(self) -> str:
        """Return a string form aligned with the summary output."""

        return self.summary()


@dataclass(frozen=True, slots=True)
class BraidOperatorData:
    """Store the global braid operator together with construction metadata."""

    braid_word: BraidWord
    rmatrix: RMatrixData
    operator: sp.Matrix
    total_dimension: int
    basis_order_description: str
    steps: tuple[BraidOperatorStep, ...]
    notes: str = ""
    convention_notes: str = ""

    @property
    def num_strands(self) -> int:
        """Return the number of strands in the underlying braid word."""

        return self.braid_word.num_strands

    @property
    def writhe(self) -> int:
        """Return the writhe of the underlying braid word."""

        return self.braid_word.writhe()

    def summary(self) -> str:
        """Return a readable multiline summary of the global braid operator."""

        lines = [
            f"Representation: {self.rmatrix.rep.name()}",
            f"Braid word: {self.braid_word.word_string()}",
            f"Number of strands: {self.num_strands}",
            f"Writhe: {self.writhe}",
            f"Total operator dimension: {self.total_dimension}",
            f"Operator shape: {self.operator.shape}",
            f"Basis order description: {self.basis_order_description}",
            "Construction steps:",
        ]
        lines.extend(f"  - {step.summary()}" for step in self.steps)
        if self.convention_notes:
            lines.append(f"Convention notes: {self.convention_notes}")
        if self.notes:
            lines.append(f"Notes: {self.notes}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Return a structured representation suitable for serialization."""

        return {
            "braid_word": self.braid_word.to_dict(),
            "rmatrix": self.rmatrix.to_dict(),
            "num_strands": self.num_strands,
            "writhe": self.writhe,
            "total_dimension": self.total_dimension,
            "operator_shape": list(self.operator.shape),
            "basis_order_description": self.basis_order_description,
            "operator": _matrix_to_string_grid(self.operator),
            "steps": [step.to_dict() for step in self.steps],
            "notes": self.notes,
            "convention_notes": self.convention_notes,
        }

    def to_string(self) -> str:
        """Return a string form aligned with the summary output."""

        return self.summary()

    def pretty_print(self) -> str:
        """Return a more detailed printable report including the matrix."""

        return "\n".join([self.summary(), "Operator matrix:", str(self.operator)])


@dataclass(slots=True)
class BraidOperatorBuilder:
    """Build a global braid operator from a braid word and local braiding data.

    Notes
    -----
    This builder uses rmatrix.braid_matrix exclusively. The raw literature-side
    matrix stored in rmatrix.matrix is not used here.
    """

    braid_word: BraidWord
    rmatrix: RMatrixData

    def build(self) -> BraidOperatorData:
        """Construct the global operator on V tensor ... tensor V."""

        if self.rmatrix.braid_matrix.shape[0] != self.rmatrix.braid_matrix.shape[1]:
            raise ValueError("braid_matrix must be square")
        if self.rmatrix.rep.dimension * self.rmatrix.rep.dimension != self.rmatrix.dim:
            raise ValueError("RMatrixData dimension is inconsistent with the representation dimension")

        num_strands = self.braid_word.num_strands
        local_dim = self.rmatrix.rep.dimension
        total_dimension = local_dim ** num_strands
        total_operator = sp.eye(total_dimension)
        steps: list[BraidOperatorStep] = []
        embedded_cache: dict[int, sp.Matrix] = {}
        local_operator = self.rmatrix.braid_matrix
        local_inverse: sp.Matrix | None = None

        for index, generator in enumerate(self.braid_word.generators, start=1):
            generator_index = abs(generator)
            used_inverse = generator < 0
            if generator not in embedded_cache:
                step_operator = local_operator
                if used_inverse:
                    if local_inverse is None:
                        local_inverse = sp.simplify(local_operator.inv())
                    step_operator = local_inverse
                embedded_cache[generator] = _embed_adjacent_local_operator(
                    step_operator,
                    local_dim=local_dim,
                    num_factors=num_strands,
                    start=generator_index - 1,
                )
            embedded = embedded_cache[generator]
            total_operator = total_operator * embedded
            steps.append(
                BraidOperatorStep(
                    step_index=index,
                    generator=generator,
                    strand_pair=(generator_index, generator_index + 1),
                    used_inverse=used_inverse,
                    embedded_operator_shape=embedded.shape,
                    local_operator_shape=local_operator.shape,
                )
            )

        basis_description = (
            f"Tensor-product basis on V^tensor {num_strands} follows lexicographic order induced by "
            f"the representation basis {self.rmatrix.rep.basis_labels}."
        )
        notes = (
            "The global operator is built by multiplying embedded local braid generators from left to right "
            "following the input generator list."
        )
        convention_notes = (
            "Only braid_matrix is used for braid generators. Negative generators use the inverse of braid_matrix."
        )
        return BraidOperatorData(
            braid_word=self.braid_word,
            rmatrix=self.rmatrix,
            operator=total_operator,
            total_dimension=total_dimension,
            basis_order_description=basis_description,
            steps=tuple(steps),
            notes=notes,
            convention_notes=convention_notes,
        )