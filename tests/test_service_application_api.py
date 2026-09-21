"""Public API, branch-catalog, and structured-error checks for services."""

from __future__ import annotations

import pytest

import src.services as services
from src.gui.demo_launcher import get_gui_branch_specs
from src.services import (
    BraidInputValidationError,
    GeneratorParseError,
    UnknownCatalogExampleError,
    UnknownEvaluationBranchError,
    UnknownEvaluationModelError,
    build_custom_braid_word,
    evaluate_catalog_example,
    get_evaluation_branch,
    get_evaluation_model,
    list_evaluation_branches,
    parse_generator_text,
)
from src.workbench.specs import WORKBENCH_DEFAULT_MODELS, WORKBENCH_MODEL_SPECS


def test_supported_service_api_is_explicit_and_narrow() -> None:
    assert set(services.__all__) == {
        "ApplicationServiceError",
        "BraidInputError",
        "BraidInputState",
        "BraidInputValidationError",
        "DEFAULT_EVALUATION_MODEL_IDS",
        "EvaluationBranchDescriptor",
        "GeneratorParseError",
        "UnknownCatalogExampleError",
        "UnknownEvaluationBranchError",
        "UnknownEvaluationModelError",
        "branch_ids_for_models",
        "build_catalog_braid_input",
        "build_custom_braid_input",
        "build_custom_braid_word",
        "evaluate_braid_input",
        "evaluate_braid_word",
        "evaluate_catalog_example",
        "evaluate_custom_braid",
        "get_evaluation_branch",
        "get_evaluation_model",
        "list_evaluation_branches",
        "parse_generator_text",
    }


def test_branch_catalog_is_the_shared_source_for_workbench_and_gui() -> None:
    catalog = list_evaluation_branches()
    assert [(item.model_id, item.branch_id, item.status) for item in catalog] == [
        ("sl2_fundamental", "sl2_fundamental", "formal"),
        ("sl2_3d_9x9", "sl2_spin1", "candidate"),
        ("sl3_fundamental", "sl3_fundamental", "formal"),
    ]
    assert WORKBENCH_DEFAULT_MODELS == tuple(item.model_id for item in catalog)
    assert tuple(WORKBENCH_MODEL_SPECS.values()) == catalog
    gui_specs = {item.branch_id: item for item in get_gui_branch_specs()}
    for descriptor in catalog:
        gui_spec = gui_specs[descriptor.branch_id]
        assert gui_spec.title == descriptor.display_name
        assert gui_spec.subtitle == descriptor.user_note


def test_service_translates_frontend_input_errors() -> None:
    with pytest.raises(GeneratorParseError, match="Generators must be integers"):
        parse_generator_text("1 nope -2")
    with pytest.raises(BraidInputValidationError, match="Generator 0 is not valid"):
        build_custom_braid_word(2, "0")
    with pytest.raises(UnknownCatalogExampleError, match="Unknown catalog example"):
        evaluate_catalog_example("not_a_catalog_label")
    with pytest.raises(UnknownEvaluationBranchError, match="Unknown evaluation branch"):
        evaluate_catalog_example("trefoil", branch_ids=("not_a_branch",))
    with pytest.raises(UnknownEvaluationModelError, match="Unknown evaluation model"):
        get_evaluation_model("not_a_model")
    assert get_evaluation_branch("sl2_spin1").status == "candidate"
