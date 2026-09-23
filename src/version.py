"""Single maintained application version and release-tag validation helpers."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass


__version__ = "0.1.4"

_RELEASE_TAG_PATTERN = re.compile(r"^v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


class ReleaseTagError(ValueError):
    """Raised when a release tag is not a supported semantic-version tag."""


@dataclass(frozen=True, slots=True)
class ReleaseVersion:
    """Parsed ``vX.Y.Z`` release version."""

    major: int
    minor: int
    patch: int

    @property
    def version(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


def parse_release_tag(tag: str) -> ReleaseVersion:
    """Parse an exact ``vX.Y.Z`` tag without accepting a loose suffix."""

    if not isinstance(tag, str):
        raise ReleaseTagError("Release tag must be text in the form vX.Y.Z.")
    match = _RELEASE_TAG_PATTERN.fullmatch(tag.strip())
    if match is None:
        raise ReleaseTagError(f"Release tag {tag!r} must match vX.Y.Z.")
    return ReleaseVersion(*(int(value) for value in match.groups()))


def release_tag_matches_version(tag: str, expected_version: str = __version__) -> bool:
    """Return whether a release tag names the maintained application version."""

    parsed = parse_release_tag(tag)
    if not isinstance(expected_version, str) or not re.fullmatch(
        r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", expected_version
    ):
        raise ReleaseTagError("Expected application version must have the form X.Y.Z.")
    return parsed.version == expected_version


def validate_release_tag(tag: str, expected_version: str = __version__) -> ReleaseVersion:
    """Validate a tag and its equality with the maintained application version."""

    parsed = parse_release_tag(tag)
    if not release_tag_matches_version(tag, expected_version):
        raise ReleaseTagError(
            f"Release tag {tag!r} names {parsed.version}, but the maintained application version is {expected_version}."
        )
    return parsed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect the maintained application version.")
    parser.add_argument("--version", action="store_true", help="print the maintained application version")
    parser.add_argument("--check-tag", metavar="TAG", help="validate a vX.Y.Z tag against the maintained version")
    args = parser.parse_args(argv)
    if args.check_tag is not None:
        try:
            validate_release_tag(args.check_tag)
        except ReleaseTagError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        print(f"{args.check_tag} matches application version {__version__}")
        return 0
    print(__version__)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
