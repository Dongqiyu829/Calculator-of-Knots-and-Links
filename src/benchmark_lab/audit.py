"""Detailed audit helpers for individual benchmark-lab pairs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import sympy as sp

from .branch_adapter import BENCHMARK_MODEL_ORDER, BENCHMARK_MODEL_SPECS, evaluate_models_for_braid
from .profile_runner import compare_branch_outputs
from .registry import BenchmarkPairDefinition, BenchmarkBraidSide


@dataclass(frozen=True, slots=True)
class BranchAuditRecord:
    """Store a detailed per-branch audit entry."""

    model_id: str
    display_name: str
    output_a: str
    output_b: str
    relation: str
    symbolic_difference: str | None
    numeric_witness: str | None
    decision_notes: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "display_name": self.display_name,
            "output_a": self.output_a,
            "output_b": self.output_b,
            "relation": self.relation,
            "symbolic_difference": self.symbolic_difference,
            "numeric_witness": self.numeric_witness,
            "decision_notes": self.decision_notes,
        }


@dataclass(frozen=True, slots=True)
class PairAuditRecord:
    """Store the full audit result for one benchmark pair."""

    pair_id: str
    q_mode: str
    status: str
    braid_a: dict[str, Any]
    braid_b: dict[str, Any]
    branch_audits: tuple[BranchAuditRecord, ...]
    warnings: tuple[str, ...] = ()
    notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "pair_id": self.pair_id,
            "q_mode": self.q_mode,
            "status": self.status,
            "braid_a": dict(self.braid_a),
            "braid_b": dict(self.braid_b),
            "branch_audits": [audit.to_dict() for audit in self.branch_audits],
            "warnings": list(self.warnings),
            "notes": self.notes,
            "metadata": dict(self.metadata),
        }

    def to_markdown(self) -> str:
        lines = [f"# Audit {self.pair_id} (q={self.q_mode})", "", f"Status: {self.status}"]
        if self.notes:
            lines.extend(["", f"Notes: {self.notes}"])
        if self.warnings:
            lines.extend(["", "Warnings:"])
            lines.extend([f"- {warning}" for warning in self.warnings])

        lines.extend(["", "## Braid A", _render_braid_section(self.braid_a)])
        lines.extend(["", "## Braid B", _render_braid_section(self.braid_b)])
        lines.extend(["", "## Branch audits"])
        for branch_audit in self.branch_audits:
            lines.extend(
                [
                    "",
                    f"### {branch_audit.display_name}",
                    f"- relation: {branch_audit.relation}",
                    f"- output A: {branch_audit.output_a}",
                    f"- output B: {branch_audit.output_b}",
                    f"- decision: {branch_audit.decision_notes}",
                    f"- symbolic difference: {branch_audit.symbolic_difference or 'n/a'}",
                    f"- numeric witness: {branch_audit.numeric_witness or 'n/a'}",
                ]
            )
        return "\n".join(lines)


def audit_pair(benchmark_pair: BenchmarkPairDefinition, *, q_parameter: sp.Expr, q_mode: str) -> PairAuditRecord:
    """Run a detailed audit for one benchmark-lab pair."""

    braid_a_info = _side_to_audit_dict(benchmark_pair.braid_a)
    braid_b_info = _side_to_audit_dict(benchmark_pair.braid_b)
    if benchmark_pair.should_skip:
        warnings = list(benchmark_pair.warnings)
        skip_reason = benchmark_pair.skip_reason or "missing_braid"
        if skip_reason == "needs_audit":
            warnings.append("Audit skipped because the pair is marked needs_audit.")
        else:
            warnings.append("Audit skipped because a braid side is still placeholder data.")
        return PairAuditRecord(
            pair_id=benchmark_pair.pair_id,
            q_mode=q_mode,
            status="skipped",
            braid_a=braid_a_info,
            braid_b=braid_b_info,
            branch_audits=tuple(),
            warnings=tuple(warnings),
            notes=benchmark_pair.notes,
            metadata={"skip_reason": skip_reason},
        )

    braid_word_a = benchmark_pair.braid_a.to_braid_word()
    braid_word_b = benchmark_pair.braid_b.to_braid_word()
    if braid_word_a is None or braid_word_b is None:
        return PairAuditRecord(
            pair_id=benchmark_pair.pair_id,
            q_mode=q_mode,
            status="skipped",
            braid_a=braid_a_info,
            braid_b=braid_b_info,
            branch_audits=tuple(),
            warnings=("Audit skipped because braid data is missing.",),
            notes=benchmark_pair.notes,
            metadata={"skip_reason": "missing_braid"},
        )

    results_a = evaluate_models_for_braid(braid_word_a, q_parameter=q_parameter)
    results_b = evaluate_models_for_braid(braid_word_b, q_parameter=q_parameter)
    branch_audits: list[BranchAuditRecord] = []
    for model_id in BENCHMARK_MODEL_ORDER:
        left = results_a[model_id].primary_output
        right = results_b[model_id].primary_output
        comparison = build_comparison_details(left, right, q_mode=q_mode)
        branch_audits.append(
            BranchAuditRecord(
                model_id=model_id,
                display_name=BENCHMARK_MODEL_SPECS[model_id].display_name,
                output_a=comparison["output_a"],
                output_b=comparison["output_b"],
                relation=comparison["relation"],
                symbolic_difference=comparison["symbolic_difference"],
                numeric_witness=comparison["numeric_witness"],
                decision_notes=comparison["decision_notes"],
            )
        )

    return PairAuditRecord(
        pair_id=benchmark_pair.pair_id,
        q_mode=q_mode,
        status="completed",
        braid_a=braid_a_info,
        braid_b=braid_b_info,
        branch_audits=tuple(branch_audits),
        warnings=benchmark_pair.warnings,
        notes=benchmark_pair.notes,
        metadata={
            "expected_profile": benchmark_pair.expected_profile,
            "expected_relations": dict(benchmark_pair.expected_relations),
        },
    )


def build_comparison_details(left: sp.Expr | None, right: sp.Expr | None, *, q_mode: str) -> dict[str, str | None]:
    """Build the detailed same/different decision payload used by audit output."""

    if left is None or right is None:
        return {
            "output_a": "not available",
            "output_b": "not available",
            "relation": "skipped",
            "symbolic_difference": None,
            "numeric_witness": None,
            "decision_notes": "At least one branch output is missing, so the audit marks this branch as skipped.",
        }

    simplified_left = sp.simplify(left)
    simplified_right = sp.simplify(right)
    difference = sp.simplify(simplified_left - simplified_right)
    relation = compare_branch_outputs(simplified_left, simplified_right, q_mode=q_mode)
    if q_mode == "q":
        decision_notes = (
            "Symbolic mode compares sympy.simplify(output_A - output_B) against 0. "
            f"The simplified difference is {difference}."
        )
        return {
            "output_a": str(simplified_left),
            "output_b": str(simplified_right),
            "relation": relation,
            "symbolic_difference": str(difference),
            "numeric_witness": None,
            "decision_notes": decision_notes,
        }

    decision_notes = (
        "Numeric mode simplifies both outputs and then performs strict equality on the resulting SymPy expressions. "
        f"The simplified numeric witness output_A - output_B is {difference}."
    )
    return {
        "output_a": str(simplified_left),
        "output_b": str(simplified_right),
        "relation": relation,
        "symbolic_difference": None,
        "numeric_witness": str(difference),
        "decision_notes": decision_notes,
    }


def _side_to_audit_dict(side: BenchmarkBraidSide) -> dict[str, Any]:
    return {
        "label": side.label,
        "source": side.source,
        "num_strands": side.num_strands,
        "generators": list(side.generators),
        "writhe": side.writhe(),
        "is_placeholder": side.is_placeholder,
    }


def _render_braid_section(side_data: dict[str, Any]) -> str:
    lines = [
        f"- label: {side_data['label']}",
        f"- source: {side_data['source']}",
        f"- num_strands: {side_data['num_strands']}",
        f"- generators: {side_data['generators']}",
        f"- writhe: {side_data['writhe']}",
        f"- is_placeholder: {side_data['is_placeholder']}",
    ]
    return "\n".join(lines)
