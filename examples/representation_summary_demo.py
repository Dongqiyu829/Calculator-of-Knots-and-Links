"""Print the three MVP-stage representation summaries.

Run this script from the project root with:

    C:/Users/dongqiyu/anaconda3/python.exe examples/representation_summary_demo.py
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.algebra.representations import get_supported_representations


def main() -> None:
    """Print summaries for all currently supported representations."""

    for key, representation in get_supported_representations().items():
        print(f"=== {key} ===")
        print(representation.summary())
        print()


if __name__ == "__main__":
    main()