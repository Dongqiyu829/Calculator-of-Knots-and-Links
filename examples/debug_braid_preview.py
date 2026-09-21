"""Export a fixed set of braid preview SVGs for renderer debugging."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.braid.braid_word import BraidWord
from src.gui.braid_preview_renderer import (
    PRESENTATION_PREVIEW_STYLE,
    STANDARD_PREVIEW_STYLE,
    build_braid_preview_geometry,
    save_braid_preview_svg,
)


SAMPLE_CASES = (
    ("identity_3", 3, ()),
    ("sigma_1", 3, (1,)),
    ("sigma_2", 3, (2,)),
    ("sigma_1_sigma_2", 3, (1, 2)),
    ("sigma_1_sigma_2_sigma_1", 3, (1, 2, 1)),
    ("sigma_2_sigma_1_sigma_2", 3, (2, 1, 2)),
    ("sigma_1_sigma_1_inverse", 2, (1, -1)),
    ("sigma_1_cubed", 2, (1, 1, 1)),
    ("negative_mixed", 3, (-1, 2, -1, 2)),
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export ordinary braid preview SVGs for manual inspection.")
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "artifacts" / "braid_preview_debug"),
        help="Directory where the SVG previews will be written.",
    )
    parser.add_argument(
        "--style",
        choices=(STANDARD_PREVIEW_STYLE, PRESENTATION_PREVIEW_STYLE),
        default=STANDARD_PREVIEW_STYLE,
        help="Preview style to export.",
    )
    parser.add_argument("--width", type=int, default=720, help="Viewport width passed to the renderer.")
    parser.add_argument("--height", type=int, default=360, help="Viewport height passed to the renderer.")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Writing braid preview SVGs to: {output_dir}")
    for label, num_strands, generators in SAMPLE_CASES:
        braid_word = BraidWord.from_iterable(num_strands, generators, label=label)
        geometry = build_braid_preview_geometry(
            braid_word,
            viewport_width=args.width,
            viewport_height=args.height,
            style=args.style,
        )
        target_path = output_dir / f"{label}.svg"
        save_braid_preview_svg(
            target_path,
            braid_word,
            viewport_width=args.width,
            viewport_height=args.height,
            style=args.style,
        )
        print(
            f"- {label}: strands={num_strands}, generators={list(generators)}, "
            f"final_permutation={list(geometry.final_permutation)}, file={target_path.name}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
