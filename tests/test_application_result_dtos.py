"""Service DTO conversion, reporting, and serialization regression checks."""

from __future__ import annotations

import sympy as sp

from src.services import (
    application_braid_result_from_internal,
    evaluate_catalog_example,
    evaluate_catalog_result,
    format_application_braid_result,
    serialize_application_braid_result,
)


def test_application_dto_preserves_current_branch_data() -> None:
    legacy_entry = evaluate_catalog_example("trefoil", branch_ids=("sl2_fundamental", "sl2_spin1"), q=sp.Integer(2))
    result = application_braid_result_from_internal(legacy_entry)

    assert result.example_label == legacy_entry.example_label
    assert result.generators == (1, 1, 1)
    assert result.selected_branch_ids == ("sl2_fundamental", "sl2_spin1")
    assert [(item.branch_id, item.status, item.primary_output) for item in result.branch_results] == [
        ("sl2_fundamental", "formal", "67/256"),
        ("sl2_spin1", "candidate", "266029/65536"),
    ]
    assert result.branch_results[1].primary_output_label == "Colored Jones candidate output"
    assert result.branch_results[1].notes == legacy_entry.branch_results[1].notes
    assert result.branch_results[1].metadata == legacy_entry.branch_results[1].metadata


def test_application_reporting_and_serialization_are_deterministic() -> None:
    result = evaluate_catalog_result("figure_eight", branch_ids=("sl2_fundamental",), q=sp.Integer(2))

    first = serialize_application_braid_result(result)
    assert first == serialize_application_braid_result(result)
    assert '"primary_output": "205/16"' in first
    report = format_application_braid_result(result)
    assert "########## figure_eight ##########" in report
    assert "Primary output: 205/16" in report
