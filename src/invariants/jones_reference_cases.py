"""Editable Jones-reference scaffolds for the current sl2 debug layer.

These cases are intentionally lightweight and easy to edit. The goal is to
support comparison and debugging, not to freeze one literature convention as
the final project-wide theorem-level target.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.catalog.braid_examples import get_braid_example
from src.braid.braid_word import BraidWord


@dataclass(frozen=True, slots=True)
class JonesReferenceCase:
    """Store one editable Jones-reference slot for a named braid example."""

    label: str
    braid_word: BraidWord
    target_expression: str | None
    variable_name: str
    convention_label: str
    notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def summary(self) -> str:
        lines = [
            f"Label: {self.label}",
            f"Braid word: {self.braid_word.word_string()}",
            "Target expression: missing reference slot"
            if self.target_expression is None
            else f"Target expression: {self.target_expression}",
            f"Variable name: {self.variable_name}",
            f"Convention label: {self.convention_label}",
        ]
        if self.notes:
            lines.append(f"Notes: {self.notes}")
        if self.metadata:
            lines.append(f"Metadata: {self.metadata}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "braid_word": self.braid_word.to_dict(),
            "target_expression": self.target_expression,
            "variable_name": self.variable_name,
            "convention_label": self.convention_label,
            "notes": self.notes,
            "metadata": dict(self.metadata),
        }

    def to_string(self) -> str:
        return self.summary()


JONES_REFERENCE_CASES: tuple[JonesReferenceCase, ...] = (
    JonesReferenceCase(
        label="unknot_1",
        braid_word=get_braid_example("unknot_1").to_braid_word(),
        target_expression="1",
        variable_name="t",
        convention_label="editable normalized Jones reference slot",
        notes=(
            "Reference slot for debugging against a standard normalized Jones convention. "
            "This value is easy to edit if you want to compare against a different literature normalization."
        ),
        metadata={
            "reference_slot": True,
            "status": "seeded",
        },
    ),
    JonesReferenceCase(
        label="trefoil",
        braid_word=get_braid_example("trefoil").to_braid_word(),
        target_expression="t + t**3 - t**4",
        variable_name="t",
        convention_label="editable literature reference slot",
        notes=(
            "This slot currently seeds the trefoil comparison with the target expression t + t**3 - t**4. "
            "It remains intentionally editable so comparison can still be repeated under different literature "
            "normalizations without changing the diagnostic engine."
        ),
        metadata={
            "reference_slot": True,
            "status": "seeded",
        },
    ),
    JonesReferenceCase(
        label="figure_eight",
        braid_word=get_braid_example("figure_eight").to_braid_word(),
        target_expression="t**2 - t + 1 - t**-1 + t**-2",
        variable_name="t",
        convention_label="editable literature reference slot",
        notes=(
            "This slot currently seeds the figure-eight comparison with the target expression "
            "t**2 - t + 1 - t**-1 + t**-2. It remains intentionally editable rather than frozen as a "
            "final theorem-level convention."
        ),
        metadata={
            "reference_slot": True,
            "status": "seeded",
        },
    ),
)


def get_default_jones_reference_cases() -> tuple[JonesReferenceCase, ...]:
    """Return the default Jones-reference scaffold set."""

    return JONES_REFERENCE_CASES


def get_jones_reference_case(label: str) -> JonesReferenceCase:
    """Return one named Jones-reference scaffold."""

    for case in JONES_REFERENCE_CASES:
        if case.label == label:
            return case
    raise KeyError(f"Unknown Jones reference case label: {label}")