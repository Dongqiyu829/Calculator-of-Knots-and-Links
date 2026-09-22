"""Contract tests for frontend-neutral mathematical explanations."""

from __future__ import annotations

from src.services import (
    build_custom_rmatrix_explanation,
    build_invariant_explanation,
    build_catalog_braid_input,
    get_branch_explanation,
    list_evaluation_branches,
)


def test_branch_explanations_follow_the_service_status_catalog() -> None:
    for descriptor in list_evaluation_branches():
        explanation = get_branch_explanation(descriptor.branch_id)
        assert explanation.status == descriptor.status
        assert explanation.branch_statuses == ((descriptor.branch_id, descriptor.status),)
        assert explanation.title == descriptor.display_name
        assert explanation.normalization
        assert explanation.variable_convention
        assert explanation.output_name
        assert explanation.representation_dimension in {2, 3}


def test_branch_explanations_preserve_current_channel_and_normalization_facts() -> None:
    sl2 = get_branch_explanation("sl2_fundamental")
    assert any("unknot" in line.lower() for line in sl2.formula_lines)
    assert "q_atlas = q_project^2" in sl2.variable_convention

    sl3 = get_branch_explanation("sl3_fundamental")
    assert any("6 plus 3-bar" in line for line in sl3.formula_lines)
    assert "q_atlas = q_project^-1" in sl3.variable_convention

    spin1 = get_branch_explanation("sl2_spin1")
    assert any("q^4, -1, q^-2" in line for line in spin1.formula_lines)
    assert spin1.status == "candidate"
    assert any("candidate" in warning.lower() for warning in spin1.warnings)


def test_contextual_explanation_preserves_braid_metadata_and_selected_statuses() -> None:
    braid = build_catalog_braid_input("trefoil").braid_word
    explanation = build_invariant_explanation(braid, branch_ids=("sl2_fundamental", "sl2_spin1"), source_label="trefoil")
    assert explanation.status == "mixed"
    assert explanation.metadata["strand_count"] == 2
    assert explanation.metadata["writhe"] == 3
    assert explanation.metadata["generators"] == [1, 1, 1]
    assert explanation.branch_statuses == (("sl2_fundamental", "formal"), ("sl2_spin1", "candidate"))
    assert any("generator order" in detail for detail in explanation.details)


def test_custom_explanation_keeps_operator_only_boundary_and_relation_status() -> None:
    explanation = build_custom_rmatrix_explanation("check-R", relation_status="failed")
    assert explanation.status == "operator-only"
    assert explanation.operator_only is True
    assert "check-R = P R" in explanation.formula_lines[0]
    assert any("not a validated braid-group representation" in warning for warning in explanation.warnings)
    assert explanation.metadata["relation_status"] == "failed"
