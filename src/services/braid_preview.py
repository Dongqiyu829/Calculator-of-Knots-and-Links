"""Deterministic braid-diagram geometry for maintained frontends.

This module deliberately accepts an already validated :class:`BraidWord`.
Parsing and validation remain in ``src.services.braid_evaluation``; the Qt
frontend only asks this module to describe a word.  The geometry uses the
project-native Artin convention: ``+i`` is ``sigma_i`` and ``-i`` is its
inverse.  At a positive crossing the left lane goes over, while at a negative
crossing the right lane goes over.
"""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path
from src.braid.braid_word import BraidWord


LEFT_MARGIN = 56.0
RIGHT_MARGIN = 180.0
TOP_MARGIN = 52.0
BOTTOM_MARGIN = 48.0
MIN_LANE_SPACING = 64.0
STEP_HEIGHT = 72.0
CROSSING_GAP = 16.0

_STRAND_COLORS = (
    "#2563eb",
    "#db2777",
    "#059669",
    "#d97706",
    "#7c3aed",
    "#0891b2",
    "#dc2626",
    "#4f46e5",
)


@dataclass(frozen=True, slots=True)
class BraidPreviewSegment:
    """One deterministic vector stroke in the diagram."""

    role: str
    strand_identity: int
    step_index: int | None
    generator: int | None
    points: tuple[tuple[float, float], ...]
    color: str
    over: bool = False


@dataclass(frozen=True, slots=True)
class BraidPreviewCrossing:
    """Semantic crossing information independent of painting technology."""

    step_index: int
    generator: int
    lane_index: int
    over_strand: int
    under_strand: int
    x: float
    y: float


@dataclass(frozen=True, slots=True)
class BraidPreviewGeometry:
    """A complete, renderer-independent braid diagram description."""

    width: float
    height: float
    strand_count: int
    generators: tuple[int, ...]
    writhe: int
    final_permutation: tuple[int, ...]
    segments: tuple[BraidPreviewSegment, ...]
    crossings: tuple[BraidPreviewCrossing, ...]
    label: str = ""

    @property
    def is_identity(self) -> bool:
        return not self.generators

    @property
    def metadata_text(self) -> str:
        generators = "identity" if not self.generators else " ".join(str(value) for value in self.generators)
        permutation = "(" + ", ".join(str(value) for value in self.final_permutation) + ")"
        return (
            f"{self.strand_count} strands  •  writhe {self.writhe}  •  "
            f"generators: {generators}  •  final permutation: {permutation}"
        )


def compute_braid_permutation(braid_word: BraidWord) -> tuple[int, ...]:
    """Return the bottom-lane strand identities using the project order."""

    current = list(range(1, braid_word.num_strands + 1))
    for generator in braid_word.generators:
        pair = abs(generator) - 1
        current[pair], current[pair + 1] = current[pair + 1], current[pair]
    return tuple(current)


def _color(strand_identity: int) -> str:
    return _STRAND_COLORS[(strand_identity - 1) % len(_STRAND_COLORS)]


def _crossing_points(start_x: float, start_y: float, end_x: float, end_y: float) -> tuple[tuple[float, float], ...]:
    mid_x = (start_x + end_x) / 2.0
    mid_y = (start_y + end_y) / 2.0
    return ((start_x, start_y), (mid_x, mid_y), (end_x, end_y))


def _split_at_gap(points: tuple[tuple[float, float], ...], gap: float) -> tuple[tuple[tuple[float, float], ...], tuple[tuple[float, float], ...]]:
    start, center, end = points
    dx_start, dy_start = center[0] - start[0], center[1] - start[1]
    dx_end, dy_end = end[0] - center[0], end[1] - center[1]
    first_length = max((dx_start * dx_start + dy_start * dy_start) ** 0.5, 1.0)
    second_length = max((dx_end * dx_end + dy_end * dy_end) ** 0.5, 1.0)
    before = (center[0] - dx_start * gap / (2 * first_length), center[1] - dy_start * gap / (2 * first_length))
    after = (center[0] + dx_end * gap / (2 * second_length), center[1] + dy_end * gap / (2 * second_length))
    return ((start, before), (after, end))


def build_braid_preview_geometry(
    braid_word: BraidWord,
    *,
    viewport_width: int = 760,
    viewport_height: int = 360,
) -> BraidPreviewGeometry:
    """Build stable geometry for a validated braid word.

    Width and height are lower bounds supplied by the containing view.  Long
    words therefore expand deterministically and can be scrolled without
    squeezing crossings together.
    """

    strands = braid_word.num_strands
    generators = tuple(braid_word.generators)
    width = max(float(viewport_width), LEFT_MARGIN + RIGHT_MARGIN + MIN_LANE_SPACING * max(strands - 1, 0))
    height = max(float(viewport_height), TOP_MARGIN + BOTTOM_MARGIN + STEP_HEIGHT * max(len(generators), 1))
    lane_region_right = width - RIGHT_MARGIN
    lane_spacing = (lane_region_right - LEFT_MARGIN) / max(strands - 1, 1)
    lane_x = tuple(LEFT_MARGIN + index * lane_spacing for index in range(strands))
    top = TOP_MARGIN
    bottom = height - BOTTOM_MARGIN
    step_height = (bottom - top) / max(len(generators), 1)

    segments: list[BraidPreviewSegment] = []
    crossings: list[BraidPreviewCrossing] = []
    current_order = list(range(1, strands + 1))

    if not generators:
        for identity, x in enumerate(lane_x, start=1):
            segments.append(BraidPreviewSegment("identity", identity, None, None, ((x, top), (x, bottom)), _color(identity)))
        return BraidPreviewGeometry(
            width, height, strands, generators, braid_word.writhe(), compute_braid_permutation(braid_word), tuple(segments), tuple(crossings), braid_word.label
        )

    for step_index, generator in enumerate(generators, start=1):
        current_y = top + (step_index - 1) * step_height
        next_y = top + step_index * step_height
        pair = abs(generator) - 1
        next_order = list(current_order)
        next_order[pair], next_order[pair + 1] = next_order[pair + 1], next_order[pair]

        for lane in range(strands):
            if lane in (pair, pair + 1):
                continue
            identity = current_order[lane]
            segments.append(BraidPreviewSegment("unchanged", identity, step_index, generator, ((lane_x[lane], current_y), (lane_x[lane], next_y)), _color(identity)))

        left_x, right_x = lane_x[pair], lane_x[pair + 1]
        crossing_x = (left_x + right_x) / 2.0
        crossing_y = (current_y + next_y) / 2.0
        if generator > 0:
            over_identity = current_order[pair]
            under_identity = current_order[pair + 1]
            over_points = _crossing_points(left_x, current_y, right_x, next_y)
            under_points = _crossing_points(right_x, current_y, left_x, next_y)
        else:
            over_identity = current_order[pair + 1]
            under_identity = current_order[pair]
            over_points = _crossing_points(right_x, current_y, left_x, next_y)
            under_points = _crossing_points(left_x, current_y, right_x, next_y)
        under_first, under_second = _split_at_gap(under_points, min(CROSSING_GAP, lane_spacing * 0.24))
        segments.append(BraidPreviewSegment("under", under_identity, step_index, generator, under_first, _color(under_identity)))
        segments.append(BraidPreviewSegment("under", under_identity, step_index, generator, under_second, _color(under_identity)))
        segments.append(BraidPreviewSegment("over", over_identity, step_index, generator, over_points, _color(over_identity), over=True))
        crossings.append(BraidPreviewCrossing(step_index, generator, pair + 1, over_identity, under_identity, crossing_x, crossing_y))
        current_order = next_order

    for lane, identity in enumerate(current_order):
        segments.append(BraidPreviewSegment("terminal", identity, len(generators), None, ((lane_x[lane], top + len(generators) * step_height), (lane_x[lane], bottom)), _color(identity)))

    return BraidPreviewGeometry(
        width, height, strands, generators, braid_word.writhe(), compute_braid_permutation(braid_word), tuple(segments), tuple(crossings), braid_word.label
    )


def render_braid_preview_svg(
    geometry_or_word: BraidPreviewGeometry | BraidWord,
    *,
    viewport_width: int = 760,
    viewport_height: int = 360,
) -> str:
    """Render geometry as deterministic standalone SVG text.

    A geometry object is preferred for reusable callers.  Accepting a
    validated ``BraidWord`` as a convenience keeps the API ergonomic without
    moving parsing into a renderer.
    """

    geometry = (
        geometry_or_word
        if isinstance(geometry_or_word, BraidPreviewGeometry)
        else build_braid_preview_geometry(geometry_or_word, viewport_width=viewport_width, viewport_height=viewport_height)
    )

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{geometry.width:g}" height="{geometry.height:g}" viewBox="0 0 {geometry.width:g} {geometry.height:g}">',
        f"<title>{escape(geometry.label or 'braid preview')}</title>",
        f'<desc>{escape(geometry.metadata_text)}</desc>',
        f'<rect width="100%" height="100%" fill="#fbfcfe"/>',
    ]
    lane_region_right = geometry.width - RIGHT_MARGIN
    spacing = (lane_region_right - LEFT_MARGIN) / max(geometry.strand_count - 1, 1)
    for index in range(geometry.strand_count):
        x = LEFT_MARGIN + index * spacing
        lines.append(f'<line x1="{x:g}" y1="{TOP_MARGIN:g}" x2="{x:g}" y2="{geometry.height - BOTTOM_MARGIN:g}" stroke="#cbd5e1" stroke-dasharray="3 6"/>')
        lines.append(f'<text x="{x:g}" y="28" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#334155">{index + 1}</text>')
        lines.append(f'<text x="{x:g}" y="{geometry.height - 20:g}" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#334155">{geometry.final_permutation[index]}</text>')
    for segment in geometry.segments:
        points = " ".join(f"{x:g},{y:g}" for x, y in segment.points)
        if segment.over:
            lines.append(f'<polyline points="{points}" fill="none" stroke="#ffffff" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>')
        dash = ' stroke-dasharray="1 0"' if segment.role != "under" else ""
        lines.append(f'<polyline points="{points}" fill="none" stroke="{segment.color}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"{dash}/>')
    for crossing in geometry.crossings:
        label = f"{crossing.step_index}: σ{abs(crossing.generator)}" + ("⁻¹" if crossing.generator < 0 else "")
        lines.append(f'<text x="{geometry.width - RIGHT_MARGIN + 20:g}" y="{crossing.y + 5:g}" font-family="sans-serif" font-size="12" fill="#475569">{escape(label)}</text>')
    if geometry.is_identity:
        lines.append(f'<text x="{geometry.width / 2:g}" y="{geometry.height - 16:g}" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#475569">identity braid</text>')
    lines.append("</svg>")
    return "\n".join(lines)


def save_braid_preview_svg(
    path: str | Path,
    geometry_or_word: BraidPreviewGeometry | BraidWord,
    *,
    viewport_width: int = 760,
    viewport_height: int = 360,
) -> Path:
    target = Path(path)
    target.write_text(
        render_braid_preview_svg(geometry_or_word, viewport_width=viewport_width, viewport_height=viewport_height),
        encoding="utf-8",
    )
    return target


__all__ = [
    "BraidPreviewCrossing",
    "BraidPreviewGeometry",
    "BraidPreviewSegment",
    "build_braid_preview_geometry",
    "compute_braid_permutation",
    "render_braid_preview_svg",
    "save_braid_preview_svg",
]
