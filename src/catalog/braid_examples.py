"""Standard braid and closure examples used for benchmarks and regression checks."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.braid.braid_word import BraidWord


@dataclass(frozen=True, slots=True)
class BraidExample:
    """Store one reusable braid benchmark example."""

    label: str
    num_strands: int
    generators: tuple[int, ...]
    notes: str
    expected_components: int | None = None
    expected_crossing_count: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "generators", tuple(self.generators))
        BraidWord(
            num_strands=self.num_strands,
            generators=self.generators,
            label=self.label,
            notes=self.notes,
            metadata=self.metadata,
        )

    def to_braid_word(self) -> BraidWord:
        """Convert this catalog entry to the core BraidWord object."""

        return BraidWord(
            num_strands=self.num_strands,
            generators=self.generators,
            label=self.label,
            notes=self.notes,
            metadata=dict(self.metadata),
        )

    def summary(self) -> str:
        """Return a readable summary for CLI or future GUI use."""

        lines = [
            f"Label: {self.label}",
            f"Number of strands: {self.num_strands}",
            f"Generators: {list(self.generators)}",
            f"Word: {self.to_braid_word().word_string()}",
            f"Notes: {self.notes}",
            "Expected components: unknown"
            if self.expected_components is None
            else f"Expected components: {self.expected_components}",
            "Expected crossing count: unknown"
            if self.expected_crossing_count is None
            else f"Expected crossing count: {self.expected_crossing_count}",
        ]
        if self.metadata:
            lines.append(f"Metadata: {self.metadata}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Return a structured representation suitable for serialization."""

        return {
            "label": self.label,
            "num_strands": self.num_strands,
            "generators": list(self.generators),
            "word": self.to_braid_word().word_string(),
            "notes": self.notes,
            "expected_components": self.expected_components,
            "expected_crossing_count": self.expected_crossing_count,
            "metadata": dict(self.metadata),
        }

    def to_string(self) -> str:
        """Return a string form aligned with the summary output."""

        return self.summary()


STANDARD_BRAID_EXAMPLES: tuple[BraidExample, ...] = (
    BraidExample(
        label="unknot_1",
        num_strands=1,
        generators=(),
        notes="Closure of the 1-strand identity braid. This is the base unknot normalization example.",
        expected_components=1,
        expected_crossing_count=0,
    ),
    BraidExample(
        label="unlink_2",
        num_strands=2,
        generators=(),
        notes="Closure of the 2-strand identity braid, giving the 2-component unlink.",
        expected_components=2,
        expected_crossing_count=0,
    ),
    BraidExample(
        label="unknot_2",
        num_strands=2,
        generators=(1,),
        notes=(
            "Closure of sigma_1 on two strands, i.e. the torus knot T(2, 1). The braid word has one crossing, "
            "but the closed link is isotopic to the unknot."
        ),
        expected_components=1,
        expected_crossing_count=1,
    ),
    BraidExample(
        label="hopf_link",
        num_strands=2,
        generators=(1, 1),
        notes="Closure of sigma_1 squared on two strands. This is the standard positive Hopf link example.",
        expected_components=2,
        expected_crossing_count=2,
    ),
    BraidExample(
        label="trefoil",
        num_strands=2,
        generators=(1, 1, 1),
        notes="Closure of sigma_1 cubed on two strands, i.e. the standard positive trefoil T(2, 3).",
        expected_components=1,
        expected_crossing_count=3,
    ),
    BraidExample(
        label="figure_eight",
        num_strands=3,
        generators=(1, -2, 1, -2),
        notes=(
            "Closure of the 3-braid sigma_1 sigma_2^-1 sigma_1 sigma_2^-1. This is a standard braid-word model "
            "for the figure-eight knot in the Artin-generator convention used throughout this project."
        ),
        expected_components=1,
        expected_crossing_count=4,
        metadata={"source_convention": "3-braid closure sigma_1 sigma_2^-1 sigma_1 sigma_2^-1"},
    ),
    BraidExample(
        label="unlink_3",
        num_strands=3,
        generators=(),
        notes="Closure of the 3-strand identity braid, giving the 3-component unlink.",
        expected_components=3,
        expected_crossing_count=0,
    ),
    BraidExample(
        label="three_strand_trefoil",
        num_strands=3,
        generators=(1, 2, 1, 2),
        notes=(
            "Closure of (sigma_1 sigma_2)^2, i.e. the torus knot T(3, 2). This is another standard trefoil braid "
            "presentation, now on three strands."
        ),
        expected_components=1,
        expected_crossing_count=4,
    ),
)


def get_standard_braid_examples() -> tuple[BraidExample, ...]:
    """Return the full standard benchmark catalog."""

    return STANDARD_BRAID_EXAMPLES


def get_default_benchmark_examples() -> tuple[BraidExample, ...]:
    """Return the default subset used by the benchmark demos."""

    labels = {"unknot_1", "unlink_2", "unknot_2", "hopf_link", "trefoil", "figure_eight", "three_strand_trefoil"}
    return tuple(example for example in STANDARD_BRAID_EXAMPLES if example.label in labels)


def get_braid_example(label: str) -> BraidExample:
    """Return one named braid example from the standard catalog."""

    for example in STANDARD_BRAID_EXAMPLES:
        if example.label == label:
            return example
    raise KeyError(f"Unknown braid example label: {label}")