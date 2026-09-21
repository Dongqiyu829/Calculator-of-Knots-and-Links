"""Smoke tests for the standalone braid preview renderer."""

from __future__ import annotations

import tempfile
import unittest
from math import hypot

from src.braid.braid_word import BraidWord
from src.gui.braid_preview_renderer import (
    PRESENTATION_PREVIEW_STYLE,
    build_braid_preview_geometry,
    compute_braid_permutation,
    render_braid_preview_svg,
    save_braid_preview_svg,
)


class TestBraidPreviewRendererSmoke(unittest.TestCase):
    def test_identity_braid_is_rendered_with_identity_label(self) -> None:
        braid_word = BraidWord.from_iterable(1, (), label="unknot_1")
        geometry = build_braid_preview_geometry(braid_word, viewport_width=520, viewport_height=220)
        self.assertTrue(any(text.role == "identity_label" for text in geometry.texts))

    def test_preview_geometry_keeps_endpoint_count(self) -> None:
        braid_word = BraidWord.from_iterable(3, (1, 2, 1), label="121")
        geometry = build_braid_preview_geometry(braid_word, viewport_width=520, viewport_height=220)
        top_endpoints = [oval for oval in geometry.ovals if oval.role == "top_endpoint"]
        bottom_endpoints = [oval for oval in geometry.ovals if oval.role == "bottom_endpoint"]
        self.assertEqual(len(top_endpoints), 3)
        self.assertEqual(len(bottom_endpoints), 3)

    def test_preview_geometry_draws_under_and_over_segments(self) -> None:
        braid_word = BraidWord.from_iterable(3, (1, -2, 1, -2), label="figure_eight_word")
        geometry = build_braid_preview_geometry(braid_word, viewport_width=520, viewport_height=220)
        under_segments = [line for line in geometry.lines if line.role == "under_strand"]
        over_segments = [line for line in geometry.lines if line.role == "over_strand"]
        self.assertEqual(len(over_segments), len(braid_word.generators))
        self.assertEqual(len(under_segments), 2 * len(braid_word.generators))

    def test_braid_relation_examples_share_the_same_final_permutation(self) -> None:
        left = BraidWord.from_iterable(3, (1, 2, 1), label="121")
        right = BraidWord.from_iterable(3, (2, 1, 2), label="212")
        left_geometry = build_braid_preview_geometry(left, viewport_width=520, viewport_height=220)
        right_geometry = build_braid_preview_geometry(right, viewport_width=520, viewport_height=220)

        self.assertEqual(compute_braid_permutation(left), (3, 2, 1))
        self.assertEqual(left_geometry.final_permutation, right_geometry.final_permutation)
        self.assertEqual(left_geometry.final_permutation, (3, 2, 1))

    def test_inverse_pair_returns_to_identity_permutation(self) -> None:
        braid_word = BraidWord.from_iterable(2, (1, -1), label="cancel")
        geometry = build_braid_preview_geometry(braid_word, viewport_width=520, viewport_height=220)
        self.assertEqual(geometry.final_permutation, (1, 2))

    def test_under_strand_keeps_a_visible_gap_at_each_crossing(self) -> None:
        braid_word = BraidWord.from_iterable(2, (1,), label="single_crossing")
        geometry = build_braid_preview_geometry(braid_word, viewport_width=520, viewport_height=220)
        under_segments = [line for line in geometry.lines if line.role == "under_strand"]
        self.assertEqual(len(under_segments), 2)
        gap_size = hypot(under_segments[1].x1 - under_segments[0].x2, under_segments[1].y1 - under_segments[0].y2)
        self.assertGreater(gap_size, 5.0)

    def test_generator_labels_share_one_column(self) -> None:
        braid_word = BraidWord.from_iterable(2, (1, 1, 1), label="trefoil")
        geometry = build_braid_preview_geometry(braid_word, viewport_width=520, viewport_height=220)
        label_positions = {text.x for text in geometry.texts if text.role == "generator_label"}
        self.assertEqual(len(label_positions), 1)

    def test_long_braid_gets_enough_width_for_label_gutter(self) -> None:
        braid_word = BraidWord.from_iterable(6, (1, -2, 3, -4, 5, 1, -2, 3, -4, 5, 1, -2), label="long_word")
        geometry = build_braid_preview_geometry(braid_word, viewport_width=520, viewport_height=220)
        generator_labels = [text for text in geometry.texts if text.role == "generator_label"]
        self.assertTrue(generator_labels)
        self.assertTrue(all(label.x < geometry.width for label in generator_labels))

    def test_presentation_style_renders_long_multistrand_braid(self) -> None:
        braid_word = BraidWord.from_iterable(5, (1, -2, 3, -4, 2, 1, -3, 4, -2, 3, -4, 1), label="presentation_long")
        geometry = build_braid_preview_geometry(
            braid_word,
            viewport_width=640,
            viewport_height=280,
            style=PRESENTATION_PREVIEW_STYLE,
        )
        self.assertGreaterEqual(geometry.width, 640)
        self.assertGreaterEqual(geometry.height, 280)
        self.assertTrue(any(rect.role == "header_panel" for rect in geometry.rectangles))

    def test_svg_export_produces_svg_text_and_file(self) -> None:
        braid_word = BraidWord.from_iterable(3, (1, -2, 1, -2), label="figure_eight_word")
        svg_text = render_braid_preview_svg(braid_word, viewport_width=520, viewport_height=220)
        self.assertIn("<svg", svg_text)
        self.assertIn("figure_eight_word", svg_text)

        with tempfile.TemporaryDirectory() as temp_dir:
            target_path = save_braid_preview_svg(
                f"{temp_dir}/preview.svg",
                braid_word,
                viewport_width=520,
                viewport_height=220,
            )
            self.assertTrue(target_path.exists())