"""Ordinary braid workbench GUI with separated manual and JSON input modes."""

from __future__ import annotations

import json
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any

import sympy as sp

from src.catalog.braid_examples import get_braid_example, get_standard_braid_examples
from src.gui import demo_launcher as current_gui
from src.gui.braid_preview_renderer import (
    PRESENTATION_PREVIEW_STYLE,
    STANDARD_PREVIEW_STYLE,
    render_braid_preview,
    save_braid_preview_svg,
)
from src.services import ApplicationBraidResult, evaluate_braid_result, parse_generator_text
from src.workbench.comparison import WORKBENCH_CLASSIFICATION_LABELS, evaluate_workbench_pair
from src.workbench.experiment_log import ExperimentLog, ExperimentLogRecord
from src.workbench.runner import (
    RESULT_TABLE_PAIRWISE,
    RESULT_TABLE_SINGLE,
    RESULT_TABLE_SUMMARY,
    WorkbenchBatchRunResult,
    evaluate_workbench_run,
    get_classification_description,
)
from src.workbench.specs import (
    AI_JSON_TEMPLATE,
    WORKBENCH_COMPARISON_MODES,
    WORKBENCH_DEFAULT_MODELS,
    WORKBENCH_MODEL_SPECS,
    WorkbenchBraidSpec,
    WorkbenchInputSpec,
    WorkbenchInputValidationError,
    build_manual_input_spec,
    get_workbench_model_descriptions,
    normalize_braid_spec_data,
    normalize_input_spec,
    parse_json_input_spec,
    parse_workbench_q_parameter_value,
)


WORKBENCH_DEFAULT_Q_TEXT = "2"
WORKBENCH_DEFAULT_EXAMPLE_A = "trefoil"
WORKBENCH_DEFAULT_EXAMPLE_B = "figure_eight"
WORKBENCH_DISPLAY_MODES = (STANDARD_PREVIEW_STYLE, PRESENTATION_PREVIEW_STYLE)
RESULT_TABLE_LABELS = {
    RESULT_TABLE_SINGLE: "Single braid result table",
    RESULT_TABLE_PAIRWISE: "Pairwise comparison table",
    RESULT_TABLE_SUMMARY: "Summary table",
}
RESULT_TABLE_COLUMNS = {
    RESULT_TABLE_SINGLE: (
        "label",
        "num_strands",
        "generators",
        "sl2_fundamental_output",
        "sl2_3d_9x9_output",
        "sl3_fundamental_output",
        "notes",
    ),
    RESULT_TABLE_PAIRWISE: (
        "pair_label",
        "braid_a",
        "braid_b",
        "sl2_fundamental_same",
        "sl2_3d_9x9_same",
        "sl3_fundamental_same",
        "classification",
    ),
    RESULT_TABLE_SUMMARY: (
        "classification",
        "count",
    ),
}
COMPARISON_MODE_DESCRIPTIONS = {
    "single": "single: compute each braid independently and do not compare braids against each other.",
    "pairwise": "pairwise: compare every unordered pair A vs B, A vs C, B vs C, ...",
    "all": "all: output the single-braid table, the pairwise table, and the summary-count table together.",
}
LOG_FILTER_ANY = "Any"
LOG_FILTER_SAME = "Same"
LOG_FILTER_DIFFERENT = "Different"
LOG_INPUT_SOURCE_VALUES = (LOG_FILTER_ANY, "manual", "json")
EXTRA_LOG_CLASSIFICATIONS = ("selected_models_all_same", "selected_models_all_different", "selected_models_mixed")
ALL_LOG_CLASSIFICATIONS = (LOG_FILTER_ANY,) + WORKBENCH_CLASSIFICATION_LABELS + EXTRA_LOG_CLASSIFICATIONS


@dataclass(slots=True)
class ManualBraidCard:
    card_id: int
    frame: ttk.LabelFrame
    label_var: tk.StringVar
    example_var: tk.StringVar
    num_strands_var: tk.IntVar
    generators_var: tk.StringVar
    notes_var: tk.StringVar
    info_var: tk.StringVar
    preview_canvas: tk.Canvas
    generator_button_frame: ttk.Frame


def get_workbench_example_labels() -> tuple[str, ...]:
    return tuple(example.label for example in get_standard_braid_examples())


def parse_workbench_q_parameter(parameter_text: str) -> sp.Expr:
    return parse_workbench_q_parameter_value(parameter_text)[0]


def evaluate_single_workbench_braid(
    braid_word: current_gui.BraidWord,
    *,
    q: sp.Expr | None = None,
) -> ApplicationBraidResult:
    return evaluate_braid_result(
        braid_word,
        branch_ids=tuple(spec.branch_id for spec in WORKBENCH_MODEL_SPECS.values()),
        q=q,
    )


class BraidWorkbenchApp:
    """Ordinary workbench with separate manual and JSON input frontends over one shared runner."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self._suspend_card_tracking = False
        self.status_var = tk.StringVar(value="Workbench ready.")
        self.display_mode_var = tk.StringVar(value=STANDARD_PREVIEW_STYLE)
        self.manual_q_text_var = tk.StringVar(value=WORKBENCH_DEFAULT_Q_TEXT)
        self.manual_comparison_mode_var = tk.StringVar(value="pairwise")
        self.manual_model_vars = {
            model_id: tk.BooleanVar(value=model_id in WORKBENCH_DEFAULT_MODELS)
            for model_id in WORKBENCH_MODEL_SPECS
        }
        self.json_status_var = tk.StringVar(value="No JSON batch loaded yet.")
        self.results_status_var = tk.StringVar(value="No run result yet.")
        self.log_filter_status_var = tk.StringVar(value="Showing 0 / 0 records")
        self.log_label_filter_var = tk.StringVar(value="")
        self.log_classification_filter_var = tk.StringVar(value=LOG_FILTER_ANY)
        self.log_input_source_filter_var = tk.StringVar(value=LOG_FILTER_ANY)
        self.log_jones_filter_var = tk.StringVar(value=LOG_FILTER_ANY)
        self.log_sl2_3d_filter_var = tk.StringVar(value=LOG_FILTER_ANY)
        self.log_sl3_filter_var = tk.StringVar(value=LOG_FILTER_ANY)
        self.current_run_result: WorkbenchBatchRunResult | None = None
        self.loaded_json_input_spec: WorkbenchInputSpec | None = None
        self.experiment_log = ExperimentLog()
        self.manual_cards: list[ManualBraidCard] = []
        self._next_manual_card_id = 1

        self.manual_cards_container: ttk.Frame
        self.manual_cards_canvas: tk.Canvas
        self.json_text: tk.Text
        self.json_detail_text: tk.Text
        self.results_notebook: ttk.Notebook
        self.results_detail_text: tk.Text
        self.result_treeviews: dict[str, ttk.Treeview] = {}
        self.log_tree: ttk.Treeview
        self.log_detail_text: tk.Text

        self._configure_styles()
        self._build_ui()
        self._add_manual_card(default_example_label=WORKBENCH_DEFAULT_EXAMPLE_A)
        self._add_manual_card(default_example_label=WORKBENCH_DEFAULT_EXAMPLE_B)
        self._populate_json_template()
        self._refresh_log_table()

    def _configure_styles(self) -> None:
        self.root.configure(background=current_gui.APP_BACKGROUND)
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Workbench.TFrame", background=current_gui.APP_BACKGROUND)
        style.configure("WorkbenchCard.TLabelframe", background=current_gui.SURFACE_BACKGROUND, bordercolor=current_gui.BORDER_COLOR)
        style.configure(
            "WorkbenchCard.TLabelframe.Label",
            background=current_gui.SURFACE_BACKGROUND,
            foreground=current_gui.TEXT_COLOR,
            font=("Segoe UI", 11, "bold"),
        )
        style.configure("WorkbenchHero.TLabel", background=current_gui.APP_BACKGROUND, foreground=current_gui.TEXT_COLOR, font=("Segoe UI Semibold", 22))
        style.configure("WorkbenchSub.TLabel", background=current_gui.APP_BACKGROUND, foreground=current_gui.MUTED_TEXT_COLOR, font=("Segoe UI", 10))
        style.configure("WorkbenchStatus.TLabel", background=current_gui.APP_BACKGROUND, foreground=current_gui.ACCENT_COLOR, font=("Segoe UI Semibold", 10))

    def _build_ui(self) -> None:
        self.root.title("Quantum Group Knot Braid Workbench")
        self.root.geometry("1600x1020")
        self.root.minsize(1320, 820)

        shell = ttk.Frame(self.root, style="Workbench.TFrame", padding=12)
        shell.pack(fill=tk.BOTH, expand=True)

        ttk.Label(shell, text="Quantum Group Knot Braid Workbench", style="WorkbenchHero.TLabel").pack(anchor=tk.W)
        ttk.Label(
            shell,
            text=(
                "Manual input and JSON input are now separate frontends over the same ordinary/mainline runner. "
                "Both modes support single evaluation, pairwise comparison, all-mode reporting, unified result tables, "
                "and shared experiment-log/export flows. For the sl2 3D line, the shared wording stays the same as the "
                "ordinary GUI: compare against Knot Atlas n=2, keep the branch labeled colored Jones candidate, and do "
                "not overclaim final global normalization."
            ),
            style="WorkbenchSub.TLabel",
            wraplength=1500,
            justify=tk.LEFT,
        ).pack(anchor=tk.W, pady=(4, 10))

        display_frame = ttk.LabelFrame(shell, text="Preview display", padding=8, style="WorkbenchCard.TLabelframe")
        display_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(display_frame, text="Preview mode:").pack(side=tk.LEFT)
        ttk.Radiobutton(display_frame, text="Standard", value=STANDARD_PREVIEW_STYLE, variable=self.display_mode_var, command=self._refresh_all_manual_previews).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Radiobutton(display_frame, text="Presentation", value=PRESENTATION_PREVIEW_STYLE, variable=self.display_mode_var, command=self._refresh_all_manual_previews).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Label(display_frame, text="Use presentation mode for cleaner screenshots and SVG export.", style="WorkbenchSub.TLabel").pack(side=tk.LEFT, padx=(12, 0))

        notebook = ttk.Notebook(shell)
        notebook.pack(fill=tk.BOTH, expand=True)

        manual_tab = ttk.Frame(notebook, style="Workbench.TFrame", padding=8)
        json_tab = ttk.Frame(notebook, style="Workbench.TFrame", padding=8)
        results_tab = ttk.Frame(notebook, style="Workbench.TFrame", padding=8)
        log_tab = ttk.Frame(notebook, style="Workbench.TFrame", padding=8)
        notebook.add(manual_tab, text="Manual input")
        notebook.add(json_tab, text="JSON input")
        notebook.add(results_tab, text="Results")
        notebook.add(log_tab, text="Experiment log")

        self._build_manual_tab(manual_tab)
        self._build_json_tab(json_tab)
        self._build_results_tab(results_tab)
        self._build_log_tab(log_tab)

        ttk.Label(shell, textvariable=self.status_var, style="WorkbenchStatus.TLabel").pack(anchor=tk.E, pady=(8, 0))

    def _build_manual_tab(self, parent: ttk.Frame) -> None:
        parameter_frame = ttk.LabelFrame(parent, text="Manual input mode", padding=8, style="WorkbenchCard.TLabelframe")
        parameter_frame.pack(fill=tk.X, pady=(0, 8))

        row_one = ttk.Frame(parameter_frame)
        row_one.pack(fill=tk.X)
        ttk.Label(row_one, text="q parameter:").pack(side=tk.LEFT)
        ttk.Entry(row_one, textvariable=self.manual_q_text_var, width=18).pack(side=tk.LEFT, padx=(8, 12))
        ttk.Label(row_one, text="Comparison mode:").pack(side=tk.LEFT)
        ttk.Combobox(
            row_one,
            textvariable=self.manual_comparison_mode_var,
            values=WORKBENCH_COMPARISON_MODES,
            state="readonly",
            width=14,
        ).pack(side=tk.LEFT, padx=(8, 12))
        ttk.Button(row_one, text="Add braid", command=self._add_manual_card).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(row_one, text="Run manual batch", command=self._run_manual_batch).pack(side=tk.LEFT)

        row_two = ttk.Frame(parameter_frame)
        row_two.pack(fill=tk.X, pady=(8, 0))
        ttk.Label(row_two, text="Models:").pack(side=tk.LEFT)
        for model_id, spec in WORKBENCH_MODEL_SPECS.items():
            ttk.Checkbutton(row_two, text=model_id, variable=self.manual_model_vars[model_id]).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Label(
            row_two,
            text="q = q means symbolic mode for formal confirmation; q = 2 or another number means faster numeric screening.",
            style="WorkbenchSub.TLabel",
        ).pack(side=tk.LEFT, padx=(12, 0))

        ttk.Label(
            parameter_frame,
            text="\n".join(COMPARISON_MODE_DESCRIPTIONS[mode] for mode in WORKBENCH_COMPARISON_MODES),
            style="WorkbenchSub.TLabel",
            justify=tk.LEFT,
            wraplength=1450,
        ).pack(anchor=tk.W, pady=(8, 0))
        ttk.Label(
            parameter_frame,
            text="\n".join(get_workbench_model_descriptions()),
            style="WorkbenchSub.TLabel",
            justify=tk.LEFT,
            wraplength=1450,
        ).pack(anchor=tk.W, pady=(6, 0))

        cards_frame = ttk.LabelFrame(parent, text="Manual braid batch", padding=6, style="WorkbenchCard.TLabelframe")
        cards_frame.pack(fill=tk.BOTH, expand=True)
        self.manual_cards_canvas = tk.Canvas(cards_frame, background=current_gui.APP_BACKGROUND, highlightthickness=0)
        scrollbar = ttk.Scrollbar(cards_frame, orient=tk.VERTICAL, command=self.manual_cards_canvas.yview)
        self.manual_cards_canvas.configure(yscrollcommand=scrollbar.set)
        self.manual_cards_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.manual_cards_container = ttk.Frame(self.manual_cards_canvas, style="Workbench.TFrame")
        self.manual_cards_container.bind(
            "<Configure>",
            lambda _event: self.manual_cards_canvas.configure(scrollregion=self.manual_cards_canvas.bbox("all")),
        )
        self.manual_cards_canvas.bind(
            "<Configure>",
            lambda event: self.manual_cards_canvas.itemconfigure(self._manual_cards_window, width=event.width),
        )
        self._manual_cards_window = self.manual_cards_canvas.create_window((0, 0), window=self.manual_cards_container, anchor="nw")

    def _build_json_tab(self, parent: ttk.Frame) -> None:
        top = ttk.Panedwindow(parent, orient=tk.HORIZONTAL)
        top.pack(fill=tk.BOTH, expand=True)
        editor_frame = ttk.LabelFrame(top, text="JSON input mode", padding=8, style="WorkbenchCard.TLabelframe")
        help_frame = ttk.LabelFrame(top, text="Schema and loaded batch", padding=8, style="WorkbenchCard.TLabelframe")
        top.add(editor_frame, weight=5)
        top.add(help_frame, weight=3)

        toolbar = ttk.Frame(editor_frame)
        toolbar.pack(fill=tk.X)
        ttk.Button(toolbar, text="Validate JSON", command=self._validate_json_input).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="Load braids", command=self._load_json_input).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(toolbar, text="Run JSON batch", command=self._run_json_batch).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(toolbar, text="Clear JSON", command=self._clear_json_input).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(toolbar, text="Copy AI JSON template", command=self._copy_ai_json_template).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Label(toolbar, textvariable=self.json_status_var, style="WorkbenchSub.TLabel").pack(side=tk.RIGHT)

        self.json_text = tk.Text(
            editor_frame,
            wrap=tk.NONE,
            font=("Cascadia Mono", 10),
            background=current_gui.SURFACE_BACKGROUND,
            foreground=current_gui.TEXT_COLOR,
            relief=tk.FLAT,
            highlightthickness=0,
            padx=8,
            pady=8,
        )
        self.json_text.pack(fill=tk.BOTH, expand=True, pady=(8, 0))

        ttk.Label(
            help_frame,
            text=(
                "JSON schema fields:\n"
                "- q_parameter: 'q', '2', 2, ...\n"
                "- models: sl2_fundamental, sl2_3d_9x9, sl3_fundamental\n"
                "- comparison_mode: single, pairwise, all\n"
                "- braids: array of {label, num_strands, generators, notes?}\n\n"
                "Generator encoding:\n"
                "1 means σ1, -1 means σ1^-1, 2 means σ2, -2 means σ2^-1.\n\n"
                "q = q gives symbolic polynomials and is slower. Numeric q such as 2 is faster and suited to screening.\n\n"
                + "\n".join(get_workbench_model_descriptions())
            ),
            style="WorkbenchSub.TLabel",
            justify=tk.LEFT,
            wraplength=500,
        ).pack(anchor=tk.W)

        self.json_detail_text = tk.Text(
            help_frame,
            height=18,
            wrap=tk.WORD,
            font=("Cascadia Mono", 10),
            background=current_gui.SURFACE_BACKGROUND,
            foreground=current_gui.TEXT_COLOR,
            relief=tk.FLAT,
            highlightthickness=0,
            padx=8,
            pady=8,
        )
        self.json_detail_text.pack(fill=tk.BOTH, expand=True, pady=(8, 0))

    def _build_results_tab(self, parent: ttk.Frame) -> None:
        summary_frame = ttk.LabelFrame(parent, text="Run summary", padding=8, style="WorkbenchCard.TLabelframe")
        summary_frame.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(summary_frame, textvariable=self.results_status_var, style="WorkbenchSub.TLabel", justify=tk.LEFT, wraplength=1450).pack(anchor=tk.W)

        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 8))
        ttk.Button(toolbar, text="Export current table CSV", command=self._export_current_result_table_csv).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="Export current table JSON", command=self._export_current_result_table_json).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(toolbar, text="Copy current table markdown", command=self._copy_current_result_table_markdown).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(toolbar, text="Export full result bundle JSON", command=self._export_full_result_bundle_json).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(toolbar, text="Add current pairwise rows to experiment log", command=self._append_current_results_to_log).pack(side=tk.LEFT, padx=(8, 0))

        panes = ttk.Panedwindow(parent, orient=tk.VERTICAL)
        panes.pack(fill=tk.BOTH, expand=True)
        notebook_frame = ttk.Frame(panes, style="Workbench.TFrame")
        detail_frame = ttk.LabelFrame(panes, text="Result detail", padding=6, style="WorkbenchCard.TLabelframe")
        panes.add(notebook_frame, weight=4)
        panes.add(detail_frame, weight=2)

        self.results_notebook = ttk.Notebook(notebook_frame)
        self.results_notebook.pack(fill=tk.BOTH, expand=True)
        self.results_notebook.bind("<<NotebookTabChanged>>", lambda _event: self._refresh_results_detail())

        for table_id in (RESULT_TABLE_SINGLE, RESULT_TABLE_PAIRWISE, RESULT_TABLE_SUMMARY):
            frame = ttk.Frame(self.results_notebook, style="Workbench.TFrame", padding=6)
            self.results_notebook.add(frame, text=RESULT_TABLE_LABELS[table_id])
            self.result_treeviews[table_id] = self._create_table_treeview(frame, RESULT_TABLE_COLUMNS[table_id])
            self.result_treeviews[table_id].bind("<<TreeviewSelect>>", lambda _event, current=table_id: self._render_result_detail(current))

        self.results_detail_text = tk.Text(
            detail_frame,
            height=14,
            wrap=tk.WORD,
            font=("Cascadia Mono", 10),
            background=current_gui.SURFACE_BACKGROUND,
            foreground=current_gui.TEXT_COLOR,
            relief=tk.FLAT,
            highlightthickness=0,
            padx=8,
            pady=8,
        )
        self.results_detail_text.pack(fill=tk.BOTH, expand=True)

    def _build_log_tab(self, parent: ttk.Frame) -> None:
        filter_frame = ttk.LabelFrame(parent, text="Log filters", padding=6, style="WorkbenchCard.TLabelframe")
        filter_frame.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(filter_frame, text="Label contains:").grid(row=0, column=0, sticky="w")
        ttk.Entry(filter_frame, textvariable=self.log_label_filter_var, width=24).grid(row=0, column=1, sticky="w", padx=(8, 12))
        ttk.Label(filter_frame, text="Classification:").grid(row=0, column=2, sticky="w")
        ttk.Combobox(filter_frame, textvariable=self.log_classification_filter_var, values=ALL_LOG_CLASSIFICATIONS, state="readonly", width=28).grid(row=0, column=3, sticky="w", padx=(8, 12))
        ttk.Label(filter_frame, text="Input source:").grid(row=0, column=4, sticky="w")
        ttk.Combobox(filter_frame, textvariable=self.log_input_source_filter_var, values=LOG_INPUT_SOURCE_VALUES, state="readonly", width=12).grid(row=0, column=5, sticky="w", padx=(8, 12))
        ttk.Label(filter_frame, text="Jones:").grid(row=1, column=0, sticky="w", pady=(8, 0))
        ttk.Combobox(filter_frame, textvariable=self.log_jones_filter_var, values=(LOG_FILTER_ANY, LOG_FILTER_SAME, LOG_FILTER_DIFFERENT), state="readonly", width=12).grid(row=1, column=1, sticky="w", padx=(8, 12), pady=(8, 0))
        ttk.Label(filter_frame, text="sl2 3D:").grid(row=1, column=2, sticky="w", pady=(8, 0))
        ttk.Combobox(filter_frame, textvariable=self.log_sl2_3d_filter_var, values=(LOG_FILTER_ANY, LOG_FILTER_SAME, LOG_FILTER_DIFFERENT), state="readonly", width=12).grid(row=1, column=3, sticky="w", padx=(8, 12), pady=(8, 0))
        ttk.Label(filter_frame, text="sl3:").grid(row=1, column=4, sticky="w", pady=(8, 0))
        ttk.Combobox(filter_frame, textvariable=self.log_sl3_filter_var, values=(LOG_FILTER_ANY, LOG_FILTER_SAME, LOG_FILTER_DIFFERENT), state="readonly", width=12).grid(row=1, column=5, sticky="w", padx=(8, 12), pady=(8, 0))
        ttk.Button(filter_frame, text="Apply filters", command=self._refresh_log_table).grid(row=0, column=6, sticky="w")
        ttk.Button(filter_frame, text="Clear filters", command=self._clear_log_filters).grid(row=0, column=7, sticky="w", padx=(8, 0))
        ttk.Label(filter_frame, textvariable=self.log_filter_status_var, style="WorkbenchSub.TLabel").grid(row=0, column=8, rowspan=2, sticky="e", padx=(12, 0))

        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 8))
        ttk.Button(toolbar, text="Export CSV", command=self._export_log_csv).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="Export JSON", command=self._export_log_json).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(toolbar, text="Copy markdown table", command=self._copy_log_markdown_table).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(toolbar, text="Clear log", command=self._clear_log).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Label(toolbar, text="Log records keep input_source = manual/json so batch origin stays traceable.", style="WorkbenchSub.TLabel").pack(side=tk.RIGHT)

        columns = (
            "record_id",
            "timestamp",
            "label",
            "input_source",
            "classification",
            "sl2_jones_same",
            "sl2_3d_same",
            "sl3_same",
            "braid_a_word",
            "braid_b_word",
        )
        self.log_tree = ttk.Treeview(parent, columns=columns, show="headings", height=14)
        for column in columns:
            self.log_tree.heading(column, text=column)
            width = 140
            if column in {"braid_a_word", "braid_b_word"}:
                width = 260
            elif column == "classification":
                width = 220
            self.log_tree.column(column, width=width, anchor="w")
        self.log_tree.pack(fill=tk.BOTH, expand=True)
        self.log_tree.bind("<<TreeviewSelect>>", self._on_log_selection_changed)

        detail_frame = ttk.LabelFrame(parent, text="Selected log record", padding=6, style="WorkbenchCard.TLabelframe")
        detail_frame.pack(fill=tk.BOTH, expand=True, pady=(8, 0))
        self.log_detail_text = tk.Text(
            detail_frame,
            height=14,
            wrap=tk.WORD,
            font=("Cascadia Mono", 10),
            background=current_gui.SURFACE_BACKGROUND,
            foreground=current_gui.TEXT_COLOR,
            relief=tk.FLAT,
            highlightthickness=0,
            padx=8,
            pady=8,
        )
        self.log_detail_text.pack(fill=tk.BOTH, expand=True)

    def _create_table_treeview(self, parent: ttk.Frame, columns: tuple[str, ...]) -> ttk.Treeview:
        tree = ttk.Treeview(parent, columns=columns, show="headings")
        for column in columns:
            tree.heading(column, text=column)
            width = 140
            if column in {"generators", "sl2_fundamental_output", "sl2_3d_9x9_output", "sl3_fundamental_output"}:
                width = 240
            elif column == "notes":
                width = 220
            elif column == "classification":
                width = 220
            tree.column(column, width=width, anchor="w")
        scrollbar_y = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        scrollbar_x = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(fill=tk.X)
        return tree

    def _populate_json_template(self) -> None:
        self.json_text.delete("1.0", tk.END)
        self.json_text.insert(tk.END, AI_JSON_TEMPLATE)
        self.json_detail_text.delete("1.0", tk.END)
        self.json_detail_text.insert(tk.END, "Paste JSON here, validate it, then load/run it.\n")

    def _add_manual_card(self, *, default_example_label: str | None = None, source_card: ManualBraidCard | None = None) -> ManualBraidCard:
        example_label = default_example_label or (source_card.example_var.get() if source_card is not None else WORKBENCH_DEFAULT_EXAMPLE_A)
        frame = ttk.LabelFrame(
            self.manual_cards_container,
            text=f"Manual braid #{self._next_manual_card_id}",
            padding=8,
            style="WorkbenchCard.TLabelframe",
        )
        frame.pack(fill=tk.X, expand=True, pady=(0, 10))

        label_var = tk.StringVar(value=(source_card.label_var.get() if source_card is not None else example_label))
        example_var = tk.StringVar(value=example_label)
        notes_var = tk.StringVar(value=(source_card.notes_var.get() if source_card is not None else ""))
        example = get_braid_example(example_label)
        num_strands_var = tk.IntVar(value=source_card.num_strands_var.get() if source_card is not None else example.num_strands)
        generators_var = tk.StringVar(
            value=(
                source_card.generators_var.get()
                if source_card is not None
                else " ".join(str(generator) for generator in example.generators)
            )
        )
        info_var = tk.StringVar(value="")

        header = ttk.Frame(frame)
        header.pack(fill=tk.X)
        ttk.Label(header, text="Label:").pack(side=tk.LEFT)
        ttk.Entry(header, textvariable=label_var, width=24).pack(side=tk.LEFT, padx=(6, 12))
        ttk.Label(header, text="Built-in example:").pack(side=tk.LEFT)
        example_box = ttk.Combobox(header, textvariable=example_var, values=get_workbench_example_labels(), state="readonly", width=18)
        example_box.pack(side=tk.LEFT, padx=(6, 8))
        preview_canvas = tk.Canvas(frame, height=250, background="#fafafa", highlightthickness=1)
        generator_button_frame = ttk.Frame(frame)

        card = ManualBraidCard(
            card_id=self._next_manual_card_id,
            frame=frame,
            label_var=label_var,
            example_var=example_var,
            num_strands_var=num_strands_var,
            generators_var=generators_var,
            notes_var=notes_var,
            info_var=info_var,
            preview_canvas=preview_canvas,
            generator_button_frame=generator_button_frame,
        )
        self._next_manual_card_id += 1

        ttk.Button(header, text="Load example", command=lambda current=card: self._load_example_into_manual_card(current)).pack(side=tk.LEFT)
        ttk.Button(header, text="Duplicate", command=lambda current=card: self._duplicate_manual_card(current)).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(header, text="Delete", command=lambda current=card: self._delete_manual_card(current)).pack(side=tk.LEFT, padx=(8, 0))

        editor = ttk.Frame(frame)
        editor.pack(fill=tk.X, pady=(8, 0))
        ttk.Label(editor, text="Strands:").grid(row=0, column=0, sticky="w")
        strands_box = ttk.Spinbox(
            editor,
            from_=2,
            to=current_gui.MAX_CUSTOM_STRANDS,
            textvariable=num_strands_var,
            width=6,
            command=lambda current=card: self._on_manual_card_strands_changed(current),
        )
        strands_box.grid(row=0, column=1, sticky="w", padx=(6, 12))
        ttk.Label(editor, text="Generators:").grid(row=0, column=2, sticky="w")
        generators_entry = ttk.Entry(editor, textvariable=generators_var, width=44)
        generators_entry.grid(row=0, column=3, sticky="ew", padx=(6, 8))
        ttk.Button(editor, text="Refresh preview", command=lambda current=card: self._refresh_manual_card_preview(current)).grid(row=0, column=4, sticky="w")
        ttk.Label(editor, text="Notes:").grid(row=1, column=0, sticky="w", pady=(8, 0))
        ttk.Entry(editor, textvariable=notes_var, width=70).grid(row=1, column=1, columnspan=4, sticky="ew", padx=(6, 0), pady=(8, 0))
        editor.columnconfigure(3, weight=1)

        toolbar = ttk.Frame(frame)
        toolbar.pack(fill=tk.X, pady=(8, 0))
        ttk.Button(toolbar, text="Undo", command=lambda current=card: self._undo_manual_card_generator(current)).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="Clear", command=lambda current=card: self._clear_manual_card_generators(current)).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(toolbar, text="Save SVG", command=lambda current=card: self._export_manual_card_preview_svg(current)).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Label(toolbar, textvariable=info_var, style="WorkbenchSub.TLabel").pack(side=tk.LEFT, padx=(12, 0))

        generator_button_frame.pack(fill=tk.X, pady=(8, 0))

        preview_frame = ttk.LabelFrame(frame, text="Braid preview", padding=6, style="WorkbenchCard.TLabelframe")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(8, 0))
        preview_container = ttk.Frame(preview_frame)
        preview_container.pack(fill=tk.BOTH, expand=True)
        preview_y_scrollbar = ttk.Scrollbar(preview_container, orient=tk.VERTICAL, command=preview_canvas.yview)
        preview_x_scrollbar = ttk.Scrollbar(preview_frame, orient=tk.HORIZONTAL, command=preview_canvas.xview)
        preview_canvas.configure(xscrollcommand=preview_x_scrollbar.set, yscrollcommand=preview_y_scrollbar.set)
        preview_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        preview_y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        preview_x_scrollbar.pack(fill=tk.X, pady=(6, 0))

        generators_entry.bind("<KeyRelease>", lambda _event, current=card: self._on_manual_card_generators_edited(current))
        example_box.bind("<<ComboboxSelected>>", lambda _event, current=card: self._load_example_into_manual_card(current))
        num_strands_var.trace_add("write", lambda *_args, current=card: self._on_manual_card_strands_changed(current))
        label_var.trace_add("write", lambda *_args, current=card: self._refresh_manual_card_preview(current))
        notes_var.trace_add("write", lambda *_args, current=card: self._refresh_manual_card_preview(current))

        self.manual_cards.append(card)
        self._rebuild_manual_card_generator_buttons(card)
        if source_card is None:
            self._load_example_into_manual_card(card)
        else:
            self._refresh_manual_card_preview(card)
        return card

    def _duplicate_manual_card(self, card: ManualBraidCard) -> None:
        duplicated = self._add_manual_card(source_card=card)
        duplicated.label_var.set(f"{card.label_var.get()}_copy")
        self.status_var.set(f"Duplicated {card.label_var.get()}.")

    def _delete_manual_card(self, card: ManualBraidCard) -> None:
        if len(self.manual_cards) <= 1:
            messagebox.showinfo("Cannot delete", "The manual batch must keep at least one braid card.")
            return
        self.manual_cards = [item for item in self.manual_cards if item.card_id != card.card_id]
        card.frame.destroy()
        self.status_var.set(f"Deleted manual braid card {card.card_id}.")

    def _load_example_into_manual_card(self, card: ManualBraidCard) -> None:
        example = get_braid_example(card.example_var.get())
        self._suspend_card_tracking = True
        try:
            card.label_var.set(example.label)
            card.num_strands_var.set(example.num_strands)
            card.generators_var.set(" ".join(str(generator) for generator in example.generators))
            card.notes_var.set(example.notes)
        finally:
            self._suspend_card_tracking = False
        self._rebuild_manual_card_generator_buttons(card)
        self._refresh_manual_card_preview(card)
        self.status_var.set(f"Loaded built-in example {example.label} into manual card {card.card_id}.")

    def _on_manual_card_strands_changed(self, card: ManualBraidCard) -> None:
        if self._suspend_card_tracking:
            return
        self._rebuild_manual_card_generator_buttons(card)
        self._refresh_manual_card_preview(card)

    def _on_manual_card_generators_edited(self, card: ManualBraidCard) -> None:
        if self._suspend_card_tracking:
            return
        self._refresh_manual_card_preview(card)

    def _append_manual_card_generator(self, card: ManualBraidCard, generator: int) -> None:
        current = card.generators_var.get().strip()
        card.generators_var.set(str(generator) if not current else f"{current} {generator}")
        self._refresh_manual_card_preview(card)

    def _undo_manual_card_generator(self, card: ManualBraidCard) -> None:
        try:
            generators = list(parse_generator_text(card.generators_var.get()))
        except ValueError:
            generators = []
        if generators:
            generators.pop()
        card.generators_var.set(" ".join(str(generator) for generator in generators))
        self._refresh_manual_card_preview(card)

    def _clear_manual_card_generators(self, card: ManualBraidCard) -> None:
        card.generators_var.set("")
        self._refresh_manual_card_preview(card)

    def _rebuild_manual_card_generator_buttons(self, card: ManualBraidCard) -> None:
        for child in card.generator_button_frame.winfo_children():
            child.destroy()

        ttk.Label(
            card.generator_button_frame,
            text="Graphical braid builder: append +σ_i / -σ_i or edit the generator list by hand.",
            style="WorkbenchSub.TLabel",
        ).pack(anchor=tk.W)
        button_grid = ttk.Frame(card.generator_button_frame)
        button_grid.pack(fill=tk.X, pady=(6, 0))
        try:
            num_strands = int(card.num_strands_var.get())
        except (tk.TclError, ValueError):
            num_strands = 2
        for index in range(1, num_strands):
            group_frame = ttk.Frame(button_grid)
            row_index = (index - 1) // current_gui.GENERATOR_BUTTON_GROUPS_PER_ROW
            column_index = (index - 1) % current_gui.GENERATOR_BUTTON_GROUPS_PER_ROW
            group_frame.grid(row=row_index, column=column_index, padx=(0, 12), pady=(0, 8), sticky="w")
            ttk.Label(group_frame, text=f"σ{index}").pack(anchor=tk.W)
            ttk.Button(group_frame, text=f"+σ{index}", command=lambda current=index, current_card=card: self._append_manual_card_generator(current_card, current)).pack(side=tk.LEFT, padx=(0, 6))
            ttk.Button(group_frame, text=f"-σ{index}", command=lambda current=index, current_card=card: self._append_manual_card_generator(current_card, -current)).pack(side=tk.LEFT)

    def _manual_card_to_spec(self, card: ManualBraidCard) -> WorkbenchBraidSpec:
        try:
            generators = list(parse_generator_text(card.generators_var.get()))
        except ValueError as exc:
            raise WorkbenchInputValidationError(f"Braid '{card.label_var.get()}' has invalid generators: {exc}") from exc
        return normalize_braid_spec_data(
            {
                "label": card.label_var.get().strip(),
                "num_strands": int(card.num_strands_var.get()),
                "generators": generators,
                "notes": card.notes_var.get().strip(),
            }
        )

    def _refresh_manual_card_preview(self, card: ManualBraidCard) -> None:
        width = max(card.preview_canvas.winfo_width(), 560)
        height = max(card.preview_canvas.winfo_height(), 250)
        card.preview_canvas.delete("all")
        try:
            braid_spec = self._manual_card_to_spec(card)
            braid_word = braid_spec.to_braid_word()
        except Exception as exc:
            card.preview_canvas.configure(scrollregion=(0, 0, width, height))
            card.preview_canvas.create_text(
                width / 2,
                height / 2,
                text=f"Preview unavailable:\n{exc}",
                fill="#b00020",
                justify=tk.CENTER,
                font=("Segoe UI", 10, "bold"),
            )
            card.info_var.set("invalid braid")
            return

        render_braid_preview(
            card.preview_canvas,
            braid_word,
            viewport_width=width,
            viewport_height=height,
            style=self.display_mode_var.get(),
        )
        card.info_var.set(
            f"label={braid_spec.label} strands={braid_spec.num_strands} crossings={len(braid_spec.generators)} writhe={braid_word.writhe()}"
        )

    def _refresh_all_manual_previews(self) -> None:
        for card in self.manual_cards:
            self._refresh_manual_card_preview(card)

    def _export_manual_card_preview_svg(self, card: ManualBraidCard) -> None:
        try:
            braid_spec = self._manual_card_to_spec(card)
        except Exception as exc:
            messagebox.showerror("Preview export failed", str(exc))
            return
        target = filedialog.asksaveasfilename(
            title=f"Export {braid_spec.label} preview as SVG",
            defaultextension=".svg",
            initialfile=f"{braid_spec.label}_preview.svg",
            filetypes=[("SVG files", "*.svg"), ("All files", "*.*")],
        )
        if not target:
            return
        save_braid_preview_svg(
            target,
            braid_spec.to_braid_word(),
            viewport_width=max(card.preview_canvas.winfo_width(), 560),
            viewport_height=max(card.preview_canvas.winfo_height(), 250),
            style=self.display_mode_var.get(),
        )
        self.status_var.set(f"Exported manual preview SVG to {target}.")

    def _selected_manual_models(self) -> tuple[str, ...]:
        return tuple(model_id for model_id in WORKBENCH_MODEL_SPECS if self.manual_model_vars[model_id].get())

    def _collect_manual_input_spec(self) -> WorkbenchInputSpec:
        braid_specs = tuple(self._manual_card_to_spec(card) for card in self.manual_cards)
        return build_manual_input_spec(
            q_parameter=self.manual_q_text_var.get(),
            models=self._selected_manual_models(),
            comparison_mode=self.manual_comparison_mode_var.get(),
            braids=braid_specs,
        )

    def _run_manual_batch(self) -> None:
        try:
            run_spec = normalize_input_spec(self._collect_manual_input_spec())
            run_result = evaluate_workbench_run(run_spec)
        except Exception as exc:
            messagebox.showerror("Manual batch failed", str(exc))
            self.status_var.set(f"Manual batch failed: {exc}")
            return
        self._render_run_result(run_result)
        self.status_var.set(f"Manual batch completed with {len(run_result.single_rows)} braid(s).")

    def _validate_json_input(self) -> None:
        try:
            input_spec = parse_json_input_spec(self.json_text.get("1.0", tk.END))
            run_spec = normalize_input_spec(input_spec)
        except Exception as exc:
            messagebox.showerror("Invalid JSON input", str(exc))
            self.status_var.set(f"JSON validation failed: {exc}")
            return
        self.loaded_json_input_spec = input_spec
        self.json_status_var.set(
            f"Validated {len(run_spec.batch.braids)} braid(s), comparison_mode={run_spec.comparison_mode}, models={', '.join(run_spec.models)}."
        )
        self._render_json_loaded_detail(input_spec, run_spec)
        self.status_var.set("JSON input validated.")

    def _load_json_input(self) -> None:
        try:
            input_spec = parse_json_input_spec(self.json_text.get("1.0", tk.END))
            run_spec = normalize_input_spec(input_spec)
        except Exception as exc:
            messagebox.showerror("Load JSON failed", str(exc))
            self.status_var.set(f"Load JSON failed: {exc}")
            return
        self.loaded_json_input_spec = input_spec
        self.json_status_var.set(f"Loaded JSON batch with {len(run_spec.batch.braids)} braid(s).")
        self._render_json_loaded_detail(input_spec, run_spec)
        self.status_var.set("Loaded JSON batch into the shared workbench spec layer.")

    def _run_json_batch(self) -> None:
        try:
            input_spec = self.loaded_json_input_spec or parse_json_input_spec(self.json_text.get("1.0", tk.END))
            run_spec = normalize_input_spec(input_spec)
            run_result = evaluate_workbench_run(run_spec)
        except Exception as exc:
            messagebox.showerror("JSON batch failed", str(exc))
            self.status_var.set(f"JSON batch failed: {exc}")
            return
        self.loaded_json_input_spec = input_spec
        self._render_json_loaded_detail(input_spec, run_spec)
        self._render_run_result(run_result)
        self.status_var.set(f"JSON batch completed with {len(run_result.single_rows)} braid(s).")

    def _clear_json_input(self) -> None:
        self.loaded_json_input_spec = None
        self.json_text.delete("1.0", tk.END)
        self.json_status_var.set("JSON editor cleared.")
        self.json_detail_text.delete("1.0", tk.END)
        self.json_detail_text.insert(tk.END, "JSON editor cleared.\n")

    def _copy_ai_json_template(self) -> None:
        self.root.clipboard_clear()
        self.root.clipboard_append(AI_JSON_TEMPLATE)
        self.status_var.set("Copied AI JSON template to clipboard.")

    def _render_json_loaded_detail(self, input_spec: WorkbenchInputSpec, run_spec: Any) -> None:
        self.json_detail_text.delete("1.0", tk.END)
        self.json_detail_text.insert(
            tk.END,
            json.dumps(
                {
                    "input_source": input_spec.input_source,
                    "q_parameter": run_spec.q_parameter_text,
                    "models": list(run_spec.models),
                    "comparison_mode": run_spec.comparison_mode,
                    "braids": [
                        {
                            "label": braid.label,
                            "num_strands": braid.num_strands,
                            "generators": list(braid.generators),
                            "notes": braid.notes,
                        }
                        for braid in run_spec.batch.braids
                    ],
                },
                indent=2,
                ensure_ascii=False,
            ),
        )

    def _render_run_result(self, run_result: WorkbenchBatchRunResult) -> None:
        self.current_run_result = run_result
        self.results_status_var.set(
            (
                f"Input source: {run_result.run_spec.input_source} | q_parameter: {run_result.run_spec.q_parameter_text} | "
                f"models: {', '.join(run_result.run_spec.models)} | comparison_mode: {run_result.run_spec.comparison_mode} | "
                f"single rows: {len(run_result.single_rows)} | pairwise rows: {len(run_result.pairwise_rows)} | summary rows: {len(run_result.summary_rows)}"
            )
        )
        for table_id, tree in self.result_treeviews.items():
            for item in tree.get_children():
                tree.delete(item)
            rows = run_result.table_rows(table_id)
            for index, row in enumerate(rows):
                values = tuple(self._stringify_table_value(row[column]) for column in RESULT_TABLE_COLUMNS[table_id])
                tree.insert("", tk.END, iid=f"{table_id}-{index}", values=values)
        self._refresh_results_detail()

    def _current_result_table_id(self) -> str:
        current_tab = self.results_notebook.select()
        tab_text = self.results_notebook.tab(current_tab, "text")
        for table_id, label in RESULT_TABLE_LABELS.items():
            if label == tab_text:
                return table_id
        return RESULT_TABLE_SINGLE

    def _refresh_results_detail(self) -> None:
        if self.current_run_result is None:
            self.results_detail_text.delete("1.0", tk.END)
            self.results_detail_text.insert(tk.END, "No result loaded yet. Run manual or JSON input first.")
            return
        self._render_result_detail(self._current_result_table_id())

    def _render_result_detail(self, table_id: str) -> None:
        self.results_detail_text.delete("1.0", tk.END)
        if self.current_run_result is None:
            self.results_detail_text.insert(tk.END, "No result loaded yet.")
            return
        tree = self.result_treeviews[table_id]
        selection = tree.selection()
        if not selection:
            self.results_detail_text.insert(
                tk.END,
                json.dumps(
                    {
                        "table": RESULT_TABLE_LABELS[table_id],
                        "rows": self.current_run_result.table_rows(table_id),
                    },
                    indent=2,
                    ensure_ascii=False,
                ),
            )
            return
        row_index = int(selection[0].split("-")[-1])
        row = self.current_run_result.table_rows(table_id)[row_index]
        detail: dict[str, Any] = dict(row)
        if table_id == RESULT_TABLE_PAIRWISE:
            pair_meta = self.current_run_result.pair_metadata[row_index]
            detail["classification_description"] = pair_meta["classification_description"]
        self.results_detail_text.insert(tk.END, json.dumps(detail, indent=2, ensure_ascii=False))

    def _stringify_table_value(self, value: Any) -> str:
        if isinstance(value, list):
            return json.dumps(value, ensure_ascii=False)
        return str(value)

    def _export_current_result_table_csv(self) -> None:
        if self.current_run_result is None:
            messagebox.showinfo("No result", "Run a manual or JSON batch first.")
            return
        table_id = self._current_result_table_id()
        target = filedialog.asksaveasfilename(
            title=f"Export {RESULT_TABLE_LABELS[table_id]} to CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not target:
            return
        Path(target).write_text(self.current_run_result.to_csv_text(table_id), encoding="utf-8", newline="")
        self.status_var.set(f"Exported {RESULT_TABLE_LABELS[table_id]} CSV to {target}.")

    def _export_current_result_table_json(self) -> None:
        if self.current_run_result is None:
            messagebox.showinfo("No result", "Run a manual or JSON batch first.")
            return
        table_id = self._current_result_table_id()
        target = filedialog.asksaveasfilename(
            title=f"Export {RESULT_TABLE_LABELS[table_id]} to JSON",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if not target:
            return
        Path(target).write_text(self.current_run_result.to_json_text(table_id), encoding="utf-8")
        self.status_var.set(f"Exported {RESULT_TABLE_LABELS[table_id]} JSON to {target}.")

    def _copy_current_result_table_markdown(self) -> None:
        if self.current_run_result is None:
            messagebox.showinfo("No result", "Run a manual or JSON batch first.")
            return
        table_id = self._current_result_table_id()
        self.root.clipboard_clear()
        self.root.clipboard_append(self.current_run_result.to_markdown_table(table_id))
        self.status_var.set(f"Copied {RESULT_TABLE_LABELS[table_id]} markdown table.")

    def _export_full_result_bundle_json(self) -> None:
        if self.current_run_result is None:
            messagebox.showinfo("No result", "Run a manual or JSON batch first.")
            return
        target = filedialog.asksaveasfilename(
            title="Export full result bundle to JSON",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if not target:
            return
        Path(target).write_text(self.current_run_result.to_json_text(), encoding="utf-8")
        self.status_var.set(f"Exported full result bundle JSON to {target}.")

    def _append_current_results_to_log(self) -> None:
        if self.current_run_result is None:
            messagebox.showinfo("No result", "Run a manual or JSON batch first.")
            return
        if not self.current_run_result.pairwise_rows:
            messagebox.showinfo("No pairwise rows", "The current run has no pairwise rows to log.")
            return
        records = self.experiment_log.add_batch_run_result(self.current_run_result)
        self._refresh_log_table(select_record_id=records[-1].record_id if records else None)
        self.status_var.set(f"Added {len(records)} pairwise row(s) to the experiment log.")

    @staticmethod
    def _tri_state_filter_to_bool(value: str) -> bool | None:
        if value == LOG_FILTER_SAME:
            return True
        if value == LOG_FILTER_DIFFERENT:
            return False
        return None

    def _filtered_log_records(self) -> list[ExperimentLogRecord]:
        classification = "" if self.log_classification_filter_var.get() == LOG_FILTER_ANY else self.log_classification_filter_var.get()
        input_source = "" if self.log_input_source_filter_var.get() == LOG_FILTER_ANY else self.log_input_source_filter_var.get()
        return self.experiment_log.filter_records(
            label_query=self.log_label_filter_var.get(),
            classification=classification,
            input_source=input_source,
            sl2_jones_same=self._tri_state_filter_to_bool(self.log_jones_filter_var.get()),
            sl2_3d_same=self._tri_state_filter_to_bool(self.log_sl2_3d_filter_var.get()),
            sl3_same=self._tri_state_filter_to_bool(self.log_sl3_filter_var.get()),
        )

    def _clear_log_filters(self) -> None:
        self.log_label_filter_var.set("")
        self.log_classification_filter_var.set(LOG_FILTER_ANY)
        self.log_input_source_filter_var.set(LOG_FILTER_ANY)
        self.log_jones_filter_var.set(LOG_FILTER_ANY)
        self.log_sl2_3d_filter_var.set(LOG_FILTER_ANY)
        self.log_sl3_filter_var.set(LOG_FILTER_ANY)
        self._refresh_log_table()

    def _refresh_log_table(self, *, select_record_id: str | None = None) -> None:
        filtered_records = self._filtered_log_records()
        for row_id in self.log_tree.get_children():
            self.log_tree.delete(row_id)
        for record in filtered_records:
            self.log_tree.insert(
                "",
                tk.END,
                iid=record.record_id,
                values=(
                    record.record_id,
                    record.timestamp,
                    record.label,
                    record.input_source,
                    record.classification,
                    record.sl2_jones_same,
                    record.sl2_3d_same,
                    record.sl3_same,
                    record.braid_a_word,
                    record.braid_b_word,
                ),
            )
        self.log_filter_status_var.set(f"Showing {len(filtered_records)} / {len(self.experiment_log.records)} records")
        if select_record_id is not None and self.log_tree.exists(select_record_id):
            self.log_tree.selection_set(select_record_id)
            self.log_tree.focus(select_record_id)
            self._render_log_record_detail(select_record_id)
        elif not filtered_records:
            self.log_detail_text.delete("1.0", tk.END)
            self.log_detail_text.insert(tk.END, "No experiment records match the current filters.")

    def _on_log_selection_changed(self, _event: object) -> None:
        selection = self.log_tree.selection()
        if not selection:
            return
        self._render_log_record_detail(selection[0])

    def _render_log_record_detail(self, record_id: str) -> None:
        record = self.experiment_log.get_record(record_id)
        if record is None:
            return
        self.log_detail_text.delete("1.0", tk.END)
        self.log_detail_text.insert(tk.END, json.dumps(record.to_dict(), indent=2, ensure_ascii=False))

    def _export_log_csv(self) -> None:
        records = self._filtered_log_records()
        if not records:
            messagebox.showinfo("Empty experiment log", "No log records are available to export.")
            return
        target = filedialog.asksaveasfilename(
            title="Export experiment log to CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not target:
            return
        Path(target).write_text(self.experiment_log.to_csv_text(records), encoding="utf-8", newline="")
        self.status_var.set(f"Exported experiment log CSV to {target}.")

    def _export_log_json(self) -> None:
        records = self._filtered_log_records()
        if not records:
            messagebox.showinfo("Empty experiment log", "No log records are available to export.")
            return
        target = filedialog.asksaveasfilename(
            title="Export experiment log to JSON",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if not target:
            return
        Path(target).write_text(self.experiment_log.to_json_text(records), encoding="utf-8")
        self.status_var.set(f"Exported experiment log JSON to {target}.")

    def _copy_log_markdown_table(self) -> None:
        records = self._filtered_log_records()
        self.root.clipboard_clear()
        self.root.clipboard_append(self.experiment_log.to_markdown_table(records))
        self.status_var.set(f"Copied markdown table for {len(records)} log record(s).")

    def _clear_log(self) -> None:
        if self.experiment_log.records and not messagebox.askyesno("Clear experiment log", "Delete all experiment-log records from the current session?"):
            return
        self.experiment_log.clear()
        self._refresh_log_table()
        self.status_var.set("Cleared experiment log.")


def launch_braid_workbench_gui() -> None:
    root = tk.Tk()
    BraidWorkbenchApp(root)
    root.mainloop()
