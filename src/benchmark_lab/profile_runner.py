"""Pairwise profile runner for the independent benchmark lab."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import sympy as sp

from .branch_adapter import BENCHMARK_MODEL_ORDER, BENCHMARK_MODEL_SPECS, evaluate_models_for_braid
from .registry import BenchmarkPairDefinition


RELATION_TO_DIGIT = {"same": 0, "different": 1}


@dataclass(frozen=True, slots=True)
class PairBranchRecord:
    """Store the pairwise outcome of one branch for one benchmark pair."""

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
class PairResultRecord:
    """Store one completed or skipped benchmark pair result."""

    pair_id: str
    group: str
    q_mode: str
    branch_records: tuple[PairBranchRecord, ...]
    observed_profile: str
    expected_profile: str
    match_expected: str
    status: str
    notes: str = ""
    warnings: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def branch_record(self, model_id: str) -> PairBranchRecord:
        for record in self.branch_records:
            if record.model_id == model_id:
                return record
        raise KeyError(f"Unknown model id: {model_id}")

    def to_pair_level_row(self) -> dict[str, Any]:
        sl2 = self.branch_record("sl2_fundamental")
        sl2_3d = self.branch_record("sl2_3d_9x9")
        sl3 = self.branch_record("sl3_fundamental")
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
            "expected_profile": self.expected_profile,
            "match_expected": self.match_expected,
            "status": self.status,
            "notes": combined_notes,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "pair_id": self.pair_id,
            "group": self.group,
            "q_mode": self.q_mode,
            "branch_records": [record.to_dict() for record in self.branch_records],
            "observed_profile": self.observed_profile,
            "expected_profile": self.expected_profile,
            "match_expected": self.match_expected,
            "status": self.status,
            "notes": self.notes,
            "warnings": list(self.warnings),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class ProfileExperimentRun:
    """Store a full benchmark lab profile experiment run."""

    input_path: str
    q_mode: str
    pair_results: tuple[PairResultRecord, ...]
    warnings: tuple[str, ...] = ()

    def pair_level_rows(self) -> list[dict[str, Any]]:
        return [result.to_pair_level_row() for result in self.pair_results]

    def to_dict(self) -> dict[str, Any]:
        return {
            "input_path": self.input_path,
            "q_mode": self.q_mode,
            "pair_results": [result.to_dict() for result in self.pair_results],
            "warnings": list(self.warnings),
        }


def run_profile_experiment(
    benchmark_pairs: tuple[BenchmarkPairDefinition, ...] | list[BenchmarkPairDefinition],
    *,
    q_parameter: sp.Expr,
    q_mode: str,
    input_path: str,
) -> ProfileExperimentRun:
    """Run the benchmark lab over all provided pairs."""

    pair_results: list[PairResultRecord] = []
    warnings: list[str] = []
    for benchmark_pair in benchmark_pairs:
        result = run_pair_profile(benchmark_pair, q_parameter=q_parameter, q_mode=q_mode)
        pair_results.append(result)
        for warning in result.warnings:
            warnings.append(f"{benchmark_pair.pair_id}: {warning}")
    return ProfileExperimentRun(
        input_path=input_path,
        q_mode=q_mode,
        pair_results=tuple(pair_results),
        warnings=tuple(warnings),
    )


def run_pair_profile(
    benchmark_pair: BenchmarkPairDefinition,
    *,
    q_parameter: sp.Expr,
    q_mode: str,
) -> PairResultRecord:
    """Run one benchmark pair and produce the observed separation profile."""

    if benchmark_pair.should_skip:
        return _build_skipped_pair_result(benchmark_pair, q_mode=q_mode)

    braid_word_a = benchmark_pair.braid_a.to_braid_word()
    braid_word_b = benchmark_pair.braid_b.to_braid_word()
    if braid_word_a is None or braid_word_b is None:
        return _build_skipped_pair_result(benchmark_pair, q_mode=q_mode)

    branch_results_a = evaluate_models_for_braid(braid_word_a, q_parameter=q_parameter)
    branch_results_b = evaluate_models_for_braid(braid_word_b, q_parameter=q_parameter)

    relation_by_model: dict[str, str] = {}
    branch_records: list[PairBranchRecord] = []
    for model_id in BENCHMARK_MODEL_ORDER:
        result_a = branch_results_a[model_id]
        result_b = branch_results_b[model_id]
        relation = compare_branch_outputs(result_a.primary_output, result_b.primary_output, q_mode=q_mode)
        relation_by_model[model_id] = relation
        branch_records.append(
            PairBranchRecord(
                model_id=model_id,
                display_name=BENCHMARK_MODEL_SPECS[model_id].display_name,
                output_a=str(sp.simplify(result_a.primary_output)),
                output_b=str(sp.simplify(result_b.primary_output)),
                relation=relation,
            )
        )

    observed_profile = build_observed_profile(relation_by_model)
    match_expected = compare_expected_to_observed(benchmark_pair, relation_by_model, observed_profile)
    return PairResultRecord(
        pair_id=benchmark_pair.pair_id,
        group=benchmark_pair.group,
        q_mode=q_mode,
        branch_records=tuple(branch_records),
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


def compare_branch_outputs(left: sp.Expr | None, right: sp.Expr | None, *, q_mode: str) -> str:
    """Compare two outputs using numeric or symbolic mode rules."""

    if left is None or right is None:
        return "skipped"
    simplified_left = sp.simplify(left)
    simplified_right = sp.simplify(right)
    if q_mode == "q":
        return "same" if sp.simplify(simplified_left - simplified_right) == 0 else "different"
    return "same" if simplified_left == simplified_right else "different"


def build_observed_profile(relation_by_model: dict[str, str]) -> str:
    """Convert model relations into the fixed-order profile tuple."""

    digits: list[int] = []
    for model_id in BENCHMARK_MODEL_ORDER:
        relation = relation_by_model.get(model_id, "skipped")
        if relation not in RELATION_TO_DIGIT:
            return "skipped"
        digits.append(RELATION_TO_DIGIT[relation])
    return f"({digits[0]},{digits[1]},{digits[2]})"


def compare_expected_to_observed(
    benchmark_pair: BenchmarkPairDefinition,
    relation_by_model: dict[str, str],
    observed_profile: str,
) -> str:
    """Return yes/no/partial when comparing expectations against observed data."""

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


def _build_skipped_pair_result(benchmark_pair: BenchmarkPairDefinition, *, q_mode: str) -> PairResultRecord:
    skip_reason = benchmark_pair.skip_reason or "missing_braid"
    warnings = list(benchmark_pair.warnings)
    if skip_reason == "needs_audit":
        warnings.append("needs_audit pair was not evaluated.")
    else:
        warnings.append("missing braid data prevented evaluation.")
    branch_records = tuple(
        PairBranchRecord(
            model_id=model_id,
            display_name=BENCHMARK_MODEL_SPECS[model_id].display_name,
            output_a="skipped",
            output_b="skipped",
            relation="skipped",
            notes=f"Skipped because {skip_reason}.",
        )
        for model_id in BENCHMARK_MODEL_ORDER
    )
    return PairResultRecord(
        pair_id=benchmark_pair.pair_id,
        group=benchmark_pair.group,
        q_mode=q_mode,
        branch_records=branch_records,
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
