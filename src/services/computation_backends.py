"""Frontend-neutral choices for the already validated built-in backends."""

from __future__ import annotations

from dataclasses import dataclass

from .branch_catalog import validate_branch_ids
from .errors import UnsupportedComputationBackendError


@dataclass(frozen=True, slots=True)
class ComputationBackendDescriptor:
    backend_id: str
    display_name: str
    description: str
    scalar_only: bool
    supported_branch_ids: frozenset[str] | None = None

    def supports_branches(self, branch_ids: tuple[str, ...] | list[str] | None) -> bool:
        if self.supported_branch_ids is None:
            return True
        return bool(branch_ids) and set(branch_ids) <= self.supported_branch_ids


COMPUTATION_BACKENDS = (
    ComputationBackendDescriptor(
        "matrix_free",
        "Fast scalar (recommended)",
        "Exact EYB scalar for all built-in branches. Ordinary raw trace and full global operator diagnostics are not computed; performance depends on the braid.",
        True,
    ),
    ComputationBackendDescriptor(
        "explicit",
        "Reference / diagnostics",
        "Explicit global-matrix reference evaluation, including ordinary raw trace and available diagnostics.",
        False,
    ),
    ComputationBackendDescriptor(
        "temperley_lieb",
        "Temperley–Lieb (sl2 Jones only)",
        "Exact planar scalar for sl2 fundamental only. Ordinary raw trace and full global operator diagnostics are not computed; performance depends on the braid.",
        True,
        frozenset({"sl2_fundamental"}),
    ),
)


def list_computation_backends() -> tuple[ComputationBackendDescriptor, ...]:
    """Return choices in the maintained desktop's recommended display order."""

    return COMPUTATION_BACKENDS


def get_computation_backend(backend_id: str) -> ComputationBackendDescriptor:
    for descriptor in COMPUTATION_BACKENDS:
        if descriptor.backend_id == backend_id:
            return descriptor
    raise UnsupportedComputationBackendError(
        f"Unknown computation backend '{backend_id}'. Choose matrix_free, explicit, or temperley_lieb."
    )


def validate_computation_backend(
    backend_id: str, branch_ids: tuple[str, ...] | list[str] | None
) -> ComputationBackendDescriptor:
    """Validate a backend/branch combination without evaluating mathematics."""

    selected = validate_branch_ids(branch_ids)
    descriptor = get_computation_backend(backend_id)
    if not descriptor.supports_branches(selected):
        raise UnsupportedComputationBackendError(
            "temperley_lieb backend supports sl2_fundamental only. "
            "Choose Fast scalar or Reference / diagnostics for sl3 and spin-1."
        )
    return descriptor
