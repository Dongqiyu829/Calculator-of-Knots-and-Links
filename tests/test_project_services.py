"""Contract tests for curated examples and deterministic project documents."""

from __future__ import annotations

import json

import pytest

from src.services import (
    ProjectFileError,
    ProjectSchemaError,
    ProjectValidationError,
    build_custom_rmatrix_project,
    build_invariant_project,
    get_curated_example,
    list_curated_examples,
    parse_project,
    serialize_project,
)


def test_curated_examples_have_unique_ids_valid_categories_and_statuses() -> None:
    examples = list_curated_examples()
    assert len({example.example_id for example in examples}) == len(examples)
    assert {example.category for example in examples} == {"knots_links", "braid_demonstration", "custom_rmatrix"}
    assert {example.mathematical_status for example in examples} <= {"formal", "candidate", "diagnostic", "negative_control"}
    assert any(example.mathematical_status == "candidate" for example in examples)
    assert {"catalog.figure_eight", "knot.5_1", "knot.5_2"} <= {example.example_id for example in examples}
    negative = get_curated_example("rmatrix.diagonal_negative_control")
    assert negative.mathematical_status == "negative_control"
    assert negative.input_kind == "check-R"


def test_invariant_project_round_trip_is_deterministic_and_preserves_text() -> None:
    document = build_invariant_project(
        source_mode="custom",
        num_strands=3,
        generator_text="1, -2, 1",
        custom_label="saved setup",
        custom_notes="do not evaluate on load",
        q_text="q",
        branch_ids=["sl2_fundamental", "sl2_spin1"],
    )
    serialized = serialize_project(document)
    assert serialized == serialize_project(parse_project(serialized))
    payload = json.loads(serialized)
    assert payload["schema_version"] == 1
    assert payload["workflow"] == "invariant"
    assert payload["input"]["generator_text"] == "1, -2, 1"
    assert payload["input"]["q_text"] == "q"
    assert "computation_backend" not in payload["input"]  # Older schema-1 documents remain unchanged.


def test_optional_invariant_backend_round_trip_and_legacy_compatibility() -> None:
    document = build_invariant_project(
        source_mode="catalog",
        example_label="trefoil",
        branch_ids=["sl2_fundamental"],
        computation_backend="temperley_lieb",
    )
    restored = parse_project(serialize_project(document))
    assert restored.schema_version == 1
    assert restored.input_data["computation_backend"] == "temperley_lieb"
    assert serialize_project(restored) == serialize_project(document)
    legacy = document.to_dict()
    del legacy["input"]["computation_backend"]
    old_document = parse_project(json.dumps(legacy))
    assert "computation_backend" not in old_document.input_data


@pytest.mark.parametrize("backend", ("unknown", "temperley_lieb"))
def test_invariant_project_rejects_invalid_or_incompatible_backend(backend) -> None:
    with pytest.raises(ProjectValidationError, match="backend|sl2_fundamental"):
        build_invariant_project(
            source_mode="catalog",
            example_label="trefoil",
            branch_ids=["sl3_fundamental"],
            computation_backend=backend,
        )


def test_custom_rmatrix_project_round_trip_preserves_raw_vs_check_r_and_symbolic_text() -> None:
    document = build_custom_rmatrix_project(
        matrix_text="[[q,0,0,0],[0,0,1,0],[0,1,q - 1/q,0],[0,0,0,q]]",
        input_kind="check-R",
        local_dimension=2,
        check_braid_relation=True,
        num_strands=2,
        generator_text="1 -1",
    )
    restored = parse_project(serialize_project(document))
    assert restored.workflow == "custom_rmatrix"
    assert restored.input_data["input_kind"] == "check-R"
    assert restored.input_data["matrix_text"] == document.input_data["matrix_text"]
    assert restored.input_data["generator_text"] == "1 -1"


def test_project_errors_are_typed_and_version_mismatch_is_informational() -> None:
    with pytest.raises(ProjectFileError):
        parse_project("{not json")
    with pytest.raises(ProjectSchemaError):
        parse_project(json.dumps({"schema_version": 99, "application": "Calculator of Knots and Links", "application_version": "0.1.0", "workflow": "invariant", "input": {}, "ui_state": {}}))
    with pytest.raises(ProjectValidationError):
        build_invariant_project(source_mode="custom", num_strands=1, generator_text="1")
    document = build_invariant_project(source_mode="catalog", example_label="unknot_1", branch_ids=["sl2_fundamental"])
    payload = document.to_dict()
    payload["application_version"] = "9.9.9"
    restored = parse_project(json.dumps(payload))
    assert restored.application_version_mismatch is True


def test_formal_curated_examples_do_not_recommend_candidate_branches() -> None:
    examples = list_curated_examples()
    formal_examples = [example for example in examples if example.workflow == "invariant" and example.mathematical_status == "formal"]
    assert formal_examples
    for example in formal_examples:
        assert "sl2_spin1" not in example.recommended_branches
        assert set(example.recommended_branches) <= {"sl2_fundamental", "sl3_fundamental"}


def test_project_write_failure_is_typed(tmp_path) -> None:
    from src.services import save_project_file

    document = build_invariant_project(source_mode="catalog", example_label="unknot_1", branch_ids=["sl2_fundamental"])
    with pytest.raises(ProjectFileError):
        save_project_file(tmp_path / "missing" / "project.knotcalc.json", document)
