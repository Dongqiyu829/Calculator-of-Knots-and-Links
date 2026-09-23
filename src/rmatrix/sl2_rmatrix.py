"""sl2 local R-matrix builders for the first MVP stage."""

from __future__ import annotations

import sympy as sp

from src.algebra.representations import (
    RepresentationSpec,
    build_sl2_fundamental_representation,
    build_sl2_spin1_representation,
)

from .rmatrix_base import (
    RMatrixData,
    build_local_braiding_from_raw,
    check_yang_baxter,
    compute_eigen_data,
    compute_minimal_polynomial,
)
from .projectors import build_channel_projector_data, validate_projector_family


def _q_number(q: sp.Expr, n: int) -> sp.Expr:
    """Return the q-integer [n]_q."""

    if n == 0:
        return sp.Integer(0)
    return sp.simplify((q**n - q**(-n)) / (q - q**-1))


def _q_factorial(q: sp.Expr, n: int) -> sp.Expr:
    """Return the q-factorial [n]_q! for a nonnegative integer n."""

    value = sp.Integer(1)
    for k in range(1, n + 1):
        value *= _q_number(q, k)
    return sp.simplify(value)


def _sl2_highest_weight_generators(q: sp.Expr, highest_weight: int) -> tuple[sp.Matrix, sp.Matrix, list[int]]:
    """Return E, F, and H-weights for the irreducible sl2 highest-weight module."""

    dimension = highest_weight + 1
    raising = sp.zeros(dimension)
    lowering = sp.zeros(dimension)
    weights: list[int] = []

    for index in range(dimension):
        weight = highest_weight - 2 * index
        weights.append(weight)
        if index > 0:
            raising[index - 1, index] = _q_number(q, highest_weight - index + 1)
        if index < dimension - 1:
            lowering[index + 1, index] = _q_number(q, index + 1)

    return raising, lowering, weights


def _sl2_same_irrep_raw_matrix(q: sp.Expr, highest_weight: int) -> sp.Matrix:
    """Build the raw matrix-form object for V_n tensor V_n.

    Notes
    -----
    This helper uses the same normalization convention that reproduces the
    existing sl2 fundamental 4 x 4 raw matrix exactly when highest_weight = 1.
    For highest_weight = 2 it yields a 9 x 9 model whose braid eigenvalues are
    cleanly organized by the 5 plus 3 plus 1 channel decomposition.
    """

    raising, lowering, weights = _sl2_highest_weight_generators(q, highest_weight)
    local_dim = highest_weight + 1
    diagonal = sp.diag(*[q ** sp.Rational(left * right, 2) for left in weights for right in weights])

    nilpotent_sum = sp.zeros(local_dim * local_dim)
    for power in range(0, highest_weight + 1):
        coefficient = q ** sp.Rational(power * (power - 1), 2)
        coefficient *= (q - q**-1) ** power
        coefficient /= _q_factorial(q, power)
        nilpotent_sum += coefficient * sp.kronecker_product(raising**power, lowering**power)

    # This scalar prefactor is the convention that matches the current 4 x 4
    # fundamental raw matrix already used elsewhere in the project.
    scalar = q ** sp.Rational(highest_weight * highest_weight, 2)
    return sp.simplify(scalar * diagonal * nilpotent_sum)


def _basis_order_from_representation(rep: RepresentationSpec) -> tuple[str, ...]:
    """Return the lexicographically ordered tensor-product basis labels."""

    return tuple(
        f"{left} tensor {right}"
        for left in rep.basis_labels
        for right in rep.basis_labels
    )


def _make_validation_container(
    rep: RepresentationSpec,
    matrix: sp.Matrix,
    braid_matrix: sp.Matrix,
    basis_order: tuple[str, ...],
    eigenvalues: list[sp.Expr],
    minimal_polynomial: sp.Expr | None,
    matrix_eigenvalues: list[sp.Expr],
    factorized_minimal_polynomial: sp.Expr | None,
    eigenvalue_channels: list[dict[str, str]],
    channel_projectors,
) -> RMatrixData:
    """Create a small temporary container used by the validation helpers."""

    return RMatrixData(
        rep=rep,
        matrix=matrix,
        braid_matrix=braid_matrix,
        dim=matrix.rows,
        basis_order=basis_order,
        eigenvalues=eigenvalues,
        minimal_polynomial=minimal_polynomial,
        notes="Temporary container used for validation.",
        convention_notes="Temporary container used for validation.",
        matrix_eigenvalues=matrix_eigenvalues,
        factorized_minimal_polynomial=factorized_minimal_polynomial,
        eigenvalue_channels=eigenvalue_channels,
        channel_projectors=channel_projectors,
    )


def _build_sl2_rmatrix_data(
    *,
    q: sp.Expr,
    rep: RepresentationSpec,
    highest_weight: int,
    eigenvalue_channels: list[dict[str, str]],
    channel_projectors,
    notes: str,
    convention_notes: str,
    diagnostics: bool = True,
) -> RMatrixData:
    """Build one sl2 raw matrix and braid matrix pair with shared reporting logic."""

    raw_matrix = _sl2_same_irrep_raw_matrix(q, highest_weight)
    braid_matrix = build_local_braiding_from_raw(raw_matrix, rep.dimension)
    basis_order = _basis_order_from_representation(rep)
    if not diagnostics:
        # Built-in evaluation needs the same matrices, not an eigen/YBE audit.
        # Research callers retain the validated construction by default.
        return RMatrixData(
            rep=rep,
            matrix=raw_matrix,
            braid_matrix=braid_matrix,
            dim=raw_matrix.rows,
            basis_order=basis_order,
            eigenvalues=[],
            minimal_polynomial=None,
            notes=notes,
            convention_notes=convention_notes,
            eigenvalue_channels=eigenvalue_channels,
        )
    braid_eigenvalues = compute_eigen_data(braid_matrix)
    raw_eigenvalues = compute_eigen_data(raw_matrix)
    minimal_polynomial = compute_minimal_polynomial(braid_matrix)
    factorized_minimal_polynomial = None if minimal_polynomial is None else sp.factor(minimal_polynomial)

    validation_container = _make_validation_container(
        rep=rep,
        matrix=raw_matrix,
        braid_matrix=braid_matrix,
        basis_order=basis_order,
        eigenvalues=braid_eigenvalues,
        minimal_polynomial=minimal_polynomial,
        matrix_eigenvalues=raw_eigenvalues,
        factorized_minimal_polynomial=factorized_minimal_polynomial,
        eigenvalue_channels=eigenvalue_channels,
        channel_projectors=channel_projectors,
    )
    projector_validation = validate_projector_family(channel_projectors, braid_matrix) if channel_projectors else {}
    validation = {
        "braid_ybe": check_yang_baxter(validation_container, target="braid_matrix"),
        "raw_ybe": check_yang_baxter(validation_container, target="matrix"),
        "projector_checks": projector_validation,
    }

    return RMatrixData(
        rep=rep,
        matrix=raw_matrix,
        braid_matrix=braid_matrix,
        dim=raw_matrix.rows,
        basis_order=basis_order,
        eigenvalues=braid_eigenvalues,
        minimal_polynomial=minimal_polynomial,
        notes=notes,
        convention_notes=convention_notes,
        validation_data=validation,
        matrix_eigenvalues=raw_eigenvalues,
        factorized_minimal_polynomial=factorized_minimal_polynomial,
        eigenvalue_channels=eigenvalue_channels,
        channel_projectors=channel_projectors,
    )


def build_sl2_fundamental_rmatrix(q: sp.Expr | None = None, *, diagnostics: bool = True) -> RMatrixData:
    """Build the sl2 fundamental raw matrix and local braiding operator.

    Parameters
    ----------
    q:
        SymPy expression for the deformation parameter. If omitted, a symbolic q
        is created.
    diagnostics:
        Keep eigenvalue, minimal-polynomial, projector, and YBE diagnostics.
        The validated research path is the default; built-in runtime evaluation
        may request the identical matrices without those audits.

    Returns
    -------
    RMatrixData
        Raw matrix and braid_matrix on the ordered basis
        (v_1 tensor v_1, v_1 tensor v_2, v_2 tensor v_1, v_2 tensor v_2).

    Notes
    -----
    The raw matrix here is the standard 4 x 4 matrix-form object for the
    fundamental representation. The local braid generator is obtained by
    applying the tensor-factor swap to that raw matrix.
    """

    parameter = q if q is not None else sp.Symbol("q", nonzero=True)
    rep = build_sl2_fundamental_representation()
    eigenvalue_channels = [
        {
            "channel_label": "J=1",
            "summand_label": "spin1 / symmetric channel",
            "eigenvalue": str(sp.simplify(parameter)),
        },
        {
            "channel_label": "J=0",
            "summand_label": "spin0 / antisymmetric channel",
            "eigenvalue": str(sp.simplify(-parameter ** -1)),
        },
    ]
    channel_projectors = []

    return _build_sl2_rmatrix_data(
        q=parameter,
        rep=rep,
        highest_weight=1,
        eigenvalue_channels=eigenvalue_channels,
        channel_projectors=channel_projectors,
        notes=(
            "Raw matrix is the standard sl2 fundamental 4 x 4 matrix-form object. "
            "braid_matrix is obtained by applying the tensor swap. The implementation is built from the same "
            "sl2 universal-R normalization that will also be used for the spin-1 9 x 9 model."
        ),
        convention_notes=(
            "matrix stores the raw literature-facing object. braid_matrix stores the local braid generator. "
            "All later braid-word code should use braid_matrix only."
        ),
        diagnostics=diagnostics,
    )


def build_sl2_spin1_rmatrix(q: sp.Expr | None = None, *, diagnostics: bool = True) -> RMatrixData:
    """Build the sl2 spin-1 raw matrix and local braiding operator.

    Parameters
    ----------
    q:
        SymPy expression for the deformation parameter. If omitted, a symbolic q
        is created.
    diagnostics:
        Keep eigenvalue, minimal-polynomial, projector, and YBE diagnostics.
        The validated research path is the default.

    Returns
    -------
    RMatrixData
        Raw matrix and braid_matrix on the ordered basis
        (w_1 tensor w_1, w_1 tensor w_0, ..., w_-1 tensor w_-1).

    Notes
    -----
    This implementation is organized around the channel decomposition
    3 tensor 3 = 5 plus 3 plus 1. The current code constructs the 9 x 9 model
    from the same universal-R normalization already used for the sl2 fundamental
    builder, then reports the braid eigenvalues by channel.

    VERIFY_WITH_REFERENCE
    ---------------------
    The channel eigenvalues are internally consistent with the current project
    conventions and pass the Yang-Baxter checks, but they should still be cross-
    checked against an external reference if a different normalization convention
    is desired later.
    """

    parameter = q if q is not None else sp.Symbol("q", nonzero=True)
    rep = build_sl2_spin1_representation()
    eigenvalue_channels = [
        {
            "channel_label": "J=2",
            "summand_label": "spin2 / symmetric channel",
            "eigenvalue": str(sp.simplify(parameter**4)),
        },
        {
            "channel_label": "J=1",
            "summand_label": "spin1 / antisymmetric channel",
            "eigenvalue": str(sp.Integer(-1)),
        },
        {
            "channel_label": "J=0",
            "summand_label": "spin0 / symmetric scalar channel",
            "eigenvalue": str(sp.simplify(parameter**-2)),
        },
    ]

    channel_projectors = []
    if diagnostics:
        raw_matrix = _sl2_same_irrep_raw_matrix(parameter, 2)
        braid_matrix = build_local_braiding_from_raw(raw_matrix, rep.dimension)
        channel_projectors = [
            build_channel_projector_data(
                channel_label="J=2",
                summand_label="spin2 / symmetric channel",
                dimension=5,
                eigenvalue=parameter**4,
                braid_matrix=braid_matrix,
                all_eigenvalues=[parameter**4, -sp.Integer(1), parameter**-2],
                notes="Projector onto the spin-2 symmetric channel.",
            ),
            build_channel_projector_data(
                channel_label="J=1",
                summand_label="spin1 / antisymmetric channel",
                dimension=3,
                eigenvalue=-sp.Integer(1),
                braid_matrix=braid_matrix,
                all_eigenvalues=[parameter**4, -sp.Integer(1), parameter**-2],
                notes="Projector onto the spin-1 antisymmetric channel.",
            ),
            build_channel_projector_data(
                channel_label="J=0",
                summand_label="spin0 / symmetric scalar channel",
                dimension=1,
                eigenvalue=parameter**-2,
                braid_matrix=braid_matrix,
                all_eigenvalues=[parameter**4, -sp.Integer(1), parameter**-2],
                notes="Projector onto the spin-0 symmetric scalar channel.",
            ),
        ]

    return _build_sl2_rmatrix_data(
        q=parameter,
        rep=rep,
        highest_weight=2,
        eigenvalue_channels=eigenvalue_channels,
        channel_projectors=channel_projectors,
        notes=(
            "The 9 x 9 sl2 spin-1 model is built from the same sl2 universal-R normalization used for the "
            "current fundamental 4 x 4 matrix. The output is organized by the projector-first channel picture "
            "5 plus 3 plus 1 even though the first implementation constructs the matrix explicitly. "
            "TODO: add explicit projector matrices to make the channel decomposition directly visible inside the "
            "matrix construction itself. VERIFY_WITH_REFERENCE: compare this normalization against a standard "
            "spin-1 braid-matrix reference if a literature-specific convention is required."
        ),
        convention_notes=(
            "matrix stores the raw literature-facing object. braid_matrix stores the local braid generator. "
            "Channel labels are reported for the braid_matrix eigenvalues, not for the raw matrix eigenvalues."
        ),
        diagnostics=diagnostics,
    )
