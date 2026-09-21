"""Unified text-formatting helpers for branch results and multi-branch benchmark reports."""

from __future__ import annotations

from collections.abc import Iterable

import sympy as sp

from .branch_results import InvariantBranchResult
from .multibranch_benchmark import MultiBranchBenchmarkEntry


def _stringify_expression(expr: object | None) -> str:
    if expr is None:
        return "not available"
    return str(sp.simplify(expr))


def _format_branch_specific_lines(branch_result: InvariantBranchResult) -> list[str]:
    metadata = branch_result.metadata
    lines: list[str] = []

    if branch_result.branch_id == "sl2_fundamental":
        if "unreduced_p2_output" in metadata:
            lines.append(f"Unreduced P2: {metadata['unreduced_p2_output']}")
        if "unknot_normalization" in metadata:
            lines.append(f"Unknot normalization: {metadata['unknot_normalization']}")
        if "reduced_p2_output" in metadata:
            lines.append(f"Reduced P2: {metadata['reduced_p2_output']}")
    elif branch_result.branch_id == "sl2_spin1":
        if "quantum_trace_before_normalization" in metadata:
            lines.append(f"Quantum trace before normalization: {metadata['quantum_trace_before_normalization']}")
        if "unreduced_candidate_output" in metadata:
            lines.append(f"Unreduced candidate output: {metadata['unreduced_candidate_output']}")
        if "unknot_normalization" in metadata:
            lines.append(f"Unknot normalization: {metadata['unknot_normalization']}")
        if "reduced_candidate_output" in metadata:
            lines.append(f"Reduced candidate output: {metadata['reduced_candidate_output']}")
        if "branch_note" in metadata:
            lines.append(f"Branch note: {metadata['branch_note']}")
        if "projector_checks" in metadata:
            lines.append(f"Projector-aware checks: {metadata['projector_checks']}")

    return lines


def format_branch_result(branch_result: InvariantBranchResult) -> str:
    """Format one branch result in a uniform CLI-friendly report block."""

    lines = [
        f"=== {branch_result.display_name} ===",
        f"Representation: {branch_result.representation_name}",
        f"Braid word: {branch_result.braid_word.word_string()}",
        f"Status: {branch_result.status}",
        f"Raw trace: {_stringify_expression(branch_result.raw_trace)}",
        f"Primary output label: {branch_result.primary_output_label}",
        f"Primary output: {_stringify_expression(branch_result.primary_output)}",
        f"Normalization label: {branch_result.normalization_label}",
        f"Variable convention: {branch_result.variable_convention}",
    ]
    lines.extend(_format_branch_specific_lines(branch_result))
    if branch_result.notes:
        lines.append(f"Notes: {branch_result.notes}")
    return "\n".join(lines)


def format_multibranch_entry(entry: MultiBranchBenchmarkEntry) -> str:
    """Format one multi-branch benchmark entry for terminal display."""

    lines = [f"########## {entry.example_label} ##########"]
    if entry.notes:
        lines.append(f"Notes: {entry.notes}")
    for index, branch_result in enumerate(entry.branch_results, start=1):
        lines.append("")
        lines.append(format_branch_result(branch_result))
        if index != len(entry.branch_results):
            lines.append("")
    return "\n".join(lines)


def format_catalog_benchmark(entries: Iterable[MultiBranchBenchmarkEntry]) -> str:
    """Format a catalog slice across branches as one CLI-friendly report."""

    entry_list = list(entries)
    lines = [
        "=== Multi-branch invariant report ===",
        "This report uses the shared formatter layer for branch-level and catalog-level output.",
    ]
    if not entry_list:
        lines.append("No benchmark entries available.")
        return "\n".join(lines)

    for entry in entry_list:
        lines.append("")
        lines.append(format_multibranch_entry(entry))
    return "\n".join(lines)