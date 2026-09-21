"""Frontend-neutral snapshots of the recovered built-in braid catalog."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.catalog.braid_examples import BraidExample, get_braid_example, get_standard_braid_examples

from .errors import UnknownCatalogExampleError


@dataclass(frozen=True, slots=True)
class ApplicationCatalogExample:
    """Application-facing selection and preview data for one built-in braid."""

    label: str
    num_strands: int
    generators: tuple[int, ...]
    word_string: str
    notes: str
    expected_components: int | None
    expected_crossing_count: int | None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return the selection and preview fields without exposing catalog internals."""

        return {
            "label": self.label,
            "num_strands": self.num_strands,
            "generators": list(self.generators),
            "word_string": self.word_string,
            "notes": self.notes,
            "expected_components": self.expected_components,
            "expected_crossing_count": self.expected_crossing_count,
            "metadata": dict(self.metadata),
        }


def _application_catalog_example_from_internal(example: BraidExample) -> ApplicationCatalogExample:
    return ApplicationCatalogExample(
        label=example.label,
        num_strands=example.num_strands,
        generators=tuple(example.generators),
        word_string=example.to_braid_word().word_string(),
        notes=example.notes,
        expected_components=example.expected_components,
        expected_crossing_count=example.expected_crossing_count,
        metadata=dict(example.metadata),
    )


def list_catalog_examples() -> tuple[ApplicationCatalogExample, ...]:
    """List every recovered built-in example in catalog order for frontend selection."""

    return tuple(_application_catalog_example_from_internal(example) for example in get_standard_braid_examples())


def get_catalog_example(example_label: str) -> ApplicationCatalogExample:
    """Get one built-in example's frontend-facing selection and preview data."""

    try:
        example = get_braid_example(example_label)
    except KeyError as exc:
        raise UnknownCatalogExampleError(f"Unknown catalog example '{example_label}'.") from exc
    return _application_catalog_example_from_internal(example)
