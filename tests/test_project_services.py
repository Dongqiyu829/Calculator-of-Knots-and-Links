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
