"""Unified batch runner and table exports for the ordinary braid workbench."""

from __future__ import annotations

import csv
import io
import json
from collections import Counter
from dataclasses import dataclass, field
from itertools import combinations
from typing import Any

import sympy as sp

from src.gui import demo_launcher as current_gui
from src.invariants.branch_results import InvariantBranchResult
from src.invariants.multibranch_benchmark import MultiBranchBenchmarkEntry
from src.workbench.comparison import WORKBENCH_CLASSIFICATION_DESCRIPTIONS, classify_workbench_pair
from src.workbench.specs import ComparisonRunSpec, WORKBENCH_DEFAULT_MODELS, WORKBENCH_MODEL_SPECS


RESULT_TABLE_SINGLE = "single"
RESULT_TABLE_PAIRWISE = "pairwise"
RESULT_TABLE_SUMMARY = "summary"
EXTRA_CLASSIFICATION_DESCRIPTIONS = {
    "selected_models_all_same": "All currently selected comparison models give the same output on the pair.",
    "selected_models_all_different": "All currently selected comparison models distinguish the pair.",
    "selected_models_mixed": "The currently selected comparison models do not agree uniformly on the pair.",
}


@dataclass(frozen=True, slots=True)
class SingleBraidResultRow:
    label: str
    num_strands: int
    generators: tuple[int, ...]
    sl2_fundamental_output: str
    sl2_3d_9x9_output: str
    sl3_fundamental_output: str
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "num_strands": self.num_strands,
            "generators": list(self.generators),
            "sl2_fundamental_output": self.sl2_fundamental_output,
            "sl2_3d_9x9_output": self.sl2_3d_9x9_output,
            "sl3_fundamental_output": self.sl3_fundamental_output,
            "notes": self.notes,
        }


@dataclass(frozen=True, slots=True)
class PairwiseComparisonRow:
    pair_label: str
    braid_a: str
    braid_b: str
    sl2_fundamental_same: str
    sl2_3d_9x9_same: str
    sl3_fundamental_same: str
    classification: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "pair_label": self.pair_label,
            "braid_a": self.braid_a,
            "braid_b": self.braid_b,
            "sl2_fundamental_same": self.sl2_fundamental_same,
            "sl2_3d_9x9_same": self.sl2_3d_9x9_same,
            "sl3_fundamental_same": self.sl3_same,
            "classification": self.classification,
        }

    @property
    def sl3_same(self) -> str:
        return self.sl3_fundamental_same


@dataclass(frozen=True, slots=True)
class SummaryCountRow:
    classification: str
    count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "classification": self.classification,
            "count": self.count,
        }


@dataclass(frozen=True, slots=True)
class WorkbenchBatchRunResult:
    run_spec: ComparisonRunSpec
    single_rows: tuple[SingleBraidResultRow, ...]
    pairwise_rows: tuple[PairwiseComparisonRow, ...]
    summary_rows: tuple[SummaryCountRow, ...]
    single_entries: tuple[MultiBranchBenchmarkEntry, ...] = ()
    pair_metadata: tuple[dict[str, Any], ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_spec": {
                "input_source": self.run_spec.input_source,
                "q_parameter": self.run_spec.q_parameter_text,
                "models": list(self.run_spec.models),
                "comparison_mode": self.run_spec.comparison_mode,
                "braids": [
                    {
                        "label": braid_spec.label,
                        "num_strands": braid_spec.num_strands,
                        "generators": list(braid_spec.generators),
                        "notes": braid_spec.notes,
                    }
                    for braid_spec in self.run_spec.batch.braids
                ],
            },
            "single_braid_result_table": [row.to_dict() for row in self.single_rows],
            "pairwise_comparison_table": [row.to_dict() for row in self.pairwise_rows],
            "summary_table": [row.to_dict() for row in self.summary_rows],
            "pair_metadata": [dict(item) for item in self.pair_metadata],
        }

    def table_rows(self, table_id: str) -> list[dict[str, Any]]:
        if table_id == RESULT_TABLE_SINGLE:
            return [row.to_dict() for row in self.single_rows]
        if table_id == RESULT_TABLE_PAIRWISE:
            return [row.to_dict() for row in self.pairwise_rows]
        if table_id == RESULT_TABLE_SUMMARY:
            return [row.to_dict() for row in self.summary_rows]
        raise ValueError(f"Unknown result table id: {table_id}")

    def to_json_text(self, table_id: str | None = None) -> str:
        if table_id is None:
            return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
        return json.dumps({table_id: self.table_rows(table_id)}, indent=2, ensure_ascii=False)

    def to_csv_text(self, table_id: str) -> str:
        rows = self.table_rows(table_id)
        if not rows:
            return ""
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=list(rows[0]))
        writer.writeheader()
        for row in rows:
            writer.writerow({key: json.dumps(value, ensure_ascii=False) if isinstance(value, list) else value for key, value in row.items()})
        return buffer.getvalue()

    def to_markdown_table(self, table_id: str) -> str:
        rows = self.table_rows(table_id)
        if not rows:
            return "No rows."
        headers = list(rows[0])
        lines = [
            "| " + " | ".join(headers) + " |",
            "| " + " | ".join("---" for _ in headers) + " |",
        ]
        for row in rows:
            lines.append(
                "| " + " | ".join(
                    json.dumps(value, ensure_ascii=False) if isinstance(value, list) else str(value)
                    for value in row.values()
                ) + " |"
            )
        return "\n".join(lines)


def _simplified_equal(left: sp.Expr, right: sp.Expr) -> bool:
    return sp.simplify(left - right) == 0


def _branch_outputs_by_model(entry: MultiBranchBenchmarkEntry) -> dict[str, str]:
    outputs = {
        "sl2_fundamental": "not_selected",
        "sl2_3d_9x9": "not_selected",
        "sl3_fundamental": "not_selected",
    }
    branch_to_model = {spec.branch_id: model_id for model_id, spec in WORKBENCH_MODEL_SPECS.items()}
    for branch_result in entry.branch_results:
        model_id = branch_to_model[branch_result.branch_id]
        outputs[model_id] = str(sp.simplify(branch_result.primary_output))
    return outputs


def _entry_branch_results_by_model(entry: MultiBranchBenchmarkEntry) -> dict[str, InvariantBranchResult]:
    branch_to_model = {spec.branch_id: model_id for model_id, spec in WORKBENCH_MODEL_SPECS.items()}
    return {
        branch_to_model[result.branch_id]: result
        for result in entry.branch_results
    }


def _classify_selected_models(same_by_model: dict[str, bool | None], selected_models: tuple[str, ...]) -> str:
    if tuple(selected_models) == WORKBENCH_DEFAULT_MODELS:
        return classify_workbench_pair(
            bool(same_by_model["sl2_fundamental"]),
            bool(same_by_model["sl2_3d_9x9"]),
            bool(same_by_model["sl3_fundamental"]),
        )

    active_values = [same_by_model[model_id] for model_id in selected_models if same_by_model[model_id] is not None]
    if active_values and all(active_values):
        return "selected_models_all_same"
    if active_values and not any(active_values):
        return "selected_models_all_different"
    return "selected_models_mixed"


def get_classification_description(classification: str) -> str:
    return WORKBENCH_CLASSIFICATION_DESCRIPTIONS.get(classification, EXTRA_CLASSIFICATION_DESCRIPTIONS.get(classification, classification))


def evaluate_workbench_run(run_spec: ComparisonRunSpec) -> WorkbenchBatchRunResult:
    single_entries: list[MultiBranchBenchmarkEntry] = []
    single_rows: list[SingleBraidResultRow] = []

    for braid_spec in run_spec.batch.braids:
        entry = current_gui.evaluate_gui_braid_word(
            braid_spec.to_braid_word(),
            branch_ids=run_spec.branch_ids,
            q=run_spec.q_parameter_expr,
        )
        outputs = _branch_outputs_by_model(entry)
        single_entries.append(entry)
        single_rows.append(
            SingleBraidResultRow(
                label=braid_spec.label,
                num_strands=braid_spec.num_strands,
                generators=braid_spec.generators,
                sl2_fundamental_output=outputs["sl2_fundamental"],
                sl2_3d_9x9_output=outputs["sl2_3d_9x9"],
                sl3_fundamental_output=outputs["sl3_fundamental"],
                notes=braid_spec.notes,
            )
        )

    pairwise_rows: list[PairwiseComparisonRow] = []
    pair_metadata: list[dict[str, Any]] = []
    if run_spec.comparison_mode in {"pairwise", "all"}:
        entry_by_label = {entry.example_label: entry for entry in single_entries}
        for braid_a, braid_b in combinations(run_spec.batch.braids, 2):
            entry_a = entry_by_label[braid_a.label]
            entry_b = entry_by_label[braid_b.label]
            results_a = _entry_branch_results_by_model(entry_a)
            results_b = _entry_branch_results_by_model(entry_b)
            same_by_model: dict[str, bool | None] = {model_id: None for model_id in WORKBENCH_MODEL_SPECS}
            for model_id in WORKBENCH_MODEL_SPECS:
                if model_id in results_a and model_id in results_b:
                    same_by_model[model_id] = _simplified_equal(
                        sp.sympify(results_a[model_id].primary_output),
                        sp.sympify(results_b[model_id].primary_output),
                    )
            classification = _classify_selected_models(same_by_model, run_spec.models)
            pair_label = f"{braid_a.label}_vs_{braid_b.label}"
            pairwise_rows.append(
                PairwiseComparisonRow(
                    pair_label=pair_label,
                    braid_a=braid_a.label,
                    braid_b=braid_b.label,
                    sl2_fundamental_same=_same_or_not_selected(same_by_model["sl2_fundamental"]),
                    sl2_3d_9x9_same=_same_or_not_selected(same_by_model["sl2_3d_9x9"]),
                    sl3_fundamental_same=_same_or_not_selected(same_by_model["sl3_fundamental"]),
                    classification=classification,
                )
            )
            pair_metadata.append(
                {
                    "pair_label": pair_label,
                    "classification_description": get_classification_description(classification),
                    "same_by_model": {key: value for key, value in same_by_model.items()},
                }
            )

    summary_rows = tuple(
        SummaryCountRow(classification=classification, count=count)
        for classification, count in sorted(Counter(row.classification for row in pairwise_rows).items())
    )
    return WorkbenchBatchRunResult(
        run_spec=run_spec,
        single_rows=tuple(single_rows),
        pairwise_rows=tuple(pairwise_rows),
        summary_rows=summary_rows,
        single_entries=tuple(single_entries),
        pair_metadata=tuple(pair_metadata),
    )


def _same_or_not_selected(value: bool | None) -> str:
    if value is None:
        return "not_selected"
    return "same" if value else "different"
