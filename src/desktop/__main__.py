"""Launch the maintained PySide6 desktop shell with ``python -m src.desktop``."""

from .main_window import launch_desktop_application


def main(argv: list[str] | None = None) -> int:
    """Dispatch the module entrypoint to the maintained desktop launcher."""

    return launch_desktop_application(argv)


if __name__ == "__main__":
    raise SystemExit(main())
