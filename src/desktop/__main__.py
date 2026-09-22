"""Launch the maintained PySide6 desktop shell with ``python -m src.desktop``."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from .main_window import launch_desktop_application


def main(argv: list[str] | None = None) -> int:
    """Dispatch the module entrypoint to the maintained desktop launcher."""

    arguments = list(sys.argv[1:] if argv is None else argv)
    if "--smoke-test" in arguments:
        return run_smoke_test()
    return launch_desktop_application(argv)


def run_smoke_test() -> int:
    """Construct the maintained window and exit without entering an event loop."""

    app = QApplication.instance() or QApplication([])
    from .main_window import DesktopMainWindow

    window = DesktopMainWindow()
    window.close()
    app.processEvents()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
