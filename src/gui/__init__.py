"""GUI helpers for the multibranch invariant frontend entrypoint."""

from .braid_preview_renderer import build_braid_preview_geometry, render_braid_preview
from .demo_launcher import (
    DemoLauncherApp,
    build_custom_braid_word,
    build_entry_summary,
    build_program_status_text,
    evaluate_gui_example,
    evaluate_gui_custom_braid,
    filter_entry_by_branch_ids,
    get_default_gui_example_label,
    get_gui_branch_specs,
    get_gui_example_labels,
    get_gui_view_modes,
    launch_demo_gui,
    parse_generator_text,
    render_entry_report,
)
from .demo_launcher_legacy import LegacyDemoLauncherApp, launch_legacy_demo_gui

__all__ = [
    "DemoLauncherApp",
    "build_braid_preview_geometry",
    "build_custom_braid_word",
    "build_entry_summary",
    "build_program_status_text",
    "evaluate_gui_example",
    "evaluate_gui_custom_braid",
    "filter_entry_by_branch_ids",
    "get_default_gui_example_label",
    "get_gui_branch_specs",
    "get_gui_example_labels",
    "get_gui_view_modes",
    "launch_demo_gui",
    "LegacyDemoLauncherApp",
    "launch_legacy_demo_gui",
    "parse_generator_text",
    "render_braid_preview",
    "render_entry_report",
]