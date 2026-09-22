"""Launch the maintained PySide6 desktop shell with ``python -m src.desktop``."""

from __future__ import annotations

import sys

from src.version import __version__


def main(argv: list[str] | None = None) -> int:
    """Dispatch the module entrypoint to the maintained desktop launcher."""

    arguments = list(sys.argv[1:] if argv is None else argv)
    if "--version" in arguments:
        print(__version__)
        return 0
    if "--smoke-test" in arguments:
        return run_smoke_test()
    return launch_desktop_application(argv)


def launch_desktop_application(argv: list[str] | None = None) -> int:
    """Import and dispatch the full UI only for normal interactive launches."""

    from .main_window import launch_desktop_application as launch

    return launch(argv)


def run_smoke_test() -> int:
    """Construct the maintained window and exit without entering an event loop."""

    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    from .main_window import DesktopMainWindow

    window = DesktopMainWindow()
    window.close()
    app.processEvents()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
