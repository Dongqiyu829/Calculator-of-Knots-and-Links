"""Frontend-neutral result DTOs, conversion, reporting, and serialization."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

import sympy as sp

from src.invariants.branch_results import InvariantBranchResult
from src.invariants.multibranch_benchmark import MultiBranchBenchmarkEntry

from .branch_catalog import get_evaluation_branch


def _text(value: object | None) -> str | None:
    return None if value is None else str(sp.simplify(value))


@dataclass(frozen=True, slots=True)
class ApplicationBranchResult:
    """Stable frontend-facing representation of one branch evaluation."""

    model_id: str
    branch_id: str
    display_name: str
    status: str
    representation_name: str
    raw_trace: str | None
    primary_output: str | None
    primary_output_label: str
    normalization_label: str
    variable_convention: str
    notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "branch_id": self.branch_id,
            "display_name": self.display_name,
            "status": self.status,
            "representation_name": self.representation_name,
            "raw_trace": self.raw_trace,
            "primary_output": self.primary_output,
            "primary_output_label": self.primary_output_label,
            "normalization_label": self.normalization_label,
            "variable_convention": self.variable_convention,
            "notes": self.notes,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class ApplicationBraidResult:
    """Stable frontend-facing result for one catalog or custom braid input."""

    example_label: str
    num_strands: int
    generators: tuple[int, ...]
    word_string: str
    notes: str
    source_mode: str
    selected_branch_ids: tuple[str, ...] | None
    branch_results: tuple[ApplicationBranchResult, ...]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "example_label": self.example_label,
            "braid": {
                "num_strands": self.num_strands,
                "generators": list(self.generators),
                "word_string": self.word_string,
            },
            "notes": self.notes,
            "source_mode": self.source_mode,
            "selected_branch_ids": None if self.selected_branch_ids is None else list(self.selected_branch_ids),
            "branch_results": [result.to_dict() for result in self.branch_results],
            "metadata": dict(self.metadata),
        }


def application_branch_result_from_internal(result: InvariantBranchResult) -> ApplicationBranchResult:
    """Convert the existing mathematical-program result at the service boundary."""

    descriptor = get_evaluation_branch(result.branch_id)
    return ApplicationBranchResult(
        model_id=descriptor.model_id,
        branch_id=result.branch_id,
        display_name=descriptor.display_name,
        status=result.status,
        representation_name=result.representation_name,
        raw_trace=_text(result.raw_trace),
        primary_output=_text(result.primary_output),
        primary_output_label=result.primary_output_label,
        normalization_label=result.normalization_label,
        variable_convention=result.variable_convention,
        notes=result.notes,
        metadata=dict(result.metadata),
    )


def application_braid_result_from_internal(entry: MultiBranchBenchmarkEntry) -> ApplicationBraidResult:
    """Convert a recovered multibranch entry without changing evaluator behavior."""

    if entry.branch_results:
        braid_word = entry.branch_results[0].braid_word
    else:
        braid_data = entry.metadata.get("braid_word", {})
        braid_word = None
        num_strands = int(braid_data.get("num_strands", 0))
        generators = tuple(int(value) for value in braid_data.get("generators", ()))
        word_string = str(braid_data.get("word") or "identity")
    if braid_word is not None:
        num_strands = braid_word.num_strands
        generators = tuple(braid_word.generators)
        word_string = braid_word.word_string()
    selected = entry.metadata.get("selected_branch_ids")
    return ApplicationBraidResult(
        example_label=entry.example_label,
        num_strands=num_strands,
        generators=generators,
        word_string=word_string,
        notes=entry.notes,
        source_mode=str(entry.metadata.get("input_mode", "catalog")),
        selected_branch_ids=None if selected is None else tuple(str(value) for value in selected),
        branch_results=tuple(application_branch_result_from_internal(result) for result in entry.branch_results),
        metadata=dict(entry.metadata),
    )


def filter_application_braid_result(result: ApplicationBraidResult, branch_ids: tuple[str, ...] | list[str]) -> ApplicationBraidResult:
    """Return one DTO limited to currently visible branch ids."""

    selected = set(branch_ids)
    return ApplicationBraidResult(
        example_label=result.example_label,
        num_strands=result.num_strands,
        generators=result.generators,
        word_string=result.word_string,
        notes=result.notes,
        source_mode=result.source_mode,
        selected_branch_ids=tuple(branch_ids),
        branch_results=tuple(item for item in result.branch_results if item.branch_id in selected),
        metadata=dict(result.metadata),
    )


def format_application_branch_result(result: ApplicationBranchResult) -> str:
    """Format one DTO using the recovered formatter's visible report fields."""

    lines = [
        f"=== {result.display_name} ===",
        f"Representation: {result.representation_name}",
        f"Status: {result.status}",
        f"Raw trace: {result.raw_trace or 'not available'}",
        f"Primary output label: {result.primary_output_label}",
        f"Primary output: {result.primary_output or 'not available'}",
        f"Normalization label: {result.normalization_label}",
        f"Variable convention: {result.variable_convention}",
    ]
    for label, key in (
        ("Unreduced P2", "unreduced_p2_output"),
        ("Quantum trace before normalization", "quantum_trace_before_normalization"),
        ("Unreduced candidate output", "unreduced_candidate_output"),
        ("Unknot normalization", "unknot_normalization"),
        ("Reduced P2", "reduced_p2_output"),
        ("Reduced candidate output", "reduced_candidate_output"),
        ("Branch note", "branch_note"),
        ("Projector-aware checks", "projector_checks"),
    ):
        if key in result.metadata:
            lines.append(f"{label}: {result.metadata[key]}")
    if result.notes:
        lines.append(f"Notes: {result.notes}")
    return "\n".join(lines)


def format_application_braid_result(result: ApplicationBraidResult) -> str:
    """Format a full application result for text-oriented frontends."""

    lines = [f"########## {result.example_label} ##########"]
    if result.notes:
        lines.append(f"Notes: {result.notes}")
    for branch_result in result.branch_results:
        lines.extend(("", format_application_branch_result(branch_result)))
    return "\n".join(lines)


def serialize_application_braid_result(result: ApplicationBraidResult) -> str:
    """Return deterministic JSON suitable for raw views and export."""

    return json.dumps(result.to_dict(), indent=2, ensure_ascii=False, sort_keys=True)
