"""Service DTO conversion, reporting, and serialization regression checks."""

from __future__ import annotations

import sympy as sp

from src.services import (
    application_braid_result_from_internal,
    build_application_branch_presentation,
    evaluate_catalog_example,
    evaluate_catalog_result,
    format_application_braid_compact_result,
    format_application_braid_result,
    serialize_application_braid_result,
    parse_q_text,
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


def test_sl2_symbolic_compact_presentation_adds_exact_standard_t_form_for_trefoil() -> None:
    result = evaluate_catalog_result("trefoil", branch_ids=("sl2_fundamental",), q=parse_q_text("q"))
    presentation = build_application_branch_presentation(result.branch_results[0], q_parameter_text="q")
    t = sp.Symbol("t")

    assert presentation.polynomial.standard_variable_name == "Standard Jones variable t"
    assert sp.simplify(sp.sympify(presentation.polynomial.standard_polynomial_expression) - (-t**4 + t**3 + t)) == 0
    assert presentation.polynomial.atlas_variable_name == "Knot Atlas-comparable q_atlas"


def test_sl2_symbolic_compact_presentation_adds_exact_standard_t_form_for_figure_eight() -> None:
    result = evaluate_catalog_result("figure_eight", branch_ids=("sl2_fundamental",), q=parse_q_text("q"))
    presentation = build_application_branch_presentation(result.branch_results[0], q_parameter_text="q")
    t = sp.Symbol("t")

    assert sp.simplify(sp.sympify(presentation.polynomial.standard_polynomial_expression) - (t**2 - t + 1 - 1 / t + t**-2)) == 0


def test_numeric_q_compact_presentation_stays_scalar_only() -> None:
    result = evaluate_catalog_result("trefoil", branch_ids=("sl2_fundamental",), q=sp.Integer(2))
    presentation = build_application_branch_presentation(result.branch_results[0], q_parameter_text="2")
    report = format_application_braid_compact_result(result, q_parameter_text="2")

    assert presentation.polynomial.conversion_status == "scalar_only"
    assert presentation.polynomial.standard_polynomial_expression is None
    assert "Scalar evaluation at q = 2." in report


def test_sl3_symbolic_compact_presentation_uses_atlas_a2_label() -> None:
    result = evaluate_catalog_result("trefoil", branch_ids=("sl3_fundamental",), q=parse_q_text("q"))
    presentation = build_application_branch_presentation(result.branch_results[0], q_parameter_text="q")

    assert presentation.polynomial.atlas_variable_name == "Knot Atlas-comparable A2 variable q_atlas"
    assert presentation.polynomial.standard_polynomial_expression is None


def test_spin1_compact_presentation_never_claims_standard_colored_jones_identification() -> None:
    result = evaluate_catalog_result("trefoil", branch_ids=("sl2_spin1",), q=parse_q_text("q"))
    presentation = build_application_branch_presentation(result.branch_results[0], q_parameter_text="q")
    report = format_application_braid_compact_result(result, q_parameter_text="q")

    assert presentation.polynomial.standard_polynomial_expression is None
    assert "Standard Jones variable t" not in report
    assert "no final standard colored-Jones variable identification" in presentation.concise_variable_label
