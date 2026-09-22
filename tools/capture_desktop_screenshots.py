"""Capture documentation images from the real maintained PySide6 application.

This is a maintainer tool, not a mockup generator.  It instantiates the same
``DesktopMainWindow`` used by ``python -m src.desktop`` and only loads existing
curated examples; no invariant or custom-operator evaluation is started.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("docs/images"),
        help="directory for PNG captures (default: docs/images)",
    )
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # The environment must be selected before importing Qt.  On Windows the
    # native platform plugin is generally preferable; Linux maintainers can
    # set QT_QPA_PLATFORM=offscreen for a deterministic headless refresh.
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    from src.desktop import DesktopMainWindow
    from src.services import get_curated_example

    app = QApplication.instance() or QApplication([])
    window = DesktopMainWindow()
    window.resize(1400, 920)
    window.show()
    app.processEvents()

    window._load_curated_example(get_curated_example("catalog.trefoil"))
    app.processEvents()
    if not window.grab().save(str(args.output_dir / "invariant-trefoil.png"), "PNG"):
        raise OSError("Could not save invariant-trefoil.png")

    window._load_curated_example(get_curated_example("rmatrix.sl2_fundamental_check_r"))
    app.processEvents()
    if not window.grab().save(str(args.output_dir / "custom-check-r.png"), "PNG"):
        raise OSError("Could not save custom-check-r.png")

    window.close()
    app.processEvents()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
