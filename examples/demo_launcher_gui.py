"""Launch the Tkinter frontend for the current multibranch invariant skeleton."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.gui.demo_launcher import main


if __name__ == "__main__":
    raise SystemExit(main())