"""Representation specifications for the first MVP stage.

The current goal is clarity and inspectability. Each supported representation
stores enough metadata to explain later R-matrix and braid-operator choices.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .lie_algebra import LieAlgebraSpec, sl2_algebra, sl3_algebra


@dataclass(frozen=True, slots=True)
class TensorSummand:
    """One irreducible channel appearing in a tensor-product decomposition.

    Parameters
    ----------
    label:
        Human-readable label for the summand.
    dimension:
        Dimension of the irreducible summand.
    eigenchannel_label:
        Optional label reserved for later braiding eigenchannel reports.
    notes:
        Extra explanatory text. This is useful when the same dimension can be
        described in multiple ways, such as symmetric versus antisymmetric.
    """

    label: str
    dimension: int
    formula_label: str | None = None
    eigenchannel_label: str | None = None
    notes: str = ""

    def __post_init__(self) -> None:
        if self.dimension < 1:
            raise ValueError("summand dimension must be positive")

    def summary(self) -> str:
        """Return a compact one-line description of the summand."""

        parts = [f"{self.label} (dim={self.dimension})"]
        if self.eigenchannel_label:
            parts.append(f"channel={self.eigenchannel_label}")
        if self.notes:
            parts.append(self.notes)
        return "; ".join(parts)

    def to_dict(self) -> dict[str, str | int | None]:
        """Return a structured description of the irreducible channel."""

        return {
            "label": self.label,
            "dimension": self.dimension,
            "formula_label": self.formula_label,
            "eigenchannel_label": self.eigenchannel_label,
            "notes": self.notes,
        }

    def to_string(self) -> str:
        """Return a string form aligned with the summary output."""

        return self.summary()


@dataclass(frozen=True, slots=True)
class TensorDecomposition:
    """Record the decomposition of V tensor V into irreducible channels.

    Parameters
    ----------
    summands:
        Ordered tuple of irreducible tensor summands.
    basis_convention:
        Text describing the basis order expected for V and V tensor V.
    notes:
        Additional remarks, including TODO or convention warnings that should be
        visible in debug output.
    """

    summands: tuple[TensorSummand, ...]
    basis_convention: str
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.summands:
            raise ValueError("TensorDecomposition requires at least one summand")

    @property
    def total_dimension(self) -> int:
        """Return the total dimension reconstructed from the listed summands."""

        return sum(summand.dimension for summand in self.summands)

    def decomposition_formula(self) -> str:
        """Return a compact formula such as 2 x 2 = 3 + 1."""

        return " + ".join(
            summand.formula_label or str(summand.dimension) for summand in self.summands
        )

    def summary(self) -> str:
        """Return a human-readable multiline summary of the decomposition."""

        lines = [
            f"V tensor V decomposition: {self.decomposition_formula()}",
            f"Reconstructed tensor dimension: {self.total_dimension}",
            f"Basis convention: {self.basis_convention}",
            "Channels:",
        ]
        lines.extend(f"  - {summand.summary()}" for summand in self.summands)
        if self.notes:
            lines.append(f"Notes: {self.notes}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Return a structured form suitable for serialization and GUI display."""

        return {
            "decomposition_formula": self.decomposition_formula(),
            "total_dimension": self.total_dimension,
            "basis_convention": self.basis_convention,
            "summands": [summand.to_dict() for summand in self.summands],
            "notes": self.notes,
        }

    def to_string(self) -> str:
        """Return a string form aligned with the summary output."""

        return self.summary()


@dataclass(frozen=True, slots=True)
class RepresentationSpec:
    """Describe a concrete low-dimensional representation used by the MVP.

    Parameters
    ----------
    algebra:
        Lie algebra supporting the representation.
    label:
        Short identifier such as "fundamental" or "spin1".
    dimension:
        Vector-space dimension of the representation.
    basis_labels:
        Ordered basis labels for V itself. This order becomes the reference for
        later tensor-product basis conventions.
    tensor_square_decomposition:
        Decomposition data for V tensor V.
    convention_notes:
        Human-readable notes explaining basis order and any convention choices.
    source_reference:
        Short provenance string documenting the mathematical source or standard
        viewpoint used for this representation.
    metadata:
        Small structured extras reserved for later modules.
    """

    algebra: LieAlgebraSpec
    label: str
    dimension: int
    basis_labels: tuple[str, ...]
    tensor_square_decomposition: TensorDecomposition
    convention_notes: str
    source_reference: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.dimension < 1:
            raise ValueError("representation dimension must be positive")
        if len(self.basis_labels) != self.dimension:
            raise ValueError("basis label count must match the representation dimension")

        expected_tensor_dim = self.dimension * self.dimension
        actual_tensor_dim = self.tensor_square_decomposition.total_dimension
        if actual_tensor_dim != expected_tensor_dim:
            raise ValueError(
                "tensor-square decomposition dimension mismatch: "
                f"expected {expected_tensor_dim}, got {actual_tensor_dim}"
            )

    def algebra_name(self) -> str:
        """Return the conventional algebra name, for example sl2 or sl3."""

        return self.algebra.name()

    def name(self) -> str:
        """Return the project-wide representation identifier."""

        return f"{self.algebra_name()} {self.label}"

    def summary(self) -> str:
        """Return a human-readable multiline summary for debug output."""

        lines = [
            f"Representation: {self.name()}",
            f"Algebra: {self.algebra_name()} ({self.algebra.dynkin_label()})",
            f"Label: {self.label}",
            f"Dimension: {self.dimension}",
            f"Basis order: ({', '.join(self.basis_labels)})",
            self.tensor_square_decomposition.summary(),
            f"Convention notes: {self.convention_notes}",
            f"Source reference: {self.source_reference}",
        ]
        if self.metadata:
            lines.append(f"Metadata: {self.metadata}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Return a structured representation suitable for serialization."""

        return {
            "name": self.name(),
            "label": self.label,
            "dimension": self.dimension,
            "algebra": self.algebra.to_dict(),
            "basis_labels": list(self.basis_labels),
            "tensor_square_decomposition": self.tensor_square_decomposition.to_dict(),
            "convention_notes": self.convention_notes,
            "source_reference": self.source_reference,
            "metadata": dict(self.metadata),
        }

    def to_string(self) -> str:
        """Return a string form aligned with the summary output."""

        return self.summary()


def build_sl2_fundamental_representation() -> RepresentationSpec:
    """Return the fundamental 2-dimensional representation of U_q(sl2).

    Basis convention
    ----------------
    The basis is ordered by decreasing weight as (v_1, v_2). Later tensor basis
    order is fixed as lexicographic order induced from this basis.
    """

    decomposition = TensorDecomposition(
        summands=(
            TensorSummand(
                label="spin1 / symmetric channel",
                dimension=3,
                formula_label="3",
                eigenchannel_label="J=1",
                notes="Triplet channel in the decomposition 2 tensor 2 = 3 plus 1.",
            ),
            TensorSummand(
                label="spin0 / antisymmetric channel",
                dimension=1,
                formula_label="1",
                eigenchannel_label="J=0",
                notes="Singlet channel in the decomposition 2 tensor 2 = 3 plus 1.",
            ),
        ),
        basis_convention=(
            "Basis of V is (v_1, v_2); basis of V tensor V is the lexicographic order "
            "(v_1 tensor v_1, v_1 tensor v_2, v_2 tensor v_1, v_2 tensor v_2)."
        ),
        notes="This decomposition corresponds to 2 tensor 2 = 3 plus 1.",
    )

    return RepresentationSpec(
        algebra=sl2_algebra(),
        label="fundamental",
        dimension=2,
        basis_labels=("v_1", "v_2"),
        tensor_square_decomposition=decomposition,
        convention_notes=(
            "Highest-weight basis is ordered from highest to lowest weight. "
            "Tensor-product basis uses the induced lexicographic order."
        ),
        source_reference=(
            "Standard U_q(sl2) fundamental representation; compatible with the "
            "Reshetikhin-Turaev ribbon functor viewpoint."
        ),
        metadata={
            "project_key": "sl2-fund",
            "highest_weight": "omega_1",
            "tensor_square_formula": "2 tensor 2 = 3 plus 1",
        },
    )


def build_sl2_spin1_representation() -> RepresentationSpec:
    """Return the 3-dimensional spin-1 representation of U_q(sl2).

    This object is intentionally organized around the tensor decomposition
    3 tensor 3 = 5 plus 3 plus 1 so that the later projector-based R-matrix
    implementation can explain each braiding channel explicitly.
    """

    decomposition = TensorDecomposition(
        summands=(
            TensorSummand(
                label="spin2 / symmetric channel",
                dimension=5,
                formula_label="5",
                eigenchannel_label="J=2",
                notes="Highest-spin channel in the decomposition 3 tensor 3 = 5 plus 3 plus 1.",
            ),
            TensorSummand(
                label="spin1 / antisymmetric channel",
                dimension=3,
                formula_label="3",
                eigenchannel_label="J=1",
                notes="Antisymmetric channel in the decomposition 3 tensor 3 = 5 plus 3 plus 1.",
            ),
            TensorSummand(
                label="spin0 / symmetric scalar channel",
                dimension=1,
                formula_label="1",
                eigenchannel_label="J=0",
                notes="Scalar symmetric channel in the decomposition 3 tensor 3 = 5 plus 3 plus 1.",
            ),
        ),
        basis_convention=(
            "Basis of V is ordered by weights as (w_1, w_0, w_-1). "
            "Basis of V tensor V will later follow lexicographic order induced from this basis."
        ),
        notes=(
            "Projector-first implementation is planned for the R-matrix stage. "
            "TODO: move detailed projector data into a dedicated tensor_decomp module if the "
            "representation catalog grows."
        ),
    )

    return RepresentationSpec(
        algebra=sl2_algebra(),
        label="spin1",
        dimension=3,
        basis_labels=("w_1", "w_0", "w_-1"),
        tensor_square_decomposition=decomposition,
        convention_notes=(
            "Weight basis is ordered from highest to lowest weight. "
            "CONVENTION_WARNING: later R-matrix code must state explicitly whether reported eigenvalues "
            "belong to the raw R object or the braiding operator."
        ),
        source_reference=(
            "Standard U_q(sl2) spin-1 representation theory; decomposition organized for a projector-based "
            "9 x 9 braiding construction in the MVP."
        ),
        metadata={
            "project_key": "sl2-spin1",
            "highest_weight": "2 omega_1",
            "tensor_square_formula": "3 tensor 3 = 5 plus 3 plus 1",
            "implementation_strategy": "projector-first, explicit-formula fallback",
            "verify_with_reference": True,
        },
    )


def build_sl3_fundamental_representation() -> RepresentationSpec:
    """Return the fundamental 3-dimensional representation of U_q(sl3).

    The decomposition 3 tensor 3 = 6 plus 3bar is recorded explicitly because
    the first sl3 braiding implementation will follow the standard Hecke-type
    symmetric versus antisymmetric channel split.
    """

    decomposition = TensorDecomposition(
        summands=(
            TensorSummand(
                label="symmetric square / 6",
                dimension=6,
                formula_label="6",
                eigenchannel_label="sym",
                notes="Corresponds to the Hecke-type symmetric channel.",
            ),
            TensorSummand(
                label="antisymmetric square / 3bar",
                dimension=3,
                formula_label="3bar",
                eigenchannel_label="antisym",
                notes="Corresponds to the Hecke-type antisymmetric channel.",
            ),
        ),
        basis_convention=(
            "Basis of V is (e_1, e_2, e_3). Basis of V tensor V will use lexicographic order "
            "(e_1 tensor e_1, e_1 tensor e_2, ..., e_3 tensor e_3)."
        ),
        notes=(
            "This is the channel split needed for the first Hecke-type sl3 fundamental braiding model: "
            "3 tensor 3 = 6 plus 3bar."
        ),
    )

    return RepresentationSpec(
        algebra=sl3_algebra(),
        label="fundamental",
        dimension=3,
        basis_labels=("e_1", "e_2", "e_3"),
        tensor_square_decomposition=decomposition,
        convention_notes=(
            "The basis is the standard ordered weight basis. Later sl3 R-matrix code must keep the tensor basis "
            "in lexicographic order so the 9 x 9 matrix remains directly inspectable."
        ),
        source_reference=(
            "Standard U_q(sl3) fundamental representation; first MVP braiding implementation will follow the "
            "classical Hecke-type symmetric/antisymmetric channel split."
        ),
        metadata={
            "project_key": "sl3-fund",
            "highest_weight": "omega_1",
            "tensor_square_formula": "3 tensor 3 = 6 plus 3bar",
            "implementation_strategy": "Hecke-type fundamental braiding",
        },
    )


def get_supported_representations() -> dict[str, RepresentationSpec]:
    """Return the first-stage catalog of supported representations."""

    return {
        "sl2-fund": build_sl2_fundamental_representation(),
        "sl2-spin1": build_sl2_spin1_representation(),
        "sl3-fund": build_sl3_fundamental_representation(),
    }
