"""Application boundary for parsing and evaluating braid inputs.

This module deliberately owns no presentation state and imports no GUI package.
It preserves the recovered GUI-facing metadata so Tkinter and workbench callers
can share one evaluation path without changing mathematical behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import sympy as sp

from src.braid.braid_word import BraidWord
from src.catalog.braid_examples import get_braid_example
from src.invariants.branch_registry import evaluate_current_branches
from src.invariants.multibranch_benchmark import MultiBranchBenchmarkEntry

from .branch_catalog import validate_branch_ids
from .errors import BraidInputValidationError, GeneratorParseError, UnknownCatalogExampleError
from .results import ApplicationBraidResult, application_braid_result_from_internal


@dataclass(frozen=True, slots=True)
class BraidInputState:
    """Source metadata and a validated braid word for one application request."""

    source_mode: str
    source_label: str
    braid_word: BraidWord
    notes: str = ""
    expected_components: int | None = None
    expected_crossing_count: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


def parse_generator_text(generator_text: str) -> tuple[int, ...]:
    """Parse a space- or comma-separated sequence of signed Artin generators."""

    if not isinstance(generator_text, str):
        raise GeneratorParseError("Generators must be supplied as text containing integers such as 1 1 -2.")
    cleaned = generator_text.replace(",", " ").strip()
    if not cleaned:
        return ()
    tokens = [token for token in cleaned.split() if token]
    try:
        return tuple(int(token) for token in tokens)
    except ValueError as exc:
        raise GeneratorParseError("Generators must be integers such as 1 1 -2.") from exc


def build_custom_braid_word(
    num_strands: int,
    generator_text: str,
    *,
    label: str = "custom_braid",
    notes: str = "Custom braid created from the GUI input panel.",
) -> BraidWord:
    """Build the recovered validated custom-braid input without evaluating it."""

    try:
        return BraidWord.from_iterable(
            num_strands=num_strands,
            generators=parse_generator_text(generator_text),
            label=label,
            notes=notes,
            metadata={"input_mode": "custom_gui"},
        )
    except GeneratorParseError:
        raise
    except ValueError as exc:
        raise BraidInputValidationError(str(exc)) from exc


def evaluate_catalog_example(
    example_label: str,
    *,
    branch_ids: tuple[str, ...] | list[str] | None = None,
    q: sp.Expr | None = None,
) -> MultiBranchBenchmarkEntry:
    """Evaluate one catalog example through the selected existing branches."""

    try:
        example = get_braid_example(example_label)
    except KeyError as exc:
        raise UnknownCatalogExampleError(f"Unknown catalog example '{example_label}'.") from exc
    selected_branch_ids = validate_branch_ids(branch_ids)
    return MultiBranchBenchmarkEntry(
        example_label=example.label,
        branch_results=tuple(evaluate_current_branches(example, branch_ids=selected_branch_ids, q=q)),
        notes=example.notes,
        metadata={
            "input_mode": "catalog",
            "braid_word": example.to_braid_word().to_dict(),
            "expected_components": example.expected_components,
            "expected_crossing_count": example.expected_crossing_count,
            "example_metadata": dict(example.metadata),
            "selected_branch_ids": list(selected_branch_ids) if selected_branch_ids is not None else None,
        },
    )


def evaluate_catalog_result(
    example_label: str, *, branch_ids: tuple[str, ...] | list[str] | None = None, q: sp.Expr | None = None
) -> ApplicationBraidResult:
    """Evaluate a catalog example and expose only the application DTO."""

    return application_braid_result_from_internal(evaluate_catalog_example(example_label, branch_ids=branch_ids, q=q))


def evaluate_braid_word(
    braid_word: BraidWord,
    *,
    branch_ids: tuple[str, ...] | list[str] | None = None,
    q: sp.Expr | None = None,
) -> MultiBranchBenchmarkEntry:
    """Evaluate one arbitrary validated braid word through selected branches."""

    selected_branch_ids = validate_branch_ids(branch_ids)
    return MultiBranchBenchmarkEntry(
        example_label=braid_word.label or "custom_braid",
        branch_results=tuple(evaluate_current_branches(braid_word, branch_ids=selected_branch_ids, q=q)),
        notes=braid_word.notes,
        metadata={
            "input_mode": "custom",
            "braid_word": braid_word.to_dict(),
            "selected_branch_ids": list(selected_branch_ids) if selected_branch_ids is not None else None,
        },
    )


def evaluate_braid_result(
    braid_word: BraidWord, *, branch_ids: tuple[str, ...] | list[str] | None = None, q: sp.Expr | None = None
) -> ApplicationBraidResult:
    """Evaluate an arbitrary braid word and expose only the application DTO."""

    return application_braid_result_from_internal(evaluate_braid_word(braid_word, branch_ids=branch_ids, q=q))


def evaluate_custom_braid(
    num_strands: int,
    generator_text: str,
    *,
    branch_ids: tuple[str, ...] | list[str] | None = None,
    q: sp.Expr | None = None,
) -> MultiBranchBenchmarkEntry:
    """Build then evaluate a custom braid using the recovered input semantics."""

    return evaluate_braid_word(build_custom_braid_word(num_strands, generator_text), branch_ids=branch_ids, q=q)


def evaluate_custom_result(
    num_strands: int, generator_text: str, *, branch_ids: tuple[str, ...] | list[str] | None = None, q: sp.Expr | None = None
) -> ApplicationBraidResult:
    """Build/evaluate custom input and expose only the application DTO."""

    return application_braid_result_from_internal(evaluate_custom_braid(num_strands, generator_text, branch_ids=branch_ids, q=q))


def build_catalog_braid_input(example_label: str) -> BraidInputState:
    """Return reusable source metadata for one catalog braid input."""

    try:
        example = get_braid_example(example_label)
    except KeyError as exc:
        raise UnknownCatalogExampleError(f"Unknown catalog example '{example_label}'.") from exc
    return BraidInputState(
        source_mode="catalog",
        source_label=example.label,
        braid_word=example.to_braid_word(),
        notes=example.notes,
        expected_components=example.expected_components,
        expected_crossing_count=example.expected_crossing_count,
        metadata={"example_metadata": dict(example.metadata)},
    )


def build_custom_braid_input(num_strands: int, generator_text: str) -> BraidInputState:
    """Return reusable source metadata for one custom braid input."""

    braid_word = build_custom_braid_word(num_strands, generator_text)
    return BraidInputState(
        source_mode="custom",
        source_label=braid_word.label or "custom_braid",
        braid_word=braid_word,
        notes=braid_word.notes,
        metadata={"braid_word": braid_word.to_dict()},
    )


def evaluate_braid_input(
    braid_input: BraidInputState,
    *,
    branch_ids: tuple[str, ...] | list[str] | None = None,
    q: sp.Expr | None = None,
) -> MultiBranchBenchmarkEntry:
    """Evaluate a catalog or custom input through the same shared path."""

    if braid_input.source_mode == "catalog":
        return evaluate_catalog_example(braid_input.source_label, branch_ids=branch_ids, q=q)
    if braid_input.source_mode == "custom":
        return evaluate_braid_word(braid_input.braid_word, branch_ids=branch_ids, q=q)
    raise BraidInputValidationError(f"Unknown braid input source mode: {braid_input.source_mode}")


def evaluate_braid_input_result(
    braid_input: BraidInputState, *, branch_ids: tuple[str, ...] | list[str] | None = None, q: sp.Expr | None = None
) -> ApplicationBraidResult:
    """Evaluate an input state and expose only the application DTO."""

    return application_braid_result_from_internal(evaluate_braid_input(braid_input, branch_ids=branch_ids, q=q))


def braid_word_from_entry(entry: MultiBranchBenchmarkEntry) -> BraidWord:
    """Recover the evaluated braid word, including empty branch-selection cases."""

    if entry.branch_results:
        return entry.branch_results[0].braid_word
    braid_word_data = entry.metadata.get("braid_word")
    if not isinstance(braid_word_data, dict):
        raise BraidInputValidationError("Evaluation entry is missing braid-word metadata.")
    return BraidWord.from_iterable(
        num_strands=int(braid_word_data["num_strands"]),
        generators=tuple(int(generator) for generator in braid_word_data.get("generators", [])),
        label=str(braid_word_data.get("label") or entry.example_label),
        notes=str(braid_word_data.get("notes") or entry.notes),
        metadata=dict(braid_word_data.get("metadata") or {}),
    )


def braid_input_from_entry(entry: MultiBranchBenchmarkEntry) -> BraidInputState:
    """Recover source metadata for rendering or subsequent service evaluation."""

    return BraidInputState(
        source_mode=str(entry.metadata.get("input_mode", "catalog")),
        source_label=entry.example_label,
        braid_word=braid_word_from_entry(entry),
        notes=entry.notes,
        expected_components=entry.metadata.get("expected_components"),
        expected_crossing_count=entry.metadata.get("expected_crossing_count"),
        metadata={
            "example_metadata": dict(entry.metadata.get("example_metadata") or {}),
            "selected_branch_ids": entry.metadata.get("selected_branch_ids"),
        },
    )


def filter_legacy_entry_by_branch_ids(
    entry: MultiBranchBenchmarkEntry, branch_ids: tuple[str, ...] | list[str]
) -> MultiBranchBenchmarkEntry:
    """Compatibility adapter for legacy GUI callers that still hold internal entries."""

    selected = set(branch_ids)
    return MultiBranchBenchmarkEntry(
        example_label=entry.example_label,
        branch_results=tuple(result for result in entry.branch_results if result.branch_id in selected),
        notes=entry.notes,
        metadata=dict(entry.metadata),
    )
