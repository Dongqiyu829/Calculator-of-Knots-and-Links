"""Structured braid-word input objects for the MVP core layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class BraidWord:
    """Represent a braid word on a fixed number of strands.

    Parameters
    ----------
    num_strands:
        Number of strands in the braid.
    generators:
        Sequence of Artin generators. For example 1 means sigma_1 and -2 means
        sigma_2^{-1}.
    label:
        Optional short label for examples or built-in braid families.
    notes:
        Free-form comments that can later be surfaced in CLI or GUI reports.
    """

    num_strands: int
    generators: tuple[int, ...]
    label: str = ""
    notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        normalized_generators = tuple(self.generators)
        object.__setattr__(self, "generators", normalized_generators)
        self.validate()

    def validate(self) -> None:
        """Validate that the braid word is well-formed for the given strand count."""

        if self.num_strands < 1:
            raise ValueError("A braid word requires at least 1 strand")

        if self.num_strands == 1 and self.generators:
            raise ValueError("A 1-strand braid can only be the identity braid with no generators")

        max_generator = self.num_strands - 1
        for generator in self.generators:
            if generator == 0:
                raise ValueError("Generator 0 is not valid in Artin braid notation")
            if abs(generator) > max_generator:
                raise ValueError(
                    f"Generator sigma_{abs(generator)} is invalid for a braid on {self.num_strands} strands"
                )

    def writhe(self) -> int:
        """Return the writhe, i.e. the signed sum of generators."""

        return sum(1 if generator > 0 else -1 for generator in self.generators)

    def word_string(self) -> str:
        """Return a readable braid-word string such as sigma_1 sigma_1 sigma_2^-1."""

        if not self.generators:
            return "identity"

        parts: list[str] = []
        for generator in self.generators:
            index = abs(generator)
            suffix = "" if generator > 0 else "^-1"
            parts.append(f"sigma_{index}{suffix}")
        return " ".join(parts)

    def summary(self) -> str:
        """Return a human-readable multiline summary of the braid word."""

        lines = [
            f"Braid label: {self.label or 'unnamed'}",
            f"Number of strands: {self.num_strands}",
            f"Generators: {list(self.generators)}",
            f"Word: {self.word_string()}",
            f"Writhe: {self.writhe()}",
        ]
        if self.notes:
            lines.append(f"Notes: {self.notes}")
        if self.metadata:
            lines.append(f"Metadata: {self.metadata}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Return a structured representation suitable for serialization."""

        return {
            "label": self.label,
            "num_strands": self.num_strands,
            "generators": list(self.generators),
            "is_identity": len(self.generators) == 0,
            "word": self.word_string(),
            "writhe": self.writhe(),
            "notes": self.notes,
            "metadata": dict(self.metadata),
        }

    def to_string(self) -> str:
        """Return a string form aligned with the summary output."""

        return self.summary()

    @classmethod
    def from_iterable(
        cls,
        num_strands: int,
        generators: list[int] | tuple[int, ...],
        *,
        label: str = "",
        notes: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> "BraidWord":
        """Construct a braid word from an iterable of integer generators."""

        return cls(
            num_strands=num_strands,
            generators=tuple(generators),
            label=label,
            notes=notes,
            metadata={} if metadata is None else dict(metadata),
        )
