"""Contract tests for the UI-independent braid evaluation service."""

from __future__ import annotations

import sympy as sp

from src.gui.demo_launcher import evaluate_gui_braid_word, evaluate_gui_example
from src.services.braid_evaluation import (
    build_catalog_braid_input,
    build_custom_braid_input,
    evaluate_braid_input,
    evaluate_braid_word,
    evaluate_catalog_example,
    evaluate_custom_braid,
    parse_generator_text,
)


FAST_Q = sp.Integer(2)


def test_catalog_evaluation_preserves_recovered_metadata_and_results() -> None:
    entry = evaluate_catalog_example("trefoil", branch_ids=("sl2_fundamental", "sl3_fundamental"), q=FAST_Q)

    assert entry.example_label == "trefoil"
    assert entry.metadata["input_mode"] == "catalog"
    assert entry.metadata["selected_branch_ids"] == ["sl2_fundamental", "sl3_fundamental"]
    assert entry.metadata["expected_components"] == 1
    assert entry.metadata["expected_crossing_count"] == 3
    assert [result.branch_id for result in entry.branch_results] == ["sl2_fundamental", "sl3_fundamental"]
    assert [str(sp.simplify(result.primary_output)) for result in entry.branch_results] == ["67/256", "5691/16384"]


def test_custom_evaluation_parsing_branch_selection_and_q_propagation() -> None:
    assert parse_generator_text("1, -2 1 -2") == (1, -2, 1, -2)
    entry = evaluate_custom_braid(3, "1 -2 1 -2", branch_ids=("sl2_fundamental",), q=FAST_Q)

    assert entry.metadata["input_mode"] == "custom"
    assert entry.metadata["selected_branch_ids"] == ["sl2_fundamental"]
    assert entry.branch_results[0].branch_id == "sl2_fundamental"
    assert sp.simplify(entry.branch_results[0].primary_output - sp.Rational(205, 16)) == 0


def test_input_state_and_gui_adapters_share_the_same_service_results() -> None:
    catalog_state = build_catalog_braid_input("trefoil")
    custom_state = build_custom_braid_input(2, "1 1 1")

    assert catalog_state.source_mode == "catalog"
    assert custom_state.source_mode == "custom"
    assert evaluate_braid_input(catalog_state, branch_ids=("sl2_fundamental",), q=FAST_Q) == evaluate_gui_example(
        "trefoil", branch_ids=("sl2_fundamental",), q=FAST_Q
    )
    assert evaluate_braid_word(custom_state.braid_word, branch_ids=("sl2_fundamental",), q=FAST_Q) == evaluate_gui_braid_word(
        custom_state.braid_word, branch_ids=("sl2_fundamental",), q=FAST_Q
    )
