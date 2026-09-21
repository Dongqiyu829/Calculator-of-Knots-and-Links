"""sl3 local R-matrix builders for the first MVP stage."""

from __future__ import annotations

import sympy as sp

from src.algebra.representations import build_sl3_fundamental_representation

from .rmatrix_base import (
    RMatrixData,
    build_local_braiding_from_raw,
    check_yang_baxter,
    compute_eigen_data,
    compute_minimal_polynomial,
)
from .projectors import build_channel_projector_data, validate_projector_family


def _matrix_units(size: int) -> dict[tuple[int, int], sp.Matrix]:
    """Return the standard matrix units E_ij for the given size."""

    units: dict[tuple[int, int], sp.Matrix] = {}
    for row in range(size):
        for col in range(size):
            unit = sp.zeros(size)
            unit[row, col] = 1
            units[(row, col)] = unit
    return units


def build_sl3_fundamental_rmatrix(q: sp.Expr | None = None) -> RMatrixData:
    """Build the sl3 fundamental raw matrix and local braiding operator.

    Parameters
    ----------
    q:
        SymPy expression for the deformation parameter. If omitted, a symbolic q
        is created.

    Returns
    -------
    RMatrixData
        Raw matrix and braid_matrix on the lexicographically ordered basis
        (e_1 tensor e_1, e_1 tensor e_2, ..., e_3 tensor e_3).

    Notes
    -----
    The raw matrix is the standard fundamental U_q(sl_n) matrix-form object
    specialized to n = 3. The braiding operator is obtained by applying the
    tensor-factor swap, which yields eigenvalues q on the symmetric 6-channel
    and -1/q on the antisymmetric 3bar-channel.
    """

    parameter = q if q is not None else sp.Symbol("q", nonzero=True)
    rep = build_sl3_fundamental_representation()
    units = _matrix_units(rep.dimension)

    raw_matrix = sp.zeros(rep.dimension * rep.dimension)
    for index in range(rep.dimension):
        raw_matrix += parameter * sp.kronecker_product(units[(index, index)], units[(index, index)])

    for left in range(rep.dimension):
        for right in range(rep.dimension):
            if left != right:
                raw_matrix += sp.kronecker_product(units[(left, left)], units[(right, right)])

    for left in range(rep.dimension):
        for right in range(left + 1, rep.dimension):
            raw_matrix += (parameter - parameter ** -1) * sp.kronecker_product(
                units[(left, right)], units[(right, left)]
            )

    braid_matrix = build_local_braiding_from_raw(raw_matrix, rep.dimension)
    braid_eigenvalues = compute_eigen_data(braid_matrix)
    raw_eigenvalues = compute_eigen_data(raw_matrix)
    minimal_polynomial = compute_minimal_polynomial(braid_matrix)
    factorized_minimal_polynomial = None if minimal_polynomial is None else sp.factor(minimal_polynomial)
    basis_order = tuple(
        f"{left} tensor {right}"
        for left in rep.basis_labels
        for right in rep.basis_labels
    )
    eigenvalue_channels = [
        {
            "channel_label": "sym",
            "summand_label": "symmetric square / 6",
            "eigenvalue": str(sp.simplify(parameter)),
        },
        {
            "channel_label": "antisym",
            "summand_label": "antisymmetric square / 3bar",
            "eigenvalue": str(sp.simplify(-parameter ** -1)),
        },
    ]
    channel_projectors = [
        build_channel_projector_data(
            channel_label="sym",
            summand_label="symmetric square / 6",
            dimension=6,
            eigenvalue=parameter,
            braid_matrix=braid_matrix,
            all_eigenvalues=[parameter, -parameter**-1],
            notes="Symmetric projector in the decomposition 3 tensor 3 = 6 plus 3bar.",
        ),
        build_channel_projector_data(
            channel_label="antisym",
            summand_label="antisymmetric square / 3bar",
            dimension=3,
            eigenvalue=-parameter**-1,
            braid_matrix=braid_matrix,
            all_eigenvalues=[parameter, -parameter**-1],
            notes="Antisymmetric projector in the decomposition 3 tensor 3 = 6 plus 3bar.",
        ),
    ]
    projector_validation = validate_projector_family(channel_projectors, braid_matrix)

    validation_container = RMatrixData(
        rep=rep,
        matrix=raw_matrix,
        braid_matrix=braid_matrix,
        dim=raw_matrix.rows,
        basis_order=basis_order,
        eigenvalues=braid_eigenvalues,
        minimal_polynomial=minimal_polynomial,
        notes="Temporary container used for validation.",
        convention_notes="Temporary container used for validation.",
        matrix_eigenvalues=raw_eigenvalues,
        factorized_minimal_polynomial=factorized_minimal_polynomial,
        eigenvalue_channels=eigenvalue_channels,
        channel_projectors=channel_projectors,
    )
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
        notes=(
            "Raw matrix is the standard Hecke-type fundamental U_q(sl3) matrix-form object on the ordered basis "
            "(e_1 tensor e_1, e_1 tensor e_2, ..., e_3 tensor e_3). braid_matrix is obtained by applying the "
            "tensor swap."
        ),
        convention_notes=(
            "matrix stores the raw literature-facing object. braid_matrix stores the local braid generator. "
            "The channel labels refer to the 6 and 3bar decomposition of braid_matrix."
        ),
        validation_data=validation,
        matrix_eigenvalues=raw_eigenvalues,
        factorized_minimal_polynomial=factorized_minimal_polynomial,
        eigenvalue_channels=eigenvalue_channels,
        channel_projectors=channel_projectors,
    )
