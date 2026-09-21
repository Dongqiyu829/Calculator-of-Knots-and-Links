"""Canvas renderer for the braid preview used by the Tkinter GUI."""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
from math import hypot
from pathlib import Path

import tkinter as tk

from src.braid.braid_word import BraidWord


LEFT_MARGIN = 112
TOP_MARGIN = 118
BOTTOM_MARGIN = 52
HEADER_HEIGHT = 74
STEP_INDEX_X = 44
MIN_RIGHT_GUTTER = 208
STRAND_SPACING = 94
STEP_HEIGHT = 76
MIN_STEP_HEIGHT = 54
MAX_STEP_HEIGHT = 88
HEADER_CARD_MARGIN = 16
IDENTITY_LABEL_GAP = 28
CURVE_SAMPLES = 24
VERTICAL_CURVE_PULL = 0.26
CROSSING_CURVE_PULL = 0.34
CROSSING_GAP_SIZE = 18.0

STANDARD_PREVIEW_STYLE = "standard"
PRESENTATION_PREVIEW_STYLE = "presentation"

_PREVIEW_STYLES = {
    STANDARD_PREVIEW_STYLE: {
        "canvas_fill": "#f8fafc",
        "header_fill": "#ffffff",
        "header_outline": "#d8e0ec",
        "title_fill": "#0f172a",
        "summary_fill": "#475569",
        "guide_fill": "#d6deeb",
        "identity_fill": "#0b5cad",
        "label_fill": "#334155",
        "step_fill": "#64748b",
        "generator_positive": "#0f766e",
        "generator_negative": "#c2410c",
        "under_fill": "#94a3b8",
        "badge_fill": "#eef4ff",
        "badge_outline": "#d6deeb",
    },
    PRESENTATION_PREVIEW_STYLE: {
        "canvas_fill": "#ffffff",
        "header_fill": "#f8fbff",
        "header_outline": "#cbd5e1",
        "title_fill": "#020617",
        "summary_fill": "#334155",
        "guide_fill": "#e2e8f0",
        "identity_fill": "#1d4ed8",
        "label_fill": "#1e293b",
        "step_fill": "#475569",
        "generator_positive": "#0369a1",
        "generator_negative": "#b45309",
        "under_fill": "#94a3b8",
        "badge_fill": "#eff6ff",
        "badge_outline": "#bfdbfe",
    },
}

_STRAND_PALETTE = (
    "#2563eb",
    "#0f766e",
    "#9333ea",
    "#ea580c",
    "#0891b2",
    "#dc2626",
)


@dataclass(frozen=True, slots=True)
class PreviewLine:
    role: str
    x1: float
    y1: float
    x2: float
    y2: float
    fill: str
    width: int
    dash: tuple[int, int] | None = None
    points: tuple[float, ...] | None = None
    smooth: bool = False


@dataclass(frozen=True, slots=True)
class PreviewRect:
    role: str
    x1: float
    y1: float
    x2: float
    y2: float
    fill: str
    outline: str


@dataclass(frozen=True, slots=True)
class PreviewText:
    role: str
    x: float
    y: float
    text: str
    fill: str
    anchor: str = "center"


@dataclass(frozen=True, slots=True)
class PreviewOval:
    role: str
    x1: float
    y1: float
    x2: float
    y2: float
    fill: str
    outline: str


@dataclass(frozen=True, slots=True)
class BraidPreviewGeometry:
    width: int
    height: int
    rectangles: tuple[PreviewRect, ...]
    lines: tuple[PreviewLine, ...]
    texts: tuple[PreviewText, ...]
    ovals: tuple[PreviewOval, ...]
    final_permutation: tuple[int, ...]


def _get_preview_style(style: str) -> dict[str, str]:
    if style not in _PREVIEW_STYLES:
        raise ValueError(f"Unknown braid preview style: {style}")
    return _PREVIEW_STYLES[style]


def _strand_color(strand_identity: int) -> str:
    return _STRAND_PALETTE[strand_identity % len(_STRAND_PALETTE)]


def compute_braid_permutation(braid_word: BraidWord) -> tuple[int, ...]:
    """Return the bottom-lane ordering as a 1-based permutation tuple."""

    current_order = list(range(braid_word.num_strands))
    for generator in braid_word.generators:
        pair_index = abs(generator) - 1
        current_order[pair_index], current_order[pair_index + 1] = current_order[pair_index + 1], current_order[pair_index]
    return tuple(strand_identity + 1 for strand_identity in current_order)


def _right_gutter_width(braid_word: BraidWord) -> int:
    longest_label = max((len(f"σ{abs(generator)}^-1") if generator < 0 else len(f"σ{abs(generator)}") for generator in braid_word.generators), default=8)
    return max(MIN_RIGHT_GUTTER, 72 + 14 * longest_label)


def _compute_canvas_size(braid_word: BraidWord, viewport_width: int, viewport_height: int) -> tuple[int, int, int, float]:
    right_gutter = _right_gutter_width(braid_word)
    strand_region_width = STRAND_SPACING * max(braid_word.num_strands - 1, 1)
    width = max(viewport_width, LEFT_MARGIN + right_gutter + strand_region_width + 48)
    if braid_word.generators:
        desired_step_height = min(MAX_STEP_HEIGHT, max(MIN_STEP_HEIGHT, 760 / len(braid_word.generators)))
    else:
        desired_step_height = STEP_HEIGHT
    height = max(viewport_height, TOP_MARGIN + BOTTOM_MARGIN + desired_step_height * max(len(braid_word.generators), 1) + 36)
    return width, height, right_gutter, desired_step_height


def _cut_line_segment(x1: float, y1: float, x2: float, y2: float, *, gap_size: float = 18.0) -> tuple[tuple[float, float, float, float], tuple[float, float, float, float]]:
    dx = x2 - x1
    dy = y2 - y1
    length = hypot(dx, dy)
    if length <= gap_size:
        midpoint_x = (x1 + x2) / 2
        midpoint_y = (y1 + y2) / 2
        return (x1, y1, midpoint_x, midpoint_y), (midpoint_x, midpoint_y, x2, y2)

    offset = (gap_size / 2) / length
    cut_left_x = (x1 + x2) / 2 - dx * offset
    cut_left_y = (y1 + y2) / 2 - dy * offset
    cut_right_x = (x1 + x2) / 2 + dx * offset
    cut_right_y = (y1 + y2) / 2 + dy * offset
    return (x1, y1, cut_left_x, cut_left_y), (cut_right_x, cut_right_y, x2, y2)


def _make_smooth_points(*points: tuple[float, float]) -> tuple[float, ...]:
    flattened: list[float] = []
    for x_value, y_value in points:
        flattened.extend((x_value, y_value))
    return tuple(flattened)


def _cubic_bezier_point(
    start: tuple[float, float],
    control_1: tuple[float, float],
    control_2: tuple[float, float],
    end: tuple[float, float],
    t_value: float,
) -> tuple[float, float]:
    inv_t = 1.0 - t_value
    x_value = (
        inv_t**3 * start[0]
        + 3 * inv_t**2 * t_value * control_1[0]
        + 3 * inv_t * t_value**2 * control_2[0]
        + t_value**3 * end[0]
    )
    y_value = (
        inv_t**3 * start[1]
        + 3 * inv_t**2 * t_value * control_1[1]
        + 3 * inv_t * t_value**2 * control_2[1]
        + t_value**3 * end[1]
    )
    return x_value, y_value


def _sample_cubic_bezier(
    start: tuple[float, float],
    control_1: tuple[float, float],
    control_2: tuple[float, float],
    end: tuple[float, float],
    *,
    samples: int = CURVE_SAMPLES,
) -> tuple[float, ...]:
    return _make_smooth_points(
        *[
            _cubic_bezier_point(start, control_1, control_2, end, index / samples)
            for index in range(samples + 1)
        ]
    )


def _flattened_points_to_pairs(points: tuple[float, ...]) -> list[tuple[float, float]]:
    return [(points[index], points[index + 1]) for index in range(0, len(points), 2)]


def _split_points_with_gap(points: tuple[float, ...], gap_size: float) -> tuple[tuple[float, ...], tuple[float, ...]]:
    point_pairs = _flattened_points_to_pairs(points)
    if len(point_pairs) < 4:
        midpoint = len(point_pairs) // 2
        return _make_smooth_points(*point_pairs[: midpoint + 1]), _make_smooth_points(*point_pairs[midpoint:])

    segment_lengths = [
        hypot(point_pairs[index + 1][0] - point_pairs[index][0], point_pairs[index + 1][1] - point_pairs[index][1])
        for index in range(len(point_pairs) - 1)
    ]
    total_length = sum(segment_lengths)
    if total_length <= gap_size:
        midpoint = len(point_pairs) // 2
        return _make_smooth_points(*point_pairs[: midpoint + 1]), _make_smooth_points(*point_pairs[midpoint:])

    gap_start = total_length / 2 - gap_size / 2
    gap_end = total_length / 2 + gap_size / 2
    travelled = 0.0
    first_part: list[tuple[float, float]] = [point_pairs[0]]
    second_part: list[tuple[float, float]] = []

    for index, segment_length in enumerate(segment_lengths):
        segment_start = point_pairs[index]
        segment_end = point_pairs[index + 1]
        next_travelled = travelled + segment_length

        if travelled < gap_start <= next_travelled and segment_length > 0:
            ratio = (gap_start - travelled) / segment_length
            first_part.append(
                (
                    segment_start[0] + (segment_end[0] - segment_start[0]) * ratio,
                    segment_start[1] + (segment_end[1] - segment_start[1]) * ratio,
                )
            )

        if travelled < gap_end <= next_travelled and segment_length > 0:
            ratio = (gap_end - travelled) / segment_length
            second_part.append(
                (
                    segment_start[0] + (segment_end[0] - segment_start[0]) * ratio,
                    segment_start[1] + (segment_end[1] - segment_start[1]) * ratio,
                )
            )

        if next_travelled < gap_start:
            first_part.append(segment_end)
        elif travelled >= gap_end:
            second_part.append(segment_end)

        travelled = next_travelled

    if not second_part:
        second_part = point_pairs[-2:]

    return _make_smooth_points(*first_part), _make_smooth_points(*second_part)


def _build_vertical_segment_points(x_position: float, top_y: float, bottom_y: float) -> tuple[float, ...]:
    y_delta = bottom_y - top_y
    return _sample_cubic_bezier(
        (x_position, top_y),
        (x_position, top_y + y_delta * VERTICAL_CURVE_PULL),
        (x_position, bottom_y - y_delta * VERTICAL_CURVE_PULL),
        (x_position, bottom_y),
    )


def _build_crossing_points(start_x: float, start_y: float, end_x: float, end_y: float) -> tuple[float, ...]:
    y_delta = end_y - start_y
    return _sample_cubic_bezier(
        (start_x, start_y),
        (start_x, start_y + y_delta * CROSSING_CURVE_PULL),
        (end_x, end_y - y_delta * CROSSING_CURVE_PULL),
        (end_x, end_y),
    )


def _render_header(
    geometry_texts: list[PreviewText],
    geometry_rectangles: list[PreviewRect],
    braid_word: BraidWord,
    width: int,
    style_data: dict[str, str],
    *,
    final_permutation: tuple[int, ...],
) -> None:
    card_left = HEADER_CARD_MARGIN
    card_top = HEADER_CARD_MARGIN
    card_right = width - HEADER_CARD_MARGIN
    card_bottom = HEADER_CARD_MARGIN + HEADER_HEIGHT
    geometry_rectangles.append(
        PreviewRect(
            "header_panel",
            card_left,
            card_top,
            card_right,
            card_bottom,
            style_data["header_fill"],
            style_data["header_outline"],
        )
    )
    geometry_rectangles.append(
        PreviewRect(
            "summary_badge",
            card_left + 14,
            card_bottom - 30,
            card_left + 360,
            card_bottom - 10,
            style_data["badge_fill"],
            style_data["badge_outline"],
        )
    )
    geometry_texts.append(
        PreviewText(
            "word_header",
            card_left + 16,
            card_top + 20,
            f"Braid preview: {braid_word.label or 'unnamed'}",
            style_data["title_fill"],
            anchor="w",
        )
    )
    geometry_texts.append(
        PreviewText(
            "word_detail",
            card_left + 16,
            card_top + 42,
            f"Word: {braid_word.word_string()}",
            style_data["summary_fill"],
            anchor="w",
        )
    )
    geometry_texts.append(
        PreviewText(
            "summary_header",
            card_left + 24,
            card_bottom - 20,
            (
                f"Strands: {braid_word.num_strands}    Crossings: {len(braid_word.generators)}    "
                f"Writhe: {braid_word.writhe()}    Final permutation: {list(final_permutation)}"
            ),
            style_data["summary_fill"],
            anchor="w",
        )
    )


def _append_smooth_line(
    lines: list[PreviewLine],
    role: str,
    points: tuple[float, ...],
    fill: str,
    width: int,
    *,
    dash: tuple[int, int] | None = None,
) -> None:
    lines.append(
        PreviewLine(
            role=role,
            x1=points[0],
            y1=points[1],
            x2=points[-2],
            y2=points[-1],
            fill=fill,
            width=width,
            dash=dash,
            points=points,
            smooth=False,
        )
    )


def _svg_color(color: str) -> str:
    return color


def render_braid_preview_svg(
    braid_word: BraidWord,
    *,
    viewport_width: int,
    viewport_height: int,
    style: str = STANDARD_PREVIEW_STYLE,
) -> str:
    geometry = build_braid_preview_geometry(
        braid_word,
        viewport_width=viewport_width,
        viewport_height=viewport_height,
        style=style,
    )
    style_data = _get_preview_style(style)
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{geometry.width}" height="{geometry.height}" viewBox="0 0 {geometry.width} {geometry.height}">',
        f'<rect x="0" y="0" width="{geometry.width}" height="{geometry.height}" fill="{_svg_color(style_data["canvas_fill"])}" />',
    ]
    for rectangle in geometry.rectangles:
        lines.append(
            f'<rect x="{rectangle.x1}" y="{rectangle.y1}" width="{rectangle.x2 - rectangle.x1}" height="{rectangle.y2 - rectangle.y1}" fill="{_svg_color(rectangle.fill)}" stroke="{_svg_color(rectangle.outline)}" rx="10" ry="10" />'
        )
    for line in geometry.lines:
        dash_text = ""
        if line.dash is not None:
            dash_text = f' stroke-dasharray="{line.dash[0]} {line.dash[1]}"'
        if line.points is not None:
            points_text = " ".join(f"{line.points[index]},{line.points[index + 1]}" for index in range(0, len(line.points), 2))
            lines.append(
                f'<polyline points="{points_text}" fill="none" stroke="{_svg_color(line.fill)}" stroke-width="{line.width}" stroke-linecap="round" stroke-linejoin="round"{dash_text} />'
            )
        else:
            lines.append(
                f'<line x1="{line.x1}" y1="{line.y1}" x2="{line.x2}" y2="{line.y2}" fill="none" stroke="{_svg_color(line.fill)}" stroke-width="{line.width}" stroke-linecap="round" stroke-linejoin="round"{dash_text} />'
            )
    for oval in geometry.ovals:
        center_x = (oval.x1 + oval.x2) / 2
        center_y = (oval.y1 + oval.y2) / 2
        radius_x = (oval.x2 - oval.x1) / 2
        radius_y = (oval.y2 - oval.y1) / 2
        lines.append(
            f'<ellipse cx="{center_x}" cy="{center_y}" rx="{radius_x}" ry="{radius_y}" fill="{_svg_color(oval.fill)}" stroke="{_svg_color(oval.outline)}" />'
        )
    for text in geometry.texts:
        anchor = {"w": "start", "center": "middle", "e": "end"}.get(text.anchor, "middle")
        lines.append(
            f'<text x="{text.x}" y="{text.y}" fill="{_svg_color(text.fill)}" font-family="Segoe UI, Arial, sans-serif" font-size="14" text-anchor="{anchor}">{escape(text.text)}</text>'
        )
    lines.append("</svg>")
    return "\n".join(lines)


def save_braid_preview_svg(
    file_path: str | Path,
    braid_word: BraidWord,
    *,
    viewport_width: int,
    viewport_height: int,
    style: str = STANDARD_PREVIEW_STYLE,
) -> Path:
    target_path = Path(file_path)
    target_path.write_text(
        render_braid_preview_svg(
            braid_word,
            viewport_width=viewport_width,
            viewport_height=viewport_height,
            style=style,
        ),
        encoding="utf-8",
    )
    return target_path


def build_braid_preview_geometry(
    braid_word: BraidWord,
    *,
    viewport_width: int,
    viewport_height: int,
    style: str = STANDARD_PREVIEW_STYLE,
) -> BraidPreviewGeometry:
    style_data = _get_preview_style(style)
    width, height, right_gutter, desired_step_height = _compute_canvas_size(braid_word, viewport_width, viewport_height)
    final_permutation = compute_braid_permutation(braid_word)
    top = TOP_MARGIN
    bottom = height - BOTTOM_MARGIN
    strand_region_right = width - right_gutter
    label_x = strand_region_right + 52
    lane_x = [LEFT_MARGIN + index * (strand_region_right - LEFT_MARGIN) / max(braid_word.num_strands - 1, 1) for index in range(braid_word.num_strands)]

    rectangles: list[PreviewRect] = []
    lines: list[PreviewLine] = []
    texts: list[PreviewText] = []
    ovals: list[PreviewOval] = []
    _render_header(texts, rectangles, braid_word, width, style_data, final_permutation=final_permutation)

    for index, x_position in enumerate(lane_x, start=1):
        lines.append(PreviewLine("strand_guide", x_position, top, x_position, bottom, style_data["guide_fill"], 1, dash=(3, 5)))
        ovals.append(PreviewOval("top_endpoint", x_position - 6, top - 20, x_position + 6, top - 8, "#ffffff", "#9a9a9a"))
        texts.append(PreviewText("strand_label", x_position, top - 16, str(index), style_data["label_fill"]))

    if not braid_word.generators:
        identity_banner_top = bottom + 10
        identity_banner_bottom = bottom + IDENTITY_LABEL_GAP
        rectangles.append(
            PreviewRect(
                "identity_badge",
                width / 2 - 92,
                identity_banner_top,
                width / 2 + 92,
                identity_banner_bottom,
                style_data["badge_fill"],
                style_data["badge_outline"],
            )
        )
        for strand_identity, x_position in enumerate(lane_x):
            _append_smooth_line(lines, "identity_strand", _build_vertical_segment_points(x_position, top, bottom), _strand_color(strand_identity), 4)
            ovals.append(PreviewOval("bottom_endpoint", x_position - 5, bottom + 6, x_position + 5, bottom + 16, "#ffffff", "#9a9a9a"))
        texts.append(PreviewText("identity_label", width / 2, bottom + 22, "identity braid", style_data["identity_fill"]))
        return BraidPreviewGeometry(width=width, height=height, rectangles=tuple(rectangles), lines=tuple(lines), texts=tuple(texts), ovals=tuple(ovals), final_permutation=final_permutation)

    current_order = list(range(braid_word.num_strands))
    current_y = top
    step_gap = max((bottom - top) / max(len(braid_word.generators), 1), desired_step_height)

    for step_index, generator in enumerate(braid_word.generators, start=1):
        next_y = current_y + step_gap
        pair_index = abs(generator) - 1
        next_order = list(current_order)
        next_order[pair_index], next_order[pair_index + 1] = current_order[pair_index + 1], current_order[pair_index]

        for strand_index in range(braid_word.num_strands):
            if strand_index in (pair_index, pair_index + 1):
                continue
            strand_identity = current_order[strand_index]
            _append_smooth_line(lines, "unchanged_strand", _build_vertical_segment_points(lane_x[strand_index], current_y, next_y), _strand_color(strand_identity), 3)

        upper_lane_x = lane_x[pair_index]
        lower_lane_x = lane_x[pair_index + 1]
        crossing_x = (upper_lane_x + lower_lane_x) / 2
        crossing_y = (current_y + next_y) / 2
        gap_size = max(CROSSING_GAP_SIZE, min(24.0, abs(lower_lane_x - upper_lane_x) * 0.24))

        if generator > 0:
            over_identity = current_order[pair_index]
            over_color = _strand_color(over_identity)
            label = f"σ{abs(generator)}"
            generator_label_fill = style_data["generator_positive"]
            over_points = _build_crossing_points(upper_lane_x, current_y, lower_lane_x, next_y)
            under_points = _build_crossing_points(lower_lane_x, current_y, upper_lane_x, next_y)
        else:
            over_identity = current_order[pair_index + 1]
            over_color = _strand_color(over_identity)
            label = f"σ{abs(generator)}^-1"
            generator_label_fill = style_data["generator_negative"]
            over_points = _build_crossing_points(lower_lane_x, current_y, upper_lane_x, next_y)
            under_points = _build_crossing_points(upper_lane_x, current_y, lower_lane_x, next_y)

        under_first, under_second = _split_points_with_gap(under_points, gap_size)
        _append_smooth_line(
            lines,
            "under_strand",
            under_first,
            style_data["under_fill"],
            3,
        )
        _append_smooth_line(
            lines,
            "under_strand",
            under_second,
            style_data["under_fill"],
            3,
        )
        ovals.append(PreviewOval("crossing_gap", crossing_x - gap_size / 2, crossing_y - gap_size / 2, crossing_x + gap_size / 2, crossing_y + gap_size / 2, style_data["canvas_fill"], style_data["canvas_fill"]))
        _append_smooth_line(
            lines,
            "over_shadow",
            over_points,
            "#ffffff",
            8,
        )
        _append_smooth_line(
            lines,
            "over_strand",
            over_points,
            over_color,
            5,
        )
        rectangles.append(
            PreviewRect(
                "generator_badge",
                label_x - 14,
                crossing_y - 12,
                width - 18,
                crossing_y + 12,
                style_data["badge_fill"],
                style_data["badge_outline"],
            )
        )
        texts.append(PreviewText("step_index", STEP_INDEX_X, crossing_y, str(step_index), style_data["step_fill"]))
        texts.append(PreviewText("generator_label", label_x, crossing_y, label, generator_label_fill, anchor="w"))

        current_order = next_order
        current_y = next_y

    for strand_index, x_position in enumerate(lane_x):
        strand_identity = current_order[strand_index]
        _append_smooth_line(
            lines,
            "terminal_strand",
            _build_vertical_segment_points(x_position, current_y, bottom),
            _strand_color(strand_identity),
            3,
        )
        ovals.append(PreviewOval("bottom_endpoint", x_position - 5, bottom + 6, x_position + 5, bottom + 16, "#ffffff", "#9a9a9a"))
        texts.append(PreviewText("bottom_label", x_position, bottom + 28, str(strand_identity + 1), style_data["label_fill"]))

    return BraidPreviewGeometry(width=width, height=height, rectangles=tuple(rectangles), lines=tuple(lines), texts=tuple(texts), ovals=tuple(ovals), final_permutation=final_permutation)


def render_braid_preview(
    canvas: tk.Canvas,
    braid_word: BraidWord,
    *,
    viewport_width: int,
    viewport_height: int,
    style: str = STANDARD_PREVIEW_STYLE,
) -> BraidPreviewGeometry:
    geometry = build_braid_preview_geometry(
        braid_word,
        viewport_width=viewport_width,
        viewport_height=viewport_height,
        style=style,
    )
    style_data = _get_preview_style(style)
    canvas.delete("all")
    canvas.configure(background=style_data["canvas_fill"])
    canvas.configure(scrollregion=(0, 0, geometry.width, geometry.height))

    for rectangle in geometry.rectangles:
        canvas.create_rectangle(
            rectangle.x1,
            rectangle.y1,
            rectangle.x2,
            rectangle.y2,
            fill=rectangle.fill,
            outline=rectangle.outline,
            width=1,
        )

    for line in geometry.lines:
        create_kwargs: dict[str, object] = {"fill": line.fill, "width": line.width}
        if line.dash is not None:
            create_kwargs["dash"] = line.dash
        if line.smooth:
            create_kwargs["smooth"] = True
        create_kwargs["capstyle"] = tk.ROUND
        create_kwargs["joinstyle"] = tk.ROUND
        if line.points is not None:
            canvas.create_line(*line.points, **create_kwargs)
        else:
            canvas.create_line(line.x1, line.y1, line.x2, line.y2, **create_kwargs)

    for oval in geometry.ovals:
        canvas.create_oval(oval.x1, oval.y1, oval.x2, oval.y2, fill=oval.fill, outline=oval.outline)

    for text in geometry.texts:
        canvas.create_text(text.x, text.y, text=text.text, fill=text.fill, anchor=text.anchor)

    return geometry