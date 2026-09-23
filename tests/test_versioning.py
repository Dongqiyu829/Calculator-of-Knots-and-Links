"""Focused tests for application version and release-tag machinery."""

from __future__ import annotations

import importlib.metadata
import os
import subprocess
import sys

import pytest

from src.version import (
    ReleaseTagError,
    __version__,
    parse_release_tag,
    release_tag_matches_version,
    validate_release_tag,
)


def test_single_application_version_is_exposed_by_source_and_package_metadata() -> None:
    assert __version__ == "0.1.2"
    assert importlib.metadata.version("calculator-of-knots-and-links") == __version__


def test_release_tag_parser_requires_exact_semantic_v_prefix() -> None:
    assert parse_release_tag("v0.1.2").version == "0.1.2"
    assert validate_release_tag("v0.1.2").version == __version__
    assert release_tag_matches_version("v0.1.2")
    assert not release_tag_matches_version("v0.1.1", expected_version=__version__)
    with pytest.raises(ReleaseTagError, match="vX.Y.Z"):
        parse_release_tag("0.1.0")
    with pytest.raises(ReleaseTagError, match="maintained application version"):
        validate_release_tag("v0.1.1")


def test_desktop_version_path_avoids_qt_and_full_window_construction() -> None:
    environment = dict(os.environ)
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys; from src.desktop.__main__ import main; "
                "assert main(['--version']) == 0; assert 'PySide6' not in sys.modules; "
                "assert 'src.services' not in sys.modules"
            ),
        ],
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout
    assert result.stdout.strip() == __version__
