"""Backend-selection contract at the frontend-neutral service boundary."""

from __future__ import annotations

import pytest
import sympy as sp

from src.services import (
    UnsupportedComputationBackendError,
    build_custom_braid_word,
    evaluate_braid_result,
    evaluate_catalog_result,
    list_computation_backends,
    validate_computation_backend,
)


def test_backend_catalog_and_sl2_only_eligibility() -> None:
    descriptors = list_computation_backends()
    assert tuple(item.backend_id for item in descriptors) == ("matrix_free", "explicit", "temperley_lieb")
    assert descriptors[0].scalar_only is True
    assert descriptors[1].scalar_only is False
    assert descriptors[2].supports_branches(("sl2_fundamental",))
    assert not descriptors[2].supports_branches(("sl2_fundamental", "sl3_fundamental"))
    with pytest.raises(UnsupportedComputationBackendError, match="supports sl2_fundamental only"):
        validate_computation_backend("temperley_lieb", ("sl2_spin1",))


@pytest.mark.parametrize("q", (sp.Integer(2), sp.Symbol("q", nonzero=True)))
def test_catalog_and_manual_routes_have_exact_backend_parity(q) -> None:
    word = build_custom_braid_word(2, "1 1 1", label="trefoil")
    for backend in ("explicit", "matrix_free", "temperley_lieb"):
        catalog = evaluate_catalog_result("trefoil", branch_ids=("sl2_fundamental",), q=q, backend=backend)
        manual = evaluate_braid_result(word, branch_ids=("sl2_fundamental",), q=q, backend=backend)
        assert catalog.branch_results[0].primary_output == manual.branch_results[0].primary_output
        assert catalog.branch_results[0].status == manual.branch_results[0].status == "formal"


def test_omitted_public_backend_is_still_explicit_reference() -> None:
    implicit = evaluate_catalog_result("trefoil", branch_ids=("sl2_fundamental",), q=sp.Integer(2))
    explicit = evaluate_catalog_result("trefoil", branch_ids=("sl2_fundamental",), q=sp.Integer(2), backend="explicit")
    assert implicit == explicit
    assert implicit.branch_results[0].raw_trace is not None
    assert implicit.branch_results[0].metadata.get("evaluation_backend") is None


def test_service_rejects_tl_for_incompatible_branches_as_application_error() -> None:
    with pytest.raises(UnsupportedComputationBackendError, match="supports sl2_fundamental only"):
        evaluate_catalog_result("trefoil", branch_ids=("sl2_fundamental", "sl3_fundamental"), q=sp.Integer(2), backend="temperley_lieb")
