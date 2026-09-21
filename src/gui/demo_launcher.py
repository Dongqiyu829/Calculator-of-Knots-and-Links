"""Tkinter GUI entrypoint for the current multi-branch invariant program skeleton."""

from __future__ import annotations

import argparse
import json
import tkinter as tk
from dataclasses import dataclass
from tkinter import messagebox, ttk
from typing import Any

import sympy as sp

from src.braid.braid_word import BraidWord
from src.catalog.braid_examples import get_braid_example
from src.gui.braid_preview_renderer import render_braid_preview
from src.invariants.branch_formatter import (
    format_branch_result,
    format_catalog_benchmark,
    format_multibranch_entry,
)
from src.invariants.branch_results import InvariantBranchResult
from src.invariants.multibranch_benchmark import MultiBranchBenchmarkEntry
from src.invariants.sl2_3d_colored_jones_candidate import (
    SL2_3D_KNOT_ATLAS_COMPARISON_RULE,
    SL2_3D_KNOT_ATLAS_FIVE_ONE_RELATION,
    SL2_3D_KNOT_ATLAS_SCOPE_NOTE,
    SL2_3D_KNOT_ATLAS_TREFOIL_RELATION,
    SL2_3D_KNOT_ATLAS_VERIFICATION_NOTE,
)
from src.services import braid_evaluation as braid_service


APP_BACKGROUND = "#f3f6fb"
SURFACE_BACKGROUND = "#ffffff"
SURFACE_SUBTLE = "#f8fbff"
TEXT_COLOR = "#0f172a"
MUTED_TEXT_COLOR = "#475569"
BORDER_COLOR = "#d6deeb"
ACCENT_COLOR = "#2563eb"
ACCENT_COLOR_ACTIVE = "#1d4ed8"
SUCCESS_COLOR = "#0f766e"
EXPLORATORY_COLOR = "#7c3aed"

DEFAULT_GUI_EXAMPLE_LABEL = "trefoil"
GUI_EXAMPLE_LABELS = ("unknot_1", "trefoil", "figure_eight")
GUI_VIEW_MODES = ("formatter", "raw")
DEFAULT_CUSTOM_STRANDS = 3
MAX_CUSTOM_STRANDS = 16
GENERATOR_BUTTON_GROUPS_PER_ROW = 4


@dataclass(frozen=True, slots=True)
class GuiBranchSpec:
    """Describe one branch toggle and card heading used by the GUI."""

    branch_id: str
    title: str
    subtitle: str
    accent_color: str
    user_hint: str


GuiActiveBraidState = braid_service.BraidInputState


GUI_BRANCH_SPECS = (
    GuiBranchSpec(
        branch_id="sl2_fundamental",
        title="Jones / sl2 fundamental",
        subtitle="Use this branch when you want the current Jones-compatible polynomial.",
        accent_color=ACCENT_COLOR,
        user_hint="Primary output here = current Jones-compatible comparison output.",
    ),
    GuiBranchSpec(
        branch_id="sl3_fundamental",
        title="sl3 fundamental",
        subtitle="Current formal sl3 branch for cross-Lie-algebra comparison.",
        accent_color=SUCCESS_COLOR,
        user_hint="Primary output here = current formal sl3 comparison branch.",
    ),
    GuiBranchSpec(
        branch_id="sl2_spin1",
        title="sl2 的3维表示下的9x9矩阵",
        subtitle=(
            "当前这条线是 colored Jones candidate branch；Knot Atlas 用 J_n 表示 (n+1) 维 sl2 表示，所以这里当前对照的是 n=2 数据。"
        ),
        accent_color=EXPLORATORY_COLOR,
        user_hint=(
            "当前已确认 3_1 对应 q^6 J_2(3_1; q^2)、5_1 对应 q^10 J_2(5_1; q^2)；5_2 仍在 verification，且全局最终归一化尚未定案。"
        ),
    ),
)

PROGRAM_STATUS_TEXT = (
    "Quick start:\n"
    "1. Choose a built-in example or switch to Custom braid.\n"
    "2. For a custom braid, set the strand count and enter generators such as 1 1 -2 3.\n"
    "3. Click Evaluate example or Apply custom braid to compute invariants.\n\n"
    "How to read the outputs:\n"
    "- Jones / sl2 fundamental: current Jones-compatible branch.\n"
    "- sl3 fundamental: current formal sl3 comparison branch.\n"
    "- sl2 的3维表示下的9x9矩阵: colored Jones candidate branch with RT / quantum-trace candidate normalization.\n\n"
    "Current Knot Atlas comparison wording:\n"
    f"- {SL2_3D_KNOT_ATLAS_COMPARISON_RULE}\n"
    f"- {SL2_3D_KNOT_ATLAS_TREFOIL_RELATION}\n"
    f"- {SL2_3D_KNOT_ATLAS_FIVE_ONE_RELATION}\n"
    f"- {SL2_3D_KNOT_ATLAS_SCOPE_NOTE}\n"
    f"- {SL2_3D_KNOT_ATLAS_VERIFICATION_NOTE}\n\n"
    "The GUI is only a frontend over the existing evaluator. It does not add new normalization rules by itself."
)


def get_gui_example_labels() -> tuple[str, ...]:
    """Return the built-in catalog examples shown by the GUI."""

    return GUI_EXAMPLE_LABELS


def get_default_gui_example_label() -> str:
    """Return the default catalog example opened by the GUI."""

    return DEFAULT_GUI_EXAMPLE_LABEL


def get_gui_branch_specs() -> tuple[GuiBranchSpec, ...]:
    """Return the branch toggle definitions used by the GUI."""

    return GUI_BRANCH_SPECS


def get_gui_view_modes() -> tuple[str, ...]:
    """Return the report view modes supported by the GUI."""

    return GUI_VIEW_MODES


def build_program_status_text() -> str:
    """Return the program-status text shown in the GUI."""

    return PROGRAM_STATUS_TEXT


def parse_generator_text(generator_text: str) -> tuple[int, ...]:
    """Compatibility adapter for the shared application input parser."""

    return braid_service.parse_generator_text(generator_text)


def build_custom_braid_word(
    num_strands: int,
    generator_text: str,
    *,
    label: str = "custom_braid",
    notes: str = "Custom braid created from the GUI input panel.",
) -> BraidWord:
    """Compatibility adapter for shared custom-braid construction."""

    return braid_service.build_custom_braid_word(num_strands, generator_text, label=label, notes=notes)


def evaluate_gui_example(
    example_label: str,
    *,
    branch_ids: tuple[str, ...] | list[str] | None = None,
    q: sp.Expr | None = None,
) -> MultiBranchBenchmarkEntry:
    """Compatibility adapter for shared catalog evaluation."""

    return braid_service.evaluate_catalog_example(example_label, branch_ids=branch_ids, q=q)


def evaluate_gui_braid_word(
    braid_word: BraidWord,
    *,
    branch_ids: tuple[str, ...] | list[str] | None = None,
    q: sp.Expr | None = None,
) -> MultiBranchBenchmarkEntry:
    """Compatibility adapter for shared arbitrary-braid evaluation."""

    return braid_service.evaluate_braid_word(braid_word, branch_ids=branch_ids, q=q)


def evaluate_gui_custom_braid(
    num_strands: int,
    generator_text: str,
    *,
    branch_ids: tuple[str, ...] | list[str] | None = None,
    q: sp.Expr | None = None,
) -> MultiBranchBenchmarkEntry:
    """Compatibility adapter for shared custom-braid evaluation."""

    return braid_service.evaluate_custom_braid(num_strands, generator_text, branch_ids=branch_ids, q=q)


def build_catalog_active_braid_state(example_label: str) -> GuiActiveBraidState:
    """Compatibility adapter for shared catalog input metadata."""

    return braid_service.build_catalog_braid_input(example_label)


def build_custom_active_braid_state(num_strands: int, generator_text: str) -> GuiActiveBraidState:
    """Compatibility adapter for shared custom input metadata."""

    return braid_service.build_custom_braid_input(num_strands, generator_text)


def evaluate_gui_active_braid(
    active_braid: GuiActiveBraidState,
    *,
    branch_ids: tuple[str, ...] | list[str] | None = None,
    q: sp.Expr | None = None,
) -> MultiBranchBenchmarkEntry:
    """Compatibility adapter for shared input-state evaluation."""

    return braid_service.evaluate_braid_input(active_braid, branch_ids=branch_ids, q=q)


def _braid_word_from_entry(entry: MultiBranchBenchmarkEntry) -> BraidWord:
    return braid_service.braid_word_from_entry(entry)


def build_active_braid_state_from_entry(entry: MultiBranchBenchmarkEntry) -> GuiActiveBraidState:
    """Recover the shared input state from one evaluated entry for rendering."""

    return braid_service.braid_input_from_entry(entry)


def build_active_braid_preview_metadata(active_braid: GuiActiveBraidState) -> dict[str, Any]:
    """Return the active braid metadata that the GUI preview and summary must agree on."""

    return {
        "source_mode": active_braid.source_mode,
        "label": active_braid.source_label,
        "num_strands": active_braid.braid_word.num_strands,
        "generators": list(active_braid.braid_word.generators),
        "word_string": active_braid.braid_word.word_string(),
        "crossings_count": len(active_braid.braid_word.generators),
        "writhe": active_braid.braid_word.writhe(),
        "expected_components": active_braid.expected_components,
        "expected_crossing_count": active_braid.expected_crossing_count,
        "notes": active_braid.notes,
    }


def build_active_braid_summary(
    active_braid: GuiActiveBraidState,
    *,
    footer_lines: tuple[str, ...] = (),
) -> str:
    """Build a summary block for either an evaluated or pending GUI braid state."""

    braid_word = active_braid.braid_word
    preview_metadata = build_active_braid_preview_metadata(active_braid)
    lines = [
        f"Source mode: {preview_metadata['source_mode']}",
        f"Label: {preview_metadata['label']}",
        f"Number of strands: {braid_word.num_strands}",
        f"Generators: {list(braid_word.generators)}",
        f"Crossings: {preview_metadata['crossings_count']}",
        f"Word: {preview_metadata['word_string']}",
        f"Writhe: {preview_metadata['writhe']}",
    ]
    if preview_metadata["expected_components"] is not None:
        lines.append(f"Expected components: {preview_metadata['expected_components']}")
    if preview_metadata["expected_crossing_count"] is not None:
        lines.append(f"Expected crossing count: {preview_metadata['expected_crossing_count']}")
    if preview_metadata["notes"]:
        lines.append(f"Notes: {preview_metadata['notes']}")
    if footer_lines:
        lines.extend(("", *footer_lines))
    return "\n".join(lines)


def filter_entry_by_branch_ids(
    entry: MultiBranchBenchmarkEntry,
    branch_ids: tuple[str, ...] | list[str],
) -> MultiBranchBenchmarkEntry:
    """Filter one multi-branch entry down to the branch ids currently visible in the GUI."""

    selected = set(branch_ids)
    return MultiBranchBenchmarkEntry(
        example_label=entry.example_label,
        branch_results=tuple(result for result in entry.branch_results if result.branch_id in selected),
        notes=entry.notes,
        metadata=dict(entry.metadata),
    )


def render_entry_report(entry: MultiBranchBenchmarkEntry, *, view_mode: str = "formatter") -> str:
    """Render one entry either as formatter text or raw structured data."""

    if view_mode == "formatter":
        return format_catalog_benchmark((entry,))
    if view_mode == "raw":
        return json.dumps(entry.to_dict(), indent=2, ensure_ascii=False)
    raise ValueError(f"Unknown GUI view mode: {view_mode}")


def build_entry_summary(entry: MultiBranchBenchmarkEntry) -> str:
    """Build a short summary block for the current GUI selection."""

    active_braid = build_active_braid_state_from_entry(entry)
    return build_active_braid_summary(
        active_braid,
        footer_lines=(
            "How to read the current outputs:",
            "- Jones-compatible polynomial: read the primary output in Jones / sl2 fundamental.",
            "- sl3 comparison output: read the primary output in sl3 fundamental.",
            "- sl2 3D candidate output: read the primary output in sl2 的3维表示下的9x9矩阵.",
            f"- {SL2_3D_KNOT_ATLAS_COMPARISON_RULE}",
            f"- {SL2_3D_KNOT_ATLAS_TREFOIL_RELATION}",
            f"- {SL2_3D_KNOT_ATLAS_FIVE_ONE_RELATION}",
            f"- {SL2_3D_KNOT_ATLAS_VERIFICATION_NOTE}",
        ),
    )


class DemoLauncherApp:
    """Tkinter application wired to the current multi-branch invariant program."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.q = sp.Symbol("q", nonzero=True)
        self.input_mode_var = tk.StringVar(value="catalog")
        self.example_var = tk.StringVar(value=get_default_gui_example_label())
        self.custom_num_strands_var = tk.IntVar(value=DEFAULT_CUSTOM_STRANDS)
        self.custom_generators_var = tk.StringVar(value="")
        self.view_mode_var = tk.StringVar(value="formatter")
        self.status_var = tk.StringVar(value="Ready.")
        self.entry_cache: dict[str, MultiBranchBenchmarkEntry] = {}
        self.branch_vars = {
            spec.branch_id: tk.BooleanVar(value=True)
            for spec in get_gui_branch_specs()
        }
        self.report_text: tk.Text
        self.summary_text: tk.Text
        self.cards_container: ttk.Frame
        self.cards_canvas: tk.Canvas
        self.preview_canvas: tk.Canvas
        self.generator_button_frame: ttk.Frame
        self.overview_container: ttk.Frame
        self.main_canvas: tk.Canvas
        self._main_window_item: int
        self.current_full_entry: MultiBranchBenchmarkEntry | None = None
        self.current_visible_entry: MultiBranchBenchmarkEntry | None = None
        self.current_active_braid: GuiActiveBraidState | None = None
        self._configure_styles()
        self._build_ui()
        self._rebuild_generator_button_panel()
        self._render_pending_state(
            "No braid has been evaluated yet. Choose a catalog example or finish a custom braid, then click Evaluate."
        )

    def _configure_styles(self) -> None:
        self.root.configure(background=APP_BACKGROUND)
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(".", background=APP_BACKGROUND, foreground=TEXT_COLOR)
        style.configure("App.TFrame", background=APP_BACKGROUND)
        style.configure("Surface.TLabelframe", background=SURFACE_BACKGROUND, bordercolor=BORDER_COLOR, relief="solid")
        style.configure("Surface.TLabelframe.Label", background=SURFACE_BACKGROUND, foreground=TEXT_COLOR, font=("Segoe UI", 11, "bold"))
        style.configure("Guide.TLabelframe", background=SURFACE_SUBTLE, bordercolor=BORDER_COLOR, relief="solid")
        style.configure("Guide.TLabelframe.Label", background=SURFACE_SUBTLE, foreground=TEXT_COLOR, font=("Segoe UI", 11, "bold"))
        style.configure("Hero.TFrame", background=SURFACE_BACKGROUND)
        style.configure("HeroTitle.TLabel", background=SURFACE_BACKGROUND, foreground=TEXT_COLOR, font=("Segoe UI Semibold", 22))
        style.configure("HeroSubtitle.TLabel", background=SURFACE_BACKGROUND, foreground=MUTED_TEXT_COLOR, font=("Segoe UI", 10))
        style.configure("Muted.TLabel", background=SURFACE_BACKGROUND, foreground=MUTED_TEXT_COLOR, font=("Segoe UI", 9))
        style.configure("GuideText.TLabel", background=SURFACE_SUBTLE, foreground=MUTED_TEXT_COLOR, font=("Segoe UI", 10))
        style.configure("Status.TLabel", background=APP_BACKGROUND, foreground=ACCENT_COLOR, font=("Segoe UI Semibold", 10))
        style.configure("Primary.TButton", background=ACCENT_COLOR, foreground="#ffffff", padding=(12, 8), borderwidth=0)
        style.map("Primary.TButton", background=[("active", ACCENT_COLOR_ACTIVE), ("pressed", ACCENT_COLOR_ACTIVE)])
        style.configure("Secondary.TButton", background=SURFACE_SUBTLE, foreground=TEXT_COLOR, padding=(10, 8), bordercolor=BORDER_COLOR)
        style.map("Secondary.TButton", background=[("active", "#eef4ff")])
        style.configure("Chip.TRadiobutton", background=SURFACE_BACKGROUND, foreground=TEXT_COLOR, font=("Segoe UI", 10))
        style.configure("Chip.TCheckbutton", background=SURFACE_BACKGROUND, foreground=TEXT_COLOR, font=("Segoe UI", 10))

    def _build_ui(self) -> None:
        self.root.title("Quantum Group Knot Multibranch GUI")
        self.root.geometry("1420x940")
        self.root.minsize(1160, 760)

        shell = ttk.Frame(self.root, style="App.TFrame")
        shell.pack(fill=tk.BOTH, expand=True)

        self.main_canvas = tk.Canvas(shell, background=APP_BACKGROUND, highlightthickness=0)
        main_scrollbar = ttk.Scrollbar(shell, orient=tk.VERTICAL, command=self.main_canvas.yview)
        self.main_canvas.configure(yscrollcommand=main_scrollbar.set)
        self.main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        main_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        container = ttk.Frame(self.main_canvas, padding=16, style="App.TFrame")
        self._main_window_item = self.main_canvas.create_window((0, 0), window=container, anchor="nw")
        container.bind("<Configure>", self._sync_main_scroll_region)
        self.main_canvas.bind("<Configure>", self._sync_main_viewport_width)

        hero_frame = ttk.Frame(container, padding=16, style="Hero.TFrame")
        hero_frame.pack(fill=tk.X, pady=(0, 12))
        ttk.Label(hero_frame, text="Quantum Group Knot Multibranch Studio", style="HeroTitle.TLabel").pack(anchor=tk.W)
        ttk.Label(
            hero_frame,
            text=(
                "Build a braid, run the current sl2/sl3 branches, and read the main outputs without leaving the GUI. "
                "If you want the current Jones-compatible polynomial, look at the Jones / sl2 fundamental branch."
            ),
            wraplength=1280,
            justify=tk.LEFT,
            style="HeroSubtitle.TLabel",
        ).pack(anchor=tk.W, pady=(6, 0))

        controls_row = ttk.Panedwindow(container, orient=tk.HORIZONTAL)
        controls_row.pack(fill=tk.BOTH, expand=False)

        input_frame = ttk.LabelFrame(controls_row, text="Braid input", padding=10, style="Surface.TLabelframe")
        controls_row.add(input_frame, weight=7)

        mode_row = ttk.Frame(input_frame)
        mode_row.pack(fill=tk.X)
        ttk.Radiobutton(
            mode_row,
            text="Catalog example",
            value="catalog",
            variable=self.input_mode_var,
            command=self._on_input_mode_changed,
            style="Chip.TRadiobutton",
        ).pack(side=tk.LEFT)
        ttk.Radiobutton(
            mode_row,
            text="Custom braid",
            value="custom",
            variable=self.input_mode_var,
            command=self._on_input_mode_changed,
            style="Chip.TRadiobutton",
        ).pack(side=tk.LEFT, padx=(10, 0))

        catalog_frame = ttk.Frame(input_frame)
        catalog_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Label(catalog_frame, text="Built-in example:").grid(row=0, column=0, sticky="w")
        self.example_box = ttk.Combobox(
            catalog_frame,
            textvariable=self.example_var,
            values=get_gui_example_labels(),
            state="readonly",
            width=18,
        )
        self.example_box.grid(row=0, column=1, sticky="w", padx=(8, 8))
        self.example_box.bind("<<ComboboxSelected>>", self._on_example_changed)
        ttk.Button(catalog_frame, text="Evaluate example", command=self._apply_catalog_example, style="Primary.TButton").grid(
            row=0,
            column=2,
            sticky="w",
        )
        ttk.Button(catalog_frame, text="Load into custom", command=self._load_example_into_custom, style="Secondary.TButton").grid(
            row=0,
            column=3,
            sticky="w",
            padx=(8, 0),
        )
        ttk.Label(
            catalog_frame,
            text=(
                "Built-in examples are only evaluated when you click 'Evaluate example'. "
                "You can also load one into the custom editor and continue editing."
            ),
            wraplength=640,
            justify=tk.LEFT,
        ).grid(row=1, column=0, columnspan=4, sticky="w", pady=(6, 0))

        custom_frame = ttk.LabelFrame(input_frame, text="Custom braid editor", padding=8, style="Guide.TLabelframe")
        custom_frame.pack(fill=tk.X, pady=(10, 0))

        editor_row = ttk.Frame(custom_frame)
        editor_row.pack(fill=tk.X)
        ttk.Label(editor_row, text="Strands:").grid(row=0, column=0, sticky="w")
        self.strands_spinbox = ttk.Spinbox(
            editor_row,
            from_=1,
            to=MAX_CUSTOM_STRANDS,
            textvariable=self.custom_num_strands_var,
            width=6,
            command=self._on_custom_strands_changed,
        )
        self.strands_spinbox.grid(row=0, column=1, sticky="w", padx=(6, 12))
        ttk.Label(editor_row, text="Generators:").grid(row=0, column=2, sticky="w")
        self.custom_generators_entry = ttk.Entry(editor_row, textvariable=self.custom_generators_var, width=38)
        self.custom_generators_entry.grid(row=0, column=3, sticky="ew", padx=(6, 8))
        self.custom_generators_entry.bind("<KeyRelease>", self._on_custom_generators_edited)
        self.custom_generators_entry.bind("<Return>", self._apply_custom_braid_event)
        ttk.Button(editor_row, text="Apply custom braid", command=self._apply_custom_braid, style="Primary.TButton").grid(
            row=0,
            column=4,
            sticky="w",
        )
        editor_row.columnconfigure(3, weight=1)

        toolbar_row = ttk.Frame(custom_frame)
        toolbar_row.pack(fill=tk.X, pady=(8, 0))
        ttk.Button(toolbar_row, text="Undo last", command=self._remove_last_generator, style="Secondary.TButton").pack(side=tk.LEFT)
        ttk.Button(toolbar_row, text="Clear", command=self._clear_custom_generators, style="Secondary.TButton").pack(side=tk.LEFT, padx=(8, 0))
        ttk.Label(
            toolbar_row,
            text=(
                "Manual input accepts space- or comma-separated Artin generators such as: "
                "1 1 -2 3 -4. The GUI only evaluates after you click Apply or press Enter."
            ),
            style="Muted.TLabel",
        ).pack(side=tk.LEFT, padx=(12, 0))

        self.generator_button_frame = ttk.Frame(custom_frame)
        self.generator_button_frame.pack(fill=tk.X, pady=(8, 0))

        preview_frame = ttk.LabelFrame(custom_frame, text="Active braid preview", padding=6, style="Surface.TLabelframe")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(8, 0))
        preview_container = ttk.Frame(preview_frame)
        preview_container.pack(fill=tk.BOTH, expand=True)
        self.preview_canvas = tk.Canvas(preview_container, height=220, background="#fafafa", highlightthickness=1)
        preview_y_scrollbar = ttk.Scrollbar(preview_container, orient=tk.VERTICAL, command=self.preview_canvas.yview)
        preview_x_scrollbar = ttk.Scrollbar(preview_frame, orient=tk.HORIZONTAL, command=self.preview_canvas.xview)
        self.preview_canvas.configure(xscrollcommand=preview_x_scrollbar.set, yscrollcommand=preview_y_scrollbar.set)
        self.preview_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        preview_y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        preview_x_scrollbar.pack(fill=tk.X, pady=(6, 0))

        branch_frame = ttk.LabelFrame(controls_row, text="Visible branches", padding=10, style="Surface.TLabelframe")
        controls_row.add(branch_frame, weight=2)
        for spec in get_gui_branch_specs():
            ttk.Checkbutton(
                branch_frame,
                text=spec.title,
                variable=self.branch_vars[spec.branch_id],
                command=self._refresh_visible_results,
                style="Chip.TCheckbutton",
            ).pack(anchor=tk.W)
            ttk.Label(
                branch_frame,
                text=spec.user_hint,
                wraplength=250,
                justify=tk.LEFT,
                style="Muted.TLabel",
            ).pack(anchor=tk.W, pady=(0, 8))

        status_panel = ttk.LabelFrame(controls_row, text="Quick guide", padding=10, style="Guide.TLabelframe")
        controls_row.add(status_panel, weight=2)
        ttk.Label(
            status_panel,
            text=build_program_status_text(),
            wraplength=420,
            justify=tk.LEFT,
            style="GuideText.TLabel",
        ).pack(anchor=tk.W)

        content_panes = ttk.Panedwindow(container, orient=tk.VERTICAL)
        content_panes.pack(fill=tk.BOTH, expand=True, pady=(12, 0))

        overview_frame = ttk.LabelFrame(content_panes, text="Polynomial overview", padding=8, style="Surface.TLabelframe")
        self.overview_container = ttk.Frame(overview_frame)
        self.overview_container.pack(fill=tk.X, expand=True)
        content_panes.add(overview_frame, weight=1)

        summary_frame = ttk.LabelFrame(content_panes, text="Active braid summary", padding=8, style="Surface.TLabelframe")
        self.summary_text = tk.Text(
            summary_frame,
            wrap=tk.WORD,
            height=7,
            font=("Cascadia Mono", 10),
            background=SURFACE_BACKGROUND,
            foreground=TEXT_COLOR,
            relief=tk.FLAT,
            highlightthickness=0,
            padx=8,
            pady=8,
            insertbackground=TEXT_COLOR,
        )
        summary_scrollbar = ttk.Scrollbar(summary_frame, orient=tk.VERTICAL, command=self.summary_text.yview)
        self.summary_text.configure(yscrollcommand=summary_scrollbar.set)
        self.summary_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        summary_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        content_panes.add(summary_frame, weight=1)

        results_panes = ttk.Panedwindow(content_panes, orient=tk.VERTICAL)
        content_panes.add(results_panes, weight=6)

        cards_frame = ttk.LabelFrame(results_panes, text="Branch result cards", padding=8, style="Surface.TLabelframe")
        report_frame = ttk.LabelFrame(results_panes, text="Report output", padding=8, style="Surface.TLabelframe")
        results_panes.add(cards_frame, weight=3)
        results_panes.add(report_frame, weight=2)

        self.cards_canvas = tk.Canvas(cards_frame, highlightthickness=0, background=APP_BACKGROUND)
        cards_scrollbar = ttk.Scrollbar(cards_frame, orient=tk.VERTICAL, command=self.cards_canvas.yview)
        self.cards_canvas.configure(yscrollcommand=cards_scrollbar.set)
        self.cards_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cards_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.cards_container = ttk.Frame(self.cards_canvas)
        self.cards_container.bind(
            "<Configure>",
            lambda _event: self.cards_canvas.configure(scrollregion=self.cards_canvas.bbox("all")),
        )
        self.cards_canvas.create_window((0, 0), window=self.cards_container, anchor="nw")

        report_toolbar = ttk.Frame(report_frame)
        report_toolbar.pack(fill=tk.X, pady=(0, 8))
        ttk.Button(report_toolbar, text="Copy current report", command=self._copy_current_report, style="Secondary.TButton").pack(side=tk.LEFT)
        ttk.Radiobutton(
            report_toolbar,
            text="Formatter view",
            value="formatter",
            variable=self.view_mode_var,
            command=self._refresh_report_view,
            style="Chip.TRadiobutton",
        ).pack(side=tk.LEFT, padx=(12, 0))
        ttk.Radiobutton(
            report_toolbar,
            text="Raw view",
            value="raw",
            variable=self.view_mode_var,
            command=self._refresh_report_view,
            style="Chip.TRadiobutton",
        ).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Label(
            report_toolbar,
            text="Toggle between shared formatter output and raw structured entry data.",
            style="Muted.TLabel",
        ).pack(side=tk.RIGHT)

        self.report_text = tk.Text(
            report_frame,
            wrap=tk.WORD,
            font=("Cascadia Mono", 10),
            height=12,
            background=SURFACE_BACKGROUND,
            foreground=TEXT_COLOR,
            relief=tk.FLAT,
            highlightthickness=0,
            padx=8,
            pady=8,
            insertbackground=TEXT_COLOR,
        )
        report_scrollbar = ttk.Scrollbar(report_frame, orient=tk.VERTICAL, command=self.report_text.yview)
        self.report_text.configure(yscrollcommand=report_scrollbar.set)
        self.report_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        report_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        ttk.Label(container, textvariable=self.status_var, style="Status.TLabel").pack(anchor=tk.E, pady=(8, 0))

        self.custom_num_strands_var.trace_add("write", self._on_custom_strands_trace)

    def _sync_main_scroll_region(self, _event: object) -> None:
        self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))

    def _sync_main_viewport_width(self, event: tk.Event[tk.Canvas]) -> None:
        self.main_canvas.itemconfigure(self._main_window_item, width=event.width)

    def _on_input_mode_changed(self) -> None:
        if self.input_mode_var.get() == "catalog":
            self._render_pending_state(
                "Catalog mode selected. Choose an example and click 'Evaluate example'.",
                preview_braid=build_catalog_active_braid_state(self.example_var.get()),
            )
            return
        self._render_pending_state(
            "Custom mode selected. Finish the braid, then click 'Apply custom braid'.",
            preview_braid=self._try_build_custom_active_braid(),
        )

    def _on_example_changed(self, _event: object) -> None:
        if self.input_mode_var.get() == "catalog":
            self._render_pending_state(
                "Catalog example changed. Click 'Evaluate example' to compute invariants.",
                preview_braid=build_catalog_active_braid_state(self.example_var.get()),
            )

    def _on_custom_strands_trace(self, *_args: object) -> None:
        self._on_custom_strands_changed()

    def _on_custom_strands_changed(self) -> None:
        self._rebuild_generator_button_panel()
        if self.input_mode_var.get() == "custom":
            self._render_pending_state(
                "Custom strand count updated. Edit the braid word, then click 'Apply custom braid'.",
                preview_braid=self._try_build_custom_active_braid(),
            )

    def _on_custom_generators_edited(self, _event: object) -> None:
        self._render_pending_state(
            "Custom generators edited. Press Enter or click 'Apply custom braid' to evaluate.",
            preview_braid=self._try_build_custom_active_braid(),
        )

    def _apply_catalog_example(self) -> None:
        """Evaluate the currently selected catalog example."""

        self.input_mode_var.set("catalog")
        self._refresh_view(show_errors=True)

    def _apply_custom_braid(self) -> None:
        """Validate and evaluate the currently edited custom braid."""

        self.input_mode_var.set("custom")
        self._refresh_view(show_errors=True)

    def _apply_custom_braid_event(self, _event: object) -> None:
        self._apply_custom_braid()

    def _append_generator(self, generator: int) -> None:
        current = self.custom_generators_var.get().strip()
        self.custom_generators_var.set(str(generator) if not current else f"{current} {generator}")
        self.input_mode_var.set("custom")
        self._render_pending_state(
            "Generator appended. Continue editing, then click 'Apply custom braid'.",
            preview_braid=self._try_build_custom_active_braid(),
        )

    def _remove_last_generator(self) -> None:
        try:
            generators = list(parse_generator_text(self.custom_generators_var.get()))
        except ValueError:
            self.custom_generators_var.set("")
        else:
            if generators:
                generators.pop()
            self.custom_generators_var.set(" ".join(str(item) for item in generators))
        self.input_mode_var.set("custom")
        self._render_pending_state(
            "Last generator removed. Click 'Apply custom braid' when the braid is ready.",
            preview_braid=self._try_build_custom_active_braid(),
        )

    def _clear_custom_generators(self) -> None:
        self.custom_generators_var.set("")
        self.input_mode_var.set("custom")
        self._render_pending_state(
            "Custom braid cleared. Enter generators, then click 'Apply custom braid'.",
            preview_braid=self._try_build_custom_active_braid(),
        )

    def _load_example_into_custom(self) -> None:
        example = get_braid_example(self.example_var.get())
        self.custom_num_strands_var.set(example.num_strands)
        self.custom_generators_var.set(" ".join(str(item) for item in example.generators))
        self.input_mode_var.set("custom")
        self._render_pending_state(
            "Built-in example loaded into the custom editor. Adjust it if needed, then click 'Apply custom braid'.",
            preview_braid=self._try_build_custom_active_braid(),
        )

    def _enabled_branch_ids(self) -> tuple[str, ...]:
        return tuple(
            spec.branch_id
            for spec in get_gui_branch_specs()
            if self.branch_vars[spec.branch_id].get()
        )

    def _current_cache_key(self) -> str:
        enabled_branch_ids = self._enabled_branch_ids()
        if self.input_mode_var.get() == "catalog":
            return f"catalog:{self.example_var.get()}:{enabled_branch_ids}"
        return f"custom:{self.custom_num_strands_var.get()}:{parse_generator_text(self.custom_generators_var.get())}:{enabled_branch_ids}"

    def _get_current_entry(self) -> MultiBranchBenchmarkEntry:
        enabled_branch_ids = self._enabled_branch_ids()
        if self.input_mode_var.get() == "catalog":
            active_braid = build_catalog_active_braid_state(self.example_var.get())
            cache_key = f"catalog:{active_braid.source_label}:{enabled_branch_ids}"
            if cache_key not in self.entry_cache:
                self.entry_cache[cache_key] = evaluate_gui_active_braid(active_braid, branch_ids=enabled_branch_ids, q=self.q)
            return self.entry_cache[cache_key]

        active_braid = build_custom_active_braid_state(
            self.custom_num_strands_var.get(),
            self.custom_generators_var.get(),
        )
        braid_word = active_braid.braid_word
        cache_key = f"custom:{braid_word.num_strands}:{braid_word.generators}:{enabled_branch_ids}"
        if cache_key not in self.entry_cache:
            # GUI data flow:
            # 1. user chooses catalog mode or custom mode
            # 2. GUI converts the active input into a BraidWord or built-in example
            # 3. GUI asks the multibranch evaluator for one MultiBranchBenchmarkEntry
            # 4. GUI filters branch_results by the current toggle state
            # 5. GUI renders cards plus formatter/raw report text
            self.entry_cache[cache_key] = evaluate_gui_active_braid(active_braid, branch_ids=enabled_branch_ids, q=self.q)
        return self.entry_cache[cache_key]

    def _refresh_view(self, *, show_errors: bool) -> None:
        try:
            entry = self._get_current_entry()
        except Exception as exc:  # pragma: no cover - defensive GUI path
            if show_errors:
                messagebox.showerror("Evaluation failed", str(exc))
            self.status_var.set(f"Evaluation failed: {exc}")
            return
        self._render_entry(entry)

    def _refresh_visible_results(self) -> None:
        if self.current_full_entry is not None:
            self._render_entry(self.current_full_entry)
            return
        self.status_var.set("No evaluated result is available yet. Click Evaluate to compute invariants.")

    def _render_entry(self, entry: MultiBranchBenchmarkEntry) -> None:
        visible_branch_ids = self._enabled_branch_ids()
        filtered_entry = filter_entry_by_branch_ids(entry, visible_branch_ids)
        self.current_full_entry = entry
        self.current_visible_entry = filtered_entry
        self.current_active_braid = build_active_braid_state_from_entry(entry)
        self._render_polynomial_overview(filtered_entry.branch_results)
        self._render_active_braid_preview(self.current_active_braid)
        self._update_summary_area(entry)
        self._render_result_cards(filtered_entry.branch_results)
        self._update_report_area(filtered_entry)
        if filtered_entry.branch_results:
            rendered = ", ".join(result.branch_id for result in filtered_entry.branch_results)
            self.status_var.set(f"Loaded {entry.example_label}. Visible branches: {rendered}")
        else:
            self.status_var.set(f"Loaded {entry.example_label}. No branches selected for display.")

    def _update_summary_area(self, entry: MultiBranchBenchmarkEntry) -> None:
        summary = build_entry_summary(entry)
        self.summary_text.delete("1.0", tk.END)
        self.summary_text.insert(tk.END, summary)
        self.summary_text.see("1.0")

    def _render_result_cards(self, branch_results: tuple[InvariantBranchResult, ...]) -> None:
        for child in self.cards_container.winfo_children():
            child.destroy()

        if not branch_results:
            ttk.Label(
                self.cards_container,
                text="No branch is currently selected. Re-enable one or more branch toggles to view results.",
                wraplength=980,
                justify=tk.LEFT,
            ).pack(anchor=tk.W, fill=tk.X, pady=8)
            return

        title_map = {spec.branch_id: spec.title for spec in get_gui_branch_specs()}
        for branch_result in branch_results:
            card = ttk.LabelFrame(
                self.cards_container,
                text=f"{title_map.get(branch_result.branch_id, branch_result.branch_id)} | {branch_result.representation_name}",
                padding=10,
                style="Surface.TLabelframe",
            )
            card.pack(fill=tk.X, expand=True, pady=(0, 10))
            self._populate_branch_card(card, branch_result)

    def _populate_branch_card(self, card: ttk.LabelFrame, branch_result: InvariantBranchResult) -> None:
        branch_spec = self._get_branch_spec(branch_result.branch_id)
        description_panel = tk.Frame(card, bg=SURFACE_SUBTLE, highlightbackground=BORDER_COLOR, highlightthickness=1)
        description_panel.pack(fill=tk.X, pady=(0, 10))
        tk.Label(
            description_panel,
            text=branch_spec.subtitle,
            bg=SURFACE_SUBTLE,
            fg=MUTED_TEXT_COLOR,
            anchor="w",
            justify=tk.LEFT,
            wraplength=1080,
            font=("Segoe UI", 10),
            padx=12,
            pady=8,
        ).pack(fill=tk.X)

        highlight_panel = tk.Frame(card, bg=branch_spec.accent_color)
        highlight_panel.pack(fill=tk.X, pady=(0, 10))
        tk.Label(
            highlight_panel,
            text=f"Primary output to compare: {branch_result.primary_output_label}",
            bg=branch_spec.accent_color,
            fg="#ffffff",
            anchor="w",
            font=("Segoe UI Semibold", 10),
            padx=12,
            pady=6,
        ).pack(fill=tk.X)

        primary_output_panel = tk.Frame(card, bg="#fbfdff", highlightbackground=BORDER_COLOR, highlightthickness=1)
        primary_output_panel.pack(fill=tk.X, pady=(0, 10))
        tk.Label(
            primary_output_panel,
            text=self._stringify(branch_result.primary_output),
            bg="#fbfdff",
            fg=TEXT_COLOR,
            anchor="w",
            justify=tk.LEFT,
            wraplength=1080,
            font=("Cascadia Mono", 11),
            padx=12,
            pady=10,
        ).pack(fill=tk.X)

        body = ttk.Frame(card)
        body.pack(fill=tk.X, expand=True)

        common_fields = [
            ("Branch id", branch_result.branch_id),
            ("Representation", branch_result.representation_name),
            ("Status", branch_result.status),
            ("Raw trace", self._stringify(branch_result.raw_trace)),
            ("Primary output label", branch_result.primary_output_label),
            ("Primary output", self._stringify(branch_result.primary_output)),
            ("Normalization label", branch_result.normalization_label),
            ("Variable convention", branch_result.variable_convention),
        ]

        for row_index, (label, value) in enumerate(common_fields):
            self._add_field_row(body, row_index, label, value)

        row_index = len(common_fields)
        if branch_result.branch_id == "sl2_fundamental":
            for label, key in (
                ("Unreduced P2", "unreduced_p2_output"),
                ("Unknot normalization", "unknot_normalization"),
                ("Reduced P2", "reduced_p2_output"),
            ):
                self._add_field_row(body, row_index, label, branch_result.metadata.get(key, "not available"))
                row_index += 1
        elif branch_result.branch_id == "sl2_spin1":
            self._add_field_row(
                body,
                row_index,
                "Quantum trace before normalization",
                branch_result.metadata.get("quantum_trace_before_normalization", "not available"),
            )
            row_index += 1
            self._add_field_row(
                body,
                row_index,
                "Unreduced candidate output",
                branch_result.metadata.get("unreduced_candidate_output", "not available"),
            )
            row_index += 1
            self._add_field_row(
                body,
                row_index,
                "Unknot normalization",
                branch_result.metadata.get("unknot_normalization", "not available"),
            )
            row_index += 1
            self._add_field_row(
                body,
                row_index,
                "Reduced candidate output",
                branch_result.metadata.get("reduced_candidate_output", "not available"),
            )
            row_index += 1
            self._add_field_row(body, row_index, "Candidate note", branch_result.metadata.get("branch_note", ""))
            row_index += 1
            self._add_field_row(body, row_index, "Projector checks", branch_result.metadata.get("projector_checks", ""))
            row_index += 1

        if branch_result.notes:
            self._add_field_row(body, row_index, "Notes", branch_result.notes)

        toolbar = ttk.Frame(card)
        toolbar.pack(fill=tk.X, pady=(8, 0))
        ttk.Button(
            toolbar,
            text="Copy branch report",
            command=lambda current=branch_result: self._copy_to_clipboard(format_branch_result(current), "Branch report copied."),
            style="Secondary.TButton",
        ).pack(side=tk.LEFT)

    def _add_field_row(self, parent: ttk.Frame, row_index: int, label: str, value: object) -> None:
        ttk.Label(parent, text=f"{label}:", font=("Segoe UI", 10, "bold")).grid(
            row=row_index,
            column=0,
            sticky="nw",
            padx=(0, 10),
            pady=(0, 6),
        )
        ttk.Label(
            parent,
            text=str(value),
            wraplength=1000,
            justify=tk.LEFT,
        ).grid(row=row_index, column=1, sticky="nw", pady=(0, 6))
        parent.columnconfigure(1, weight=1)

    def _refresh_report_view(self) -> None:
        if self.current_visible_entry is not None:
            self._update_report_area(self.current_visible_entry)

    def _update_report_area(self, entry: MultiBranchBenchmarkEntry) -> None:
        report = render_entry_report(entry, view_mode=self.view_mode_var.get())
        self.report_text.delete("1.0", tk.END)
        self.report_text.insert(tk.END, report)
        self.report_text.see("1.0")

    def _copy_current_report(self) -> None:
        if self.current_visible_entry is None:
            return
        self._copy_to_clipboard(
            render_entry_report(self.current_visible_entry, view_mode=self.view_mode_var.get()),
            "Current report copied.",
        )

    def _copy_to_clipboard(self, text: str, status_message: str) -> None:
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.status_var.set(status_message)

    def _try_build_custom_active_braid(self) -> GuiActiveBraidState | None:
        try:
            return build_custom_active_braid_state(
                self.custom_num_strands_var.get(),
                self.custom_generators_var.get(),
            )
        except Exception:
            return None

    def _render_pending_state(self, message: str, *, preview_braid: GuiActiveBraidState | None = None) -> None:
        self.current_full_entry = None
        self.current_visible_entry = None
        self.current_active_braid = preview_braid
        self._render_polynomial_overview(())
        if preview_braid is None:
            self._render_preview_message(message)
            summary_text = "No evaluated braid yet.\n\n" + message
            report_text = "No report available yet.\n\n" + message
        else:
            self._render_active_braid_preview(preview_braid)
            summary_text = build_active_braid_summary(
                preview_braid,
                footer_lines=(
                    "Status: pending evaluation.",
                    message,
                ),
            )
            report_text = "No report available yet.\n\n" + summary_text
        self.summary_text.delete("1.0", tk.END)
        self.summary_text.insert(tk.END, summary_text)
        self.summary_text.see("1.0")
        self.report_text.delete("1.0", tk.END)
        self.report_text.insert(tk.END, report_text)
        self.report_text.see("1.0")
        for child in self.cards_container.winfo_children():
            child.destroy()
        ttk.Label(
            self.cards_container,
            text=message,
            wraplength=980,
            justify=tk.LEFT,
        ).pack(anchor=tk.W, fill=tk.X, pady=8)
        self.status_var.set(message)

    def _render_polynomial_overview(self, branch_results: tuple[InvariantBranchResult, ...]) -> None:
        for child in self.overview_container.winfo_children():
            child.destroy()

        if not branch_results:
            ttk.Label(
                self.overview_container,
                text=(
                    "No polynomial output yet. Run Evaluate example or Apply custom braid, and the key outputs for "
                    "Jones/sl2, sl3, and the sl2 3D candidate branch will be summarized here."
                ),
                wraplength=1180,
                justify=tk.LEFT,
                style="Muted.TLabel",
            ).pack(anchor=tk.W)
            return

        for index, branch_result in enumerate(branch_results):
            branch_spec = self._get_branch_spec(branch_result.branch_id)
            card = tk.Frame(
                self.overview_container,
                bg=SURFACE_BACKGROUND,
                highlightbackground=BORDER_COLOR,
                highlightthickness=1,
                padx=14,
                pady=12,
            )
            card.grid(row=0, column=index, sticky="nsew", padx=(0, 10) if index < len(branch_results) - 1 else 0)
            self.overview_container.columnconfigure(index, weight=1)
            tk.Frame(card, bg=branch_spec.accent_color, height=4).pack(fill=tk.X, pady=(0, 10))
            tk.Label(
                card,
                text=branch_spec.title,
                bg=SURFACE_BACKGROUND,
                fg=TEXT_COLOR,
                anchor="w",
                font=("Segoe UI Semibold", 11),
            ).pack(fill=tk.X)
            tk.Label(
                card,
                text=branch_spec.user_hint,
                bg=SURFACE_BACKGROUND,
                fg=MUTED_TEXT_COLOR,
                anchor="w",
                justify=tk.LEFT,
                wraplength=330,
                font=("Segoe UI", 9),
            ).pack(fill=tk.X, pady=(4, 8))
            tk.Label(
                card,
                text=branch_result.primary_output_label,
                bg="#eef4ff" if branch_result.branch_id == "sl2_fundamental" else "#ecfdf5" if branch_result.branch_id == "sl3_fundamental" else "#f5f3ff",
                fg=branch_spec.accent_color,
                anchor="w",
                font=("Segoe UI", 9, "bold"),
                padx=8,
                pady=4,
            ).pack(fill=tk.X)
            tk.Label(
                card,
                text=self._stringify(branch_result.primary_output),
                bg=SURFACE_BACKGROUND,
                fg=TEXT_COLOR,
                anchor="w",
                justify=tk.LEFT,
                wraplength=330,
                font=("Cascadia Mono", 10),
            ).pack(fill=tk.X, pady=(10, 4))
            tk.Label(
                card,
                text=f"Status: {branch_result.status}",
                bg=SURFACE_BACKGROUND,
                fg=MUTED_TEXT_COLOR,
                anchor="w",
                font=("Segoe UI", 9),
            ).pack(fill=tk.X)

    @staticmethod
    def _get_branch_spec(branch_id: str) -> GuiBranchSpec:
        for spec in get_gui_branch_specs():
            if spec.branch_id == branch_id:
                return spec
        return GuiBranchSpec(
            branch_id=branch_id,
            title=branch_id,
            subtitle="No branch description available.",
            accent_color=ACCENT_COLOR,
            user_hint="Read the primary output shown for this branch.",
        )

    def _rebuild_generator_button_panel(self) -> None:
        for child in self.generator_button_frame.winfo_children():
            child.destroy()

        try:
            num_strands = int(self.custom_num_strands_var.get())
        except (tk.TclError, ValueError):
            num_strands = DEFAULT_CUSTOM_STRANDS

        ttk.Label(
            self.generator_button_frame,
            text=(
                "Choose the strand count, then click generator buttons to build the braid word. "
                "Higher strand counts automatically expose more generators."
            ),
        ).pack(anchor=tk.W)
        button_grid = ttk.Frame(self.generator_button_frame)
        button_grid.pack(fill=tk.X, pady=(6, 0))
        if num_strands <= 1:
            ttk.Label(button_grid, text="A 1-strand braid only supports the identity braid.").pack(anchor=tk.W)
            return

        for index in range(1, num_strands):
            group_frame = ttk.Frame(button_grid)
            row_index = (index - 1) // GENERATOR_BUTTON_GROUPS_PER_ROW
            column_index = (index - 1) % GENERATOR_BUTTON_GROUPS_PER_ROW
            group_frame.grid(row=row_index, column=column_index, padx=(0, 12), pady=(0, 8), sticky="w")
            ttk.Label(group_frame, text=f"σ{index}").pack(anchor=tk.W)
            ttk.Button(
                group_frame,
                text=f"+σ{index}",
                command=lambda current=index: self._append_generator(current),
            ).pack(side=tk.LEFT, padx=(0, 6))
            ttk.Button(
                group_frame,
                text=f"-σ{index}",
                command=lambda current=index: self._append_generator(-current),
            ).pack(side=tk.LEFT)

    def _render_preview_message(self, message: str) -> None:
        width = max(self.preview_canvas.winfo_width(), 520)
        height = max(self.preview_canvas.winfo_height(), 220)
        self.preview_canvas.delete("all")
        self.preview_canvas.configure(scrollregion=(0, 0, width, height))
        self.preview_canvas.xview_moveto(0)
        self.preview_canvas.yview_moveto(0)
        self.preview_canvas.create_text(
            width / 2,
            height / 2,
            text=(
                "No active braid preview yet.\n\n"
                f"{message}\n\n"
                "The preview switches only after Evaluate example or Apply custom braid so it stays synchronized with the computed outputs."
            ),
            fill=MUTED_TEXT_COLOR,
            justify=tk.CENTER,
            font=("Segoe UI", 10, "bold"),
            width=width - 80,
        )

    def _render_active_braid_preview(self, active_braid: GuiActiveBraidState) -> None:
        width = max(self.preview_canvas.winfo_width(), 520)
        height = max(self.preview_canvas.winfo_height(), 220)
        self.preview_canvas.delete("all")
        self.preview_canvas.xview_moveto(0)
        self.preview_canvas.yview_moveto(0)
        render_braid_preview(
            self.preview_canvas,
            active_braid.braid_word,
            viewport_width=width,
            viewport_height=height,
        )

    @staticmethod
    def _stringify(value: object | None) -> str:
        if value is None:
            return "not available"
        return str(value)


def launch_demo_gui() -> None:
    """Start the Tkinter GUI for the current multi-branch invariant skeleton."""

    root = tk.Tk()
    DemoLauncherApp(root)
    root.mainloop()


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Launch or inspect the multibranch invariant GUI entrypoint.")
    parser.add_argument("--list", action="store_true", help="List the built-in catalog examples shown by the GUI.")
    parser.add_argument("--run", metavar="EXAMPLE_LABEL", help="Print one built-in multibranch report in CLI mode.")
    parser.add_argument("--custom-strands", type=int, help="Evaluate one custom braid word in CLI mode.")
    parser.add_argument("--custom-generators", default="", help="Space- or comma-separated Artin generators for --custom-strands.")
    parser.add_argument(
        "--view",
        choices=get_gui_view_modes(),
        default="formatter",
        help="Choose formatter or raw report output for CLI inspection.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the GUI by default, or use small CLI helpers for smoke checks."""

    args = _build_arg_parser().parse_args(argv)

    if args.list:
        for label in get_gui_example_labels():
            print(label)
        return 0

    if args.run and args.custom_strands is not None:
        raise SystemExit("Use either --run for a built-in example or --custom-strands/--custom-generators for a custom braid.")

    if args.run:
        entry = evaluate_gui_example(args.run, q=sp.Symbol("q", nonzero=True))
        print(render_entry_report(entry, view_mode=args.view))
        return 0

    if args.custom_strands is not None:
        entry = evaluate_gui_custom_braid(args.custom_strands, args.custom_generators, q=sp.Symbol("q", nonzero=True))
        print(render_entry_report(entry, view_mode=args.view))
        return 0

    launch_demo_gui()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
