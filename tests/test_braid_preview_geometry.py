"""Deterministic semantic tests for the maintained braid preview geometry."""

from __future__ import annotations

from src.braid.braid_word import BraidWord
from src.services.braid_preview import (
    build_braid_preview_geometry,
    compute_braid_permutation,
    render_braid_preview_svg,
)


def test_positive_and_negative_crossings_follow_project_artin_over_strand() -> None:
    positive = build_braid_preview_geometry(BraidWord.from_iterable(2, (1,), label="positive"))
    negative = build_braid_preview_geometry(BraidWord.from_iterable(2, (-1,), label="negative"))

    assert positive.crossings[0].generator == 1
    assert positive.crossings[0].over_strand == 1
    assert positive.crossings[0].under_strand == 2
    assert negative.crossings[0].generator == -1
    assert negative.crossings[0].over_strand == 2
    assert negative.crossings[0].under_strand == 1


def test_generator_order_and_permutation_are_preserved() -> None:
    word = BraidWord.from_iterable(3, (1, -2, 1), label="mixed")
    geometry = build_braid_preview_geometry(word)
    assert tuple(c.generator for c in geometry.crossings) == (1, -2, 1)
    assert geometry.final_permutation == (3, 2, 1)
    assert compute_braid_permutation(word) == geometry.final_permutation
    assert geometry.writhe == 1


def test_identity_and_long_words_have_stable_geometry_and_metadata() -> None:
    identity = build_braid_preview_geometry(BraidWord.from_iterable(1, (), label="identity"), viewport_width=300, viewport_height=180)
    assert identity.is_identity
    assert identity.final_permutation == (1,)
    assert len(identity.segments) == 1
    assert "identity" in identity.metadata_text

    long_word = BraidWord.from_iterable(6, (1, -2, 3, -4, 5) * 12, label="long")
    long_geometry = build_braid_preview_geometry(long_word, viewport_width=300, viewport_height=180)
    assert long_geometry.height >= 180
    assert len(long_geometry.crossings) == 60
    assert len(long_geometry.segments) >= 3 * len(long_word.generators)


def test_svg_export_is_deterministic_and_contains_semantic_metadata() -> None:
    geometry = build_braid_preview_geometry(BraidWord.from_iterable(3, (1, -2, 1, -2), label="figure_eight"))
    svg = render_braid_preview_svg(geometry)
    assert svg == render_braid_preview_svg(geometry)
    assert "figure_eight" in svg
    assert "generators: 1 -2 1 -2" in svg
    assert "final permutation" in svg
