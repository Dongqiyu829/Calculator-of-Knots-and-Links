"""Pair-comparison helpers for the ordinary braid workbench."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import sympy as sp

from src.braid.braid_word import BraidWord
from src.services import ApplicationBraidResult, evaluate_braid_result


WORKBENCH_CLASSIFICATION_LABELS = (
    "both_distinguish",
    "neither_distinguishes",
    "only_sl2_3d_distinguishes",
    "only_sl3_distinguishes",
    "jones_same_sl3_diff",
    "jones_same_sl2_3d_diff",
    "all_same",
    "all_different",
)

WORKBENCH_CLASSIFICATION_DESCRIPTIONS = {
    "both_distinguish": "Jones stays the same, while sl2 3D and sl3 both distinguish the pair.",
    "neither_distinguishes": "Jones distinguishes the pair, while sl2 3D and sl3 both stay the same.",
    "only_sl2_3d_distinguishes": "sl2 3D distinguishes the pair, while sl3 stays the same.",
    "only_sl3_distinguishes": "sl3 distinguishes the pair, while sl2 3D stays the same.",
    "jones_same_sl3_diff": "Jones stays the same, sl2 3D stays the same, and only sl3 differs.",
    "jones_same_sl2_3d_diff": "Jones stays the same, sl3 stays the same, and only sl2 3D differs.",
    "all_same": "All three current branches give the same output on braid A and braid B.",
    "all_different": "All three current branches distinguish braid A from braid B.",
}


def _simplified_equal(left: sp.Expr, right: sp.Expr) -> bool:
    return sp.simplify(left - right) == 0


def _primary_output_for_model(entry: ApplicationBraidResult, model_id: str) -> sp.Expr:
    """Return one application-result output using its public model identity."""

    for result in entry.branch_results:
        if result.model_id == model_id:
            if result.primary_output is None:
                raise ValueError(f"Model '{model_id}' did not provide a primary output.")
            return sp.simplify(sp.sympify(result.primary_output))
    raise ValueError(f"Evaluation result did not include model '{model_id}'.")


def classify_workbench_pair(jones_same: bool, sl2_3d_same: bool, sl3_same: bool) -> str:
    """Classify one pairwise comparison across the three main branches."""

    if jones_same and sl2_3d_same and sl3_same:
        return "all_same"
    if not jones_same and not sl2_3d_same and not sl3_same:
        return "all_different"
    if jones_same and not sl2_3d_same and not sl3_same:
        return "both_distinguish"
    if not jones_same and sl2_3d_same and sl3_same:
        return "neither_distinguishes"
    if jones_same and sl2_3d_same and not sl3_same:
        return "jones_same_sl3_diff"
    if jones_same and not sl2_3d_same and sl3_same:
        return "jones_same_sl2_3d_diff"
    if not sl2_3d_same and sl3_same:
        return "only_sl2_3d_distinguishes"
    return "only_sl3_distinguishes"


@dataclass(frozen=True, slots=True)
class WorkbenchPairComparisonResult:
    """Store one structured pair comparison across the three main branches."""

    label: str
    braid_a: BraidWord
    braid_b: BraidWord
    jones_output_a: sp.Expr
    jones_output_b: sp.Expr
    jones_same: bool
    sl2_3d_output_a: sp.Expr
    sl2_3d_output_b: sp.Expr
    sl2_3d_same: bool
    sl3_output_a: sp.Expr
    sl3_output_b: sp.Expr
    sl3_same: bool
    classification: str
    notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def classification_description(self) -> str:
        return WORKBENCH_CLASSIFICATION_DESCRIPTIONS[self.classification]

    def summary(self) -> str:
        lines = [
            f"Pair label: {self.label}",
            f"Classification: {self.classification}",
            f"Classification note: {self.classification_description}",
            f"Braid A: {self.braid_a.label or self.braid_a.word_string()}",
            f"Braid B: {self.braid_b.label or self.braid_b.word_string()}",
            f"Jones / sl2 fundamental same: {self.jones_same}",
            f"Jones / sl2 fundamental A: {sp.simplify(self.jones_output_a)}",
            f"Jones / sl2 fundamental B: {sp.simplify(self.jones_output_b)}",
            f"sl2 的3维表示下的9x9矩阵 same: {self.sl2_3d_same}",
            f"sl2 的3维表示下的9x9矩阵 A: {sp.simplify(self.sl2_3d_output_a)}",
            f"sl2 的3维表示下的9x9矩阵 B: {sp.simplify(self.sl2_3d_output_b)}",
            f"sl3 fundamental same: {self.sl3_same}",
            f"sl3 fundamental A: {sp.simplify(self.sl3_output_a)}",
            f"sl3 fundamental B: {sp.simplify(self.sl3_output_b)}",
        ]
        if self.notes:
            lines.append(f"Notes: {self.notes}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "braid_a": self.braid_a.to_dict(),
            "braid_b": self.braid_b.to_dict(),
            "jones_output_a": str(sp.simplify(self.jones_output_a)),
            "jones_output_b": str(sp.simplify(self.jones_output_b)),
            "jones_same": self.jones_same,
            "sl2_3d_output_a": str(sp.simplify(self.sl2_3d_output_a)),
            "sl2_3d_output_b": str(sp.simplify(self.sl2_3d_output_b)),
            "sl2_3d_same": self.sl2_3d_same,
            "sl3_output_a": str(sp.simplify(self.sl3_output_a)),
            "sl3_output_b": str(sp.simplify(self.sl3_output_b)),
            "sl3_same": self.sl3_same,
            "classification": self.classification,
            "classification_description": self.classification_description,
            "notes": self.notes,
            "metadata": dict(self.metadata),
        }


def evaluate_workbench_pair(
    braid_a: BraidWord,
    braid_b: BraidWord,
    *,
    label: str = "",
    notes: str = "",
    q: sp.Expr | None = None,
) -> WorkbenchPairComparisonResult:
    """Evaluate one braid pair across Jones, sl2 3D, and sl3 branches."""

    result_a = evaluate_braid_result(braid_a, q=q)
    result_b = evaluate_braid_result(braid_b, q=q)
    jones_a = _primary_output_for_model(result_a, "sl2_fundamental")
    jones_b = _primary_output_for_model(result_b, "sl2_fundamental")
    sl2_3d_a = _primary_output_for_model(result_a, "sl2_3d_9x9")
    sl2_3d_b = _primary_output_for_model(result_b, "sl2_3d_9x9")
    sl3_a = _primary_output_for_model(result_a, "sl3_fundamental")
    sl3_b = _primary_output_for_model(result_b, "sl3_fundamental")

    jones_same = _simplified_equal(jones_a, jones_b)
    sl2_3d_same = _simplified_equal(sl2_3d_a, sl2_3d_b)
    sl3_same = _simplified_equal(sl3_a, sl3_b)
    comparison_label = label or f"{braid_a.label or 'braid_a'}_vs_{braid_b.label or 'braid_b'}"

    return WorkbenchPairComparisonResult(
        label=comparison_label,
        braid_a=braid_a,
        braid_b=braid_b,
        jones_output_a=jones_a,
        jones_output_b=jones_b,
        jones_same=jones_same,
        sl2_3d_output_a=sl2_3d_a,
        sl2_3d_output_b=sl2_3d_b,
        sl2_3d_same=sl2_3d_same,
        sl3_output_a=sl3_a,
        sl3_output_b=sl3_b,
        sl3_same=sl3_same,
        classification=classify_workbench_pair(jones_same, sl2_3d_same, sl3_same),
        notes=notes,
        metadata={
            "q": None if q is None else str(q),
        },
    )
