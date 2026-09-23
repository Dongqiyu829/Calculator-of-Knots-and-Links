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
    assert len(long_geometry.segments) == 6


def test_non_crossing_step_boundaries_and_changed_strand_joins_stay_continuous() -> None:
    geometry = build_braid_preview_geometry(BraidWord.from_iterable(5, (1, 4), label="disjoint"))
    assert len(geometry.segments) == 5
    unchanged = next(segment for segment in geometry.segments if segment.strand_identity == 3)
    assert len({point[0] for point in unchanged.points}) == 1
    assert [point[1] for point in unchanged.points] == sorted(point[1] for point in unchanged.points)

    repeated_crossing = build_braid_preview_geometry(BraidWord.from_iterable(2, (1, 1), label="repeat"))
    assert len(repeated_crossing.segments) == 2
    assert all(segment.points[0][1] < segment.points[-1][1] for segment in repeated_crossing.segments)


def test_crossing_masks_are_localized_to_registered_crossings() -> None:
    geometry = build_braid_preview_geometry(BraidWord.from_iterable(3, (1, -2, 1, -2), label="figure_eight"))
    assert len(geometry.crossings) == 4
    for crossing in geometry.crossings:
        mask_start, mask_end = crossing.under_mask_points
        midpoint = ((mask_start[0] + mask_end[0]) / 2.0, (mask_start[1] + mask_end[1]) / 2.0)
        assert midpoint == (crossing.x, crossing.y)
        assert crossing.over_redraw_points[1] == (crossing.x, crossing.y)
        assert mask_start != mask_end


def test_svg_export_is_deterministic_and_contains_semantic_metadata() -> None:
    geometry = build_braid_preview_geometry(BraidWord.from_iterable(3, (1, -2, 1, -2), label="figure_eight"))
    svg = render_braid_preview_svg(geometry)
    assert svg == render_braid_preview_svg(geometry)
    assert "figure_eight" in svg
    assert "generators: 1 -2 1 -2" in svg
    assert "final permutation" in svg
    assert svg.count('stroke="#fbfcfe" stroke-width="11"') == len(geometry.crossings)
    assert svg.count('stroke-width="5"') == len(geometry.segments) + len(geometry.crossings)
