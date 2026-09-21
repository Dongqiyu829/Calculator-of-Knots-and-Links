"""Central test-tier classification for the recovered historical suite.

Markers live here rather than in the authoritative test files so recovery keeps
their source bodies intact.  A test may belong to both tiers: GUI tests can also
exercise expensive symbolic mathematical paths.
"""

from __future__ import annotations

from pathlib import Path

import pytest


GUI_TEST_FILES = frozenset(
    {
        "test_braid_preview_renderer_smoke.py",
        "test_braid_workbench_comparison_smoke.py",
        "test_braid_workbench_gui_smoke.py",
        "test_experiment_log_smoke.py",
        "test_gui_builtin_preview_sync.py",
        "test_gui_custom_vs_branch_evaluator.py",
        "test_gui_dataflow_smoke.py",
        "test_legacy_fast_program_smoke.py",
        "test_workbench_input_parity.py",
        "test_workbench_input_schema_smoke.py",
    }
)

SLOW_TEST_FILES = frozenset(
    {
        "test_branch_formatter_smoke.py",
        "test_eyb_stabilization_regression.py",
        "test_gui_custom_vs_branch_evaluator.py",
        "test_gui_dataflow_smoke.py",
        "test_jones_debug_smoke.py",
        "test_multibranch_benchmark_smoke.py",
        "test_sl2_3d_candidate_catalog_regression.py",
        "test_sl2_3d_candidate_smoke.py",
        "test_sl2_3d_knot_atlas_correspondence.py",
        "test_sl2_jones_compatible_regression.py",
    }
)


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Apply stable tiers by file without altering recovered test source."""

    for item in items:
        filename = Path(str(item.fspath)).name
        if filename in GUI_TEST_FILES:
            item.add_marker(pytest.mark.gui)
        if filename in SLOW_TEST_FILES:
            item.add_marker(pytest.mark.slow)
