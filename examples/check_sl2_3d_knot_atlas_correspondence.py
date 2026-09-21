"""Print the current Knot Atlas correspondence status for the sl2 3D candidate branch."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import sympy as sp

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.invariants.sl2_3d_colored_jones_candidate import (
    evaluate_sl2_3d_knot_atlas_correspondence,
    get_sl2_3d_knot_atlas_current_status_lines,
    get_sl2_3d_knot_atlas_summary_lines,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Show the current sl2 3D vs Knot Atlas correspondence wording.")
    parser.add_argument(
        "--recompute",
        action="store_true",
        help="Recompute the symbolic correspondence checks instead of printing the stored current status lines.",
    )
    args = parser.parse_args()

    print("Current shared wording:")
    for line in get_sl2_3d_knot_atlas_summary_lines():
        print(f"- {line}")
    print()

    if not args.recompute:
        print("Current stored status lines:")
        for line in get_sl2_3d_knot_atlas_current_status_lines():
            print(f"- {line}")
        print()
        print("Use --recompute if you want the script to rerun the symbolic correspondence checks.")
        return

    q = sp.Symbol("q", nonzero=True)
    print("Current correspondence checks:")
    for check in evaluate_sl2_3d_knot_atlas_correspondence(q=q):
        print(check.summary())
        print()


if __name__ == "__main__":
    main()