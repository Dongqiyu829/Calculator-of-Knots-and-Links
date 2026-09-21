"""Compare the discriminating behavior of the two current 9x9 invariant branches."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

import sympy as sp

from src.braid.braid_word import BraidWord
from src.catalog.braid_examples import BraidExample, get_braid_example

from .branch_registry import evaluate_sl2_spin1_branch, evaluate_sl3_fundamental_branch


SL2_3D_CHANNEL_EXPLANATION = "sl2 的3维表示下的9x9矩阵 uses 3 tensor 3 = 5 plus 3 plus 1, so the local 9x9 braiding data split into three channels."
SL3_FUNDAMENTAL_9X9_CHANNEL_EXPLANATION = "sl3 fundamental uses 3 tensor 3 = 6 plus 3bar, so the local 9x9 braiding data split into two channels."
NINE_BY_NINE_COMPARISON_CONCLUSION = (
    "The two 9x9 branches have different channel structures and different local spectral data. "
    "Their actual discriminating power should be read from the benchmark results rather than inferred from channel count alone."
)


@dataclass(frozen=True, slots=True)
class NineByNineComparisonPair:
    """Store one reproducible braid pair for 9x9 branch comparison."""

    label: str
    left: BraidWord
    right: BraidWord
    notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def summary(self) -> str:
        lines = [
            f"Pair label: {self.label}",
            f"Left braid: {self.left.label or self.left.word_string()}",
            f"Right braid: {self.right.label or self.right.word_string()}",
        ]
        if self.notes:
            lines.append(f"Notes: {self.notes}")
        if self.metadata:
            lines.append(f"Metadata: {self.metadata}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "left": self.left.to_dict(),
            "right": self.right.to_dict(),
            "notes": self.notes,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class NineByNinePairComparisonResult:
    """Store one pairwise comparison between the sl2 3D candidate and sl3 9x9 branches."""

    pair: NineByNineComparisonPair
    sl2_3d_left_output: sp.Expr
    sl2_3d_right_output: sp.Expr
    sl3_left_output: sp.Expr
    sl3_right_output: sp.Expr
    classification: str

    @property
    def sl2_3d_distinguishes(self) -> bool:
        return sp.simplify(self.sl2_3d_left_output - self.sl2_3d_right_output) != 0

    @property
    def sl3_distinguishes(self) -> bool:
        return sp.simplify(self.sl3_left_output - self.sl3_right_output) != 0

    def summary(self) -> str:
        lines = [
            f"Pair label: {self.pair.label}",
            f"Classification: {self.classification}",
            f"sl2 3D left: {sp.simplify(self.sl2_3d_left_output)}",
            f"sl2 3D right: {sp.simplify(self.sl2_3d_right_output)}",
            f"sl3 left: {sp.simplify(self.sl3_left_output)}",
            f"sl3 right: {sp.simplify(self.sl3_right_output)}",
        ]
        if self.pair.notes:
            lines.append(f"Notes: {self.pair.notes}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        return {
            "pair": self.pair.to_dict(),
            "sl2_3d_left_output": str(sp.simplify(self.sl2_3d_left_output)),
            "sl2_3d_right_output": str(sp.simplify(self.sl2_3d_right_output)),
            "sl3_left_output": str(sp.simplify(self.sl3_left_output)),
            "sl3_right_output": str(sp.simplify(self.sl3_right_output)),
            "sl2_3d_distinguishes": self.sl2_3d_distinguishes,
            "sl3_distinguishes": self.sl3_distinguishes,
            "classification": self.classification,
        }


@dataclass(frozen=True, slots=True)
class NineByNineComparisonSummary:
    """Store a structured summary for a 9x9-vs-9x9 discriminating-power benchmark."""

    pair_results: tuple[NineByNinePairComparisonResult, ...]
    notes: str = ""

    def classification_counts(self) -> dict[str, int]:
        counts = {
            "both_distinguish": 0,
            "neither_distinguishes": 0,
            "only_sl2_3d_distinguishes": 0,
            "only_sl3_distinguishes": 0,
        }
        for result in self.pair_results:
            counts[result.classification] += 1
        return counts

    def representative_examples(self) -> dict[str, list[str]]:
        buckets = {
            "both_distinguish": [],
            "neither_distinguishes": [],
            "only_sl2_3d_distinguishes": [],
            "only_sl3_distinguishes": [],
        }
        for result in self.pair_results:
            buckets[result.classification].append(result.pair.label)
        return buckets

    def summary(self) -> str:
        counts = self.classification_counts()
        reps = self.representative_examples()
        lines = [
            "=== 9x9 discriminating-power benchmark ===",
            f"Tested pair count: {len(self.pair_results)}",
            f"both distinguish: {counts['both_distinguish']}",
            f"neither distinguishes: {counts['neither_distinguishes']}",
            f"only sl2 3D distinguishes: {counts['only_sl2_3d_distinguishes']}",
            f"only sl3 distinguishes: {counts['only_sl3_distinguishes']}",
            "",
            "Channel-level explanation:",
            f"- {SL2_3D_CHANNEL_EXPLANATION}",
            f"- {SL3_FUNDAMENTAL_9X9_CHANNEL_EXPLANATION}",
            f"- {NINE_BY_NINE_COMPARISON_CONCLUSION}",
            "",
            "Representative examples:",
            f"- both distinguish: {reps['both_distinguish'] or ['none']}",
            f"- neither distinguishes: {reps['neither_distinguishes'] or ['none']}",
            f"- only sl2 3D distinguishes: {reps['only_sl2_3d_distinguishes'] or ['none']}",
            f"- only sl3 distinguishes: {reps['only_sl3_distinguishes'] or ['none']}",
        ]
        if not reps["neither_distinguishes"]:
            lines.append("- Current default pair set does not yet exhibit a neither-distinguishes case.")
        if not reps["only_sl3_distinguishes"]:
            lines.append("- Current default pair set does not yet exhibit an only-sl3-distinguishes case.")
        if self.notes:
            lines.extend(["", f"Notes: {self.notes}"])
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        return {
            "pair_results": [result.to_dict() for result in self.pair_results],
            "tested_pair_count": len(self.pair_results),
            "classification_counts": self.classification_counts(),
            "representative_examples": self.representative_examples(),
            "channel_explanation": {
                "sl2_3d": SL2_3D_CHANNEL_EXPLANATION,
                "sl3_fundamental": SL3_FUNDAMENTAL_9X9_CHANNEL_EXPLANATION,
                "conclusion": NINE_BY_NINE_COMPARISON_CONCLUSION,
            },
            "notes": self.notes,
        }


def _make_pair(label: str, left: BraidExample | BraidWord, right: BraidExample | BraidWord, *, notes: str = "") -> NineByNineComparisonPair:
    left_braid = left.to_braid_word() if isinstance(left, BraidExample) else left
    right_braid = right.to_braid_word() if isinstance(right, BraidExample) else right
    return NineByNineComparisonPair(
        label=label,
        left=left_braid,
        right=right_braid,
        notes=notes,
        metadata={
            "left_label": left_braid.label,
            "right_label": right_braid.label,
        },
    )


DEFAULT_9X9_COMPARISON_PAIRS: tuple[NineByNineComparisonPair, ...] = (
    _make_pair(
        "unknot_presentation_pair",
        get_braid_example("unknot_1"),
        get_braid_example("unknot_2"),
        notes="Compares two braid presentations of the unknot to expose how sensitive each current 9x9 branch is to this pair.",
    ),
    _make_pair(
        "unlink_vs_unknot",
        get_braid_example("unknot_1"),
        get_braid_example("unlink_2"),
        notes="A baseline pair that both current 9x9 branches separate in the present implementation.",
    ),
    _make_pair(
        "hopf_vs_unlink",
        get_braid_example("hopf_link"),
        get_braid_example("unlink_2"),
        notes="Another reproducible pair on which both current 9x9 branches separate the two closures.",
    ),
    _make_pair(
        "trefoil_presentation_pair",
        get_braid_example("trefoil"),
        get_braid_example("three_strand_trefoil"),
        notes="Compares two standard trefoil braid presentations across the two current 9x9 branches.",
    ),
    _make_pair(
        "trefoil_vs_figure_eight",
        get_braid_example("trefoil"),
        get_braid_example("figure_eight"),
        notes="A baseline pair that both current 9x9 branches separate in the present implementation.",
    ),
    _make_pair(
        "10_22_vs_10_35",
        BraidWord.from_iterable(4, (1, -3, -3, 2, 2, 2, -3, 2, 1, -2, -3), label="10_22"),
        BraidWord.from_iterable(6, (1, -2, -3, 2, 4, -3, -5, 4, -5, 1, -2), label="10_35"),
        notes="External-reference pair used to compare current 9x9 branch behavior on a harder custom input.",
    ),
)


def classify_9x9_pair(sl2_3d_distinguishes: bool, sl3_distinguishes: bool) -> str:
    if sl2_3d_distinguishes and sl3_distinguishes:
        return "both_distinguish"
    if not sl2_3d_distinguishes and not sl3_distinguishes:
        return "neither_distinguishes"
    if sl2_3d_distinguishes:
        return "only_sl2_3d_distinguishes"
    return "only_sl3_distinguishes"


def evaluate_9x9_pair(
    pair: NineByNineComparisonPair,
    *,
    q: sp.Expr | None = None,
) -> NineByNinePairComparisonResult:
    """Evaluate one braid pair through the current sl2 3D candidate and sl3 9x9 branches."""

    left_sl2 = evaluate_sl2_spin1_branch(pair.left, q=q)
    right_sl2 = evaluate_sl2_spin1_branch(pair.right, q=q)
    left_sl3 = evaluate_sl3_fundamental_branch(pair.left, q=q)
    right_sl3 = evaluate_sl3_fundamental_branch(pair.right, q=q)
    left_sl2_output = sp.simplify(left_sl2.primary_output)
    right_sl2_output = sp.simplify(right_sl2.primary_output)
    left_sl3_output = sp.simplify(left_sl3.primary_output)
    right_sl3_output = sp.simplify(right_sl3.primary_output)
    classification = classify_9x9_pair(
        sp.simplify(left_sl2_output - right_sl2_output) != 0,
        sp.simplify(left_sl3_output - right_sl3_output) != 0,
    )
    return NineByNinePairComparisonResult(
        pair=pair,
        sl2_3d_left_output=left_sl2_output,
        sl2_3d_right_output=right_sl2_output,
        sl3_left_output=left_sl3_output,
        sl3_right_output=right_sl3_output,
        classification=classification,
    )


def evaluate_9x9_pairs(
    pairs: Iterable[NineByNineComparisonPair],
    *,
    q: sp.Expr | None = None,
) -> NineByNineComparisonSummary:
    """Evaluate a reproducible family of braid pairs through the current two 9x9 branches."""

    pair_results = tuple(evaluate_9x9_pair(pair, q=q) for pair in pairs)
    return NineByNineComparisonSummary(
        pair_results=pair_results,
        notes=(
            "This summary compares the current sl2 3D candidate branch against the formal sl3 fundamental 9x9 branch. "
            "It is a branch-level discriminating-power report, not a theorem claiming one branch is uniformly stronger."
        ),
    )


def evaluate_default_9x9_discriminating_power(
    *,
    q: sp.Expr | None = None,
) -> NineByNineComparisonSummary:
    """Run the default reproducible 9x9-vs-9x9 benchmark family."""

    return evaluate_9x9_pairs(DEFAULT_9X9_COMPARISON_PAIRS, q=q)