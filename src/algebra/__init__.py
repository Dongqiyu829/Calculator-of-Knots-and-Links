"""Algebra-level specifications for Lie algebras and representations."""

from .lie_algebra import LieAlgebraSpec
from .representations import (
    RepresentationSpec,
    TensorDecomposition,
    TensorSummand,
    build_sl2_fundamental_representation,
    build_sl2_spin1_representation,
    build_sl3_fundamental_representation,
    get_supported_representations,
)

__all__ = [
    "LieAlgebraSpec",
    "RepresentationSpec",
    "TensorDecomposition",
    "TensorSummand",
    "build_sl2_fundamental_representation",
    "build_sl2_spin1_representation",
    "build_sl3_fundamental_representation",
    "get_supported_representations",
]
