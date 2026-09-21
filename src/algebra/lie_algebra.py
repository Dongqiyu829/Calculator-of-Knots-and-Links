"""Minimal Lie algebra specifications used by the first MVP stage.

This module intentionally stays small. It only models the data that later
representation and R-matrix builders need for the confirmed MVP scope.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LieAlgebraSpec:
    """Describe a simple Lie algebra family at the level needed by this project.

    Parameters
    ----------
    family:
        Cartan family identifier, for example "A".
    rank:
        Rank of the Lie algebra. For type A this means A_rank, so A1 gives sl2
        and A2 gives sl3.

    Notes
    -----
    The current MVP only requires type A. The validation logic is written so
    unsupported families fail loudly instead of creating ambiguous objects.
    """

    family: str
    rank: int

    def __post_init__(self) -> None:
        normalized_family = self.family.strip().upper()
        object.__setattr__(self, "family", normalized_family)

        if not normalized_family:
            raise ValueError("family must be a non-empty Cartan type label")
        if self.rank < 1:
            raise ValueError("rank must be a positive integer")

    def name(self) -> str:
        """Return the conventional algebra name used by the project.

        Returns
        -------
        str
            For type A, returns the corresponding sl_n name. For example A1 is
            returned as "sl2" and A2 as "sl3".

        Raises
        ------
        NotImplementedError
            If the family is not yet supported by the MVP.
        """

        if self.family == "A":
            return f"sl{self.rank + 1}"

        raise NotImplementedError(
            f"Lie algebra family {self.family!r} is not supported in the MVP"
        )

    def dynkin_label(self) -> str:
        """Return the Dynkin-style label, for example A1 or A2."""

        return f"{self.family}{self.rank}"

    def summary(self) -> str:
        """Return a human-readable summary of the algebra specification."""

        return (
            f"Lie algebra: {self.name()} ({self.dynkin_label()})\n"
            f"Family: {self.family}\n"
            f"Rank: {self.rank}"
        )

    def to_dict(self) -> dict[str, str | int]:
        """Return a structured representation suitable for CLI or GUI display."""

        return {
            "family": self.family,
            "rank": self.rank,
            "name": self.name(),
            "dynkin_label": self.dynkin_label(),
        }

    def to_string(self) -> str:
        """Return a string form aligned with the summary output."""

        return self.summary()


def sl2_algebra() -> LieAlgebraSpec:
    """Construct the type A1 algebra specification used for sl2."""

    return LieAlgebraSpec(family="A", rank=1)


def sl3_algebra() -> LieAlgebraSpec:
    """Construct the type A2 algebra specification used for sl3."""

    return LieAlgebraSpec(family="A", rank=2)
