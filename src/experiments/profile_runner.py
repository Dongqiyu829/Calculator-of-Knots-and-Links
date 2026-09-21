"""Run pairwise benchmark experiments across the three ordinary/mainline branches."""

from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass, field
from typing import Any

import sympy as sp

from src.experiments.benchmark_registry import BenchmarkPairDefinition
from src.invariants.branch_registry import evaluate_current_branches
from src.invariants.branch_results import InvariantBranchResult
from src.workbench.specs import WORKBENCH_MODEL_SPECS


EXPERIMENT_MODEL_ORDER = ("sl2_fundamental", "sl2_3d_9x9", "sl3_fundamental")
PROFILE_DIGIT_BY_RELATION = {"same": 0, "different": 1}


@dataclass(frozen=True, slots=True)
class PairBranchResult:
    """Store the pairwise comparison outcome for one model."""

    model_id: str
    display_name: str
    output_a: str
    output_b: str
    relation: str
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "display_name": self.display_name,
            "output_a": self.output_a,
            "output_b": self.output_b,
            "relation": self.relation,
            "notes": self.notes,
        }


@dataclass(frozen=True, slots=True)
class BenchmarkPairResult:
    """Store one benchmark pair run result together with profile metadata."""

    pair_id: str
    group: str
    q_mode: str
    branch_results: tuple[PairBranchResult, ...]
    observed_profile: str
    expected_profile: str
    match_expected: str
    status: str
    notes: str = ""
    warnings: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def branch_result(self, model_id: str) -> PairBranchResult:
        for result in self.branch_results:
            if result.model_id == model_id:
                return result
        raise KeyError(f"Unknown model id: {model_id}")

    def to_pair_level_row(self) -> dict[str, Any]:
        sl2 = self.branch_result("sl2_fundamental")
        sl2_3d = self.branch_result("sl2_3d_9x9")
        sl3 = self.branch_result("sl3_fundamental")
        combined_notes = self.notes
        if self.warnings:
            warning_text = " | ".join(self.warnings)
            combined_notes = warning_text if not combined_notes else f"{combined_notes} | {warning_text}"
        return {
            "pair_id": self.pair_id,
            "q_mode": self.q_mode,
            "sl2_fundamental_A": sl2.output_a,
            "sl2_fundamental_B": sl2.output_b,
            "sl2_fundamental_relation": sl2.relation,
            "sl2_3d_A": sl2_3d.output_a,
            "sl2_3d_B": sl2_3d.output_b,
            "sl2_3d_relation": sl2_3d.relation,
            "sl3_fundamental_A": sl3.output_a,
            "sl3_fundamental_B": sl3.output_b,
            "sl3_fundamental_relation": sl3.relation,
            "observed_profile": self.observed_profile,
            "match_expected": self.match_expected,
            "notes": combined_notes,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "pair_id": self.pair_id,
            "group": self.group,
            "q_mode": self.q_mode,
            "branch_results": [result.to_dict() for result in self.branch_results],
            "observed_profile": self.observed_profile,
            "expected_profile": self.expected_profile,
            "match_expected": self.match_expected,
            "status": self.status,
            "notes": self.notes,
            "warnings": list(self.warnings),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class BenchmarkExperimentRun:
    """Store a full benchmark experiment run over a set of benchmark pairs."""

    q_mode: str
    input_path: str
    pair_results: tuple[BenchmarkPairResult, ...]
    warnings: tuple[str, ...] = ()

    def pair_level_rows(self) -> list[dict[str, Any]]:
        return [result.to_pair_level_row() for result in self.pair_results]

    def to_pair_level_csv_text(self) -> str:
        rows = self.pair_level_rows()
        if not rows:
            return ""
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=list(rows[0]))
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
        return buffer.getvalue()

    def to_pair_level_json_text(self) -> str:
        return json.dumps([result.to_dict() for result in self.pair_results], indent=2, ensure_ascii=False)

    def to_pair_level_markdown(self) -> str:
        return _rows_to_markdown(self.pair_level_rows())


def run_benchmark_experiment(
    benchmark_pairs: tuple[BenchmarkPairDefinition, ...] | list[BenchmarkPairDefinition],
    *,
    q_parameter_expr: sp.Expr,
    q_parameter_text: str,
    input_path: str,
) -> BenchmarkExperimentRun:
    """Run all benchmark pairs for the requested q mode."""

    pair_results: list[BenchmarkPairResult] = []
    warnings: list[str] = []
    for benchmark_pair in benchmark_pairs:
        pair_result = run_benchmark_pair(
            benchmark_pair,
            q_parameter_expr=q_parameter_expr,
            q_parameter_text=q_parameter_text,
        )
        pair_results.append(pair_result)
        for warning in pair_result.warnings:
            warnings.append(f"{benchmark_pair.pair_id}: {warning}")
    return BenchmarkExperimentRun(
        q_mode=q_parameter_text,
        input_path=input_path,
        pair_results=tuple(pair_results),
        warnings=tuple(warnings),
    )


def run_benchmark_pair(
    benchmark_pair: BenchmarkPairDefinition,
    *,
    q_parameter_expr: sp.Expr,
    q_parameter_text: str,
) -> BenchmarkPairResult:
    """Run one benchmark pair through the three ordinary/mainline branches."""

    if benchmark_pair.should_skip:
        return _build_skipped_pair_result(benchmark_pair, q_mode=q_parameter_text)

    braid_word_a = benchmark_pair.braid_a.to_braid_word()
    braid_word_b = benchmark_pair.braid_b.to_braid_word()
    if braid_word_a is None or braid_word_b is None:
        return _build_skipped_pair_result(benchmark_pair, q_mode=q_parameter_text)

    branch_results_a = _evaluate_branch_results_by_model(braid_word_a, q=q_parameter_expr)
    branch_results_b = _evaluate_branch_results_by_model(braid_word_b, q=q_parameter_expr)
    pair_branch_results: list[PairBranchResult] = []
    relation_by_model: dict[str, str] = {}

    for model_id in EXPERIMENT_MODEL_ORDER:
        result_a = branch_results_a[model_id]
        result_b = branch_results_b[model_id]
        relation = compare_branch_outputs(
            result_a.primary_output,
            result_b.primary_output,
            q_parameter_text=q_parameter_text,
        )
        relation_by_model[model_id] = relation
        pair_branch_results.append(
            PairBranchResult(
                model_id=model_id,
                display_name=WORKBENCH_MODEL_SPECS[model_id].display_name,
                output_a=str(sp.simplify(result_a.primary_output)),
                output_b=str(sp.simplify(result_b.primary_output)),
                relation=relation,
            )
        )

    observed_profile = observed_profile_from_relations(relation_by_model)
    match_expected = compare_expected_and_observed(benchmark_pair, relation_by_model, observed_profile)
    return BenchmarkPairResult(
        pair_id=benchmark_pair.pair_id,
        group=benchmark_pair.group,
        q_mode=q_parameter_text,
        branch_results=tuple(pair_branch_results),
        observed_profile=observed_profile,
        expected_profile=benchmark_pair.expected_profile,
        match_expected=match_expected,
        status="completed",
        notes=benchmark_pair.notes,
        warnings=benchmark_pair.warnings,
        metadata={
            "expected_relations": dict(benchmark_pair.expected_relations),
            "source_status": benchmark_pair.status_of_braid_source,
        },
    )


def compare_branch_outputs(left: sp.Expr | None, right: sp.Expr | None, *, q_parameter_text: str) -> str:
    """Compare two branch outputs under numeric or symbolic q mode."""

    if left is None or right is None:
        return "skipped"
    left_simplified = sp.simplify(left)
    right_simplified = sp.simplify(right)
    if q_parameter_text == "q":
        return "same" if sp.simplify(left_simplified - right_simplified) == 0 else "different"
    return "same" if left_simplified == right_simplified else "different"


def observed_profile_from_relations(relation_by_model: dict[str, str]) -> str:
    """Build the fixed-order separation profile text from branch relations."""

    digits: list[int] = []
    for model_id in EXPERIMENT_MODEL_ORDER:
        relation = relation_by_model.get(model_id, "skipped")
        if relation not in PROFILE_DIGIT_BY_RELATION:
            return "skipped"
        digits.append(PROFILE_DIGIT_BY_RELATION[relation])
    return f"({digits[0]},{digits[1]},{digits[2]})"


def compare_expected_and_observed(
    benchmark_pair: BenchmarkPairDefinition,
    relation_by_model: dict[str, str],
    observed_profile: str,
) -> str:
    """Compare expected metadata against the observed run result."""

    if benchmark_pair.should_skip or observed_profile == "skipped":
        return "partial"

    has_unknown_expectation = False
    for model_id, expected_relation in benchmark_pair.expected_relations.items():
        if expected_relation in {"", "unknown", "skipped"}:
            has_unknown_expectation = True
            continue
        if relation_by_model.get(model_id) != expected_relation:
            return "no"

    expected_profile = benchmark_pair.expected_profile.strip()
    if expected_profile:
        if observed_profile != expected_profile:
            return "no"
    else:
        has_unknown_expectation = True

    return "partial" if has_unknown_expectation else "yes"


def _evaluate_branch_results_by_model(braid_word: Any, *, q: sp.Expr) -> dict[str, InvariantBranchResult]:
    branch_results = evaluate_current_branches(
        braid_word,
        branch_ids=tuple(spec.branch_id for spec in WORKBENCH_MODEL_SPECS.values()),
        q=q,
    )
    branch_to_model = {spec.branch_id: model_id for model_id, spec in WORKBENCH_MODEL_SPECS.items()}
    return {branch_to_model[result.branch_id]: result for result in branch_results}


def _build_skipped_pair_result(benchmark_pair: BenchmarkPairDefinition, *, q_mode: str) -> BenchmarkPairResult:
    skip_reason = benchmark_pair.skip_reason or "missing_braid"
    pair_branch_results = tuple(
        PairBranchResult(
            model_id=model_id,
            display_name=WORKBENCH_MODEL_SPECS[model_id].display_name,
            output_a="skipped",
            output_b="skipped",
            relation="skipped",
            notes=f"Skipped because {skip_reason}.",
        )
        for model_id in EXPERIMENT_MODEL_ORDER
    )
    warnings = list(benchmark_pair.warnings)
    if skip_reason == "needs_audit":
        warnings.append("needs_audit pair was not evaluated.")
    else:
        warnings.append("missing braid data prevented evaluation.")
    return BenchmarkPairResult(
        pair_id=benchmark_pair.pair_id,
        group=benchmark_pair.group,
        q_mode=q_mode,
        branch_results=pair_branch_results,
        observed_profile="skipped",
        expected_profile=benchmark_pair.expected_profile,
        match_expected="partial",
        status="skipped",
        notes=benchmark_pair.notes,
        warnings=tuple(warnings),
        metadata={
            "expected_relations": dict(benchmark_pair.expected_relations),
            "source_status": benchmark_pair.status_of_braid_source,
            "skip_reason": skip_reason,
        },
    )


def _rows_to_markdown(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "No rows."
    headers = list(rows[0])
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(_markdown_escape(row[header]) for header in headers) + " |")
    return "\n".join(lines)


def _markdown_escape(value: Any) -> str:
    return str(value).replace("|", "\\|")
