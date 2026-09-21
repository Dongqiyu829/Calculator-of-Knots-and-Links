from __future__ import annotations

import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
BUNDLE_DIR = ROOT / "report_bundle"
ZIP_PATH = ROOT / "report_bundle.zip"


def copy_path(source: Path, destination: Path) -> str | None:
    if not source.exists():
        return f"missing: {source.relative_to(ROOT).as_posix()}"
    if source.is_dir():
        shutil.copytree(source, destination)
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    return None


def detect_git_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return "unavailable (not a git repository)"
    return result.stdout.strip() or "unavailable (empty git output)"


def write_version_file(bundle_dir: Path) -> None:
    created_at = datetime.now(timezone.utc).isoformat()
    commit_hash = detect_git_commit()
    lines = [
        f"date_created_utc: {created_at}",
        f"git_commit: {commit_hash}",
        "note: snapshot prepared for UROP report submission",
    ]
    (bundle_dir / "VERSION.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_zip(bundle_dir: Path, zip_path: Path) -> None:
    if zip_path.exists():
        zip_path.unlink()
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as archive:
        for path in sorted(bundle_dir.rglob("*")):
            arcname = Path("report_bundle") / path.relative_to(bundle_dir)
            archive.write(path, arcname)


def main() -> None:
    if BUNDLE_DIR.exists():
        shutil.rmtree(BUNDLE_DIR)
    BUNDLE_DIR.mkdir(parents=True)

    bundle_targets = [
        (ROOT / "README.md", BUNDLE_DIR / "README.md"),
        (ROOT / "LICENSE", BUNDLE_DIR / "LICENSE"),
        (ROOT / "docs" / "report_appendix.md", BUNDLE_DIR / "docs" / "report_appendix.md"),
        (ROOT / "docs" / "reproducibility.md", BUNDLE_DIR / "docs" / "reproducibility.md"),
        (ROOT / "docs" / "benchmark_summary.md", BUNDLE_DIR / "docs" / "benchmark_summary.md"),
        (ROOT / "docs" / "github_release_checklist.md", BUNDLE_DIR / "docs" / "github_release_checklist.md"),
        (ROOT / "docs" / "benchmark_lab", BUNDLE_DIR / "docs" / "benchmark_lab"),
        (ROOT / "data" / "benchmark_lab", BUNDLE_DIR / "data" / "benchmark_lab"),
        (ROOT / "examples" / "benchmark_lab", BUNDLE_DIR / "examples" / "benchmark_lab"),
        (ROOT / "src" / "benchmark_lab", BUNDLE_DIR / "src" / "benchmark_lab"),
        (ROOT / "artifacts" / "benchmark_lab", BUNDLE_DIR / "artifacts" / "benchmark_lab"),
    ]

    missing_items: list[str] = []
    for source, destination in bundle_targets:
        missing = copy_path(source, destination)
        if missing is not None:
            missing_items.append(missing)

    write_version_file(BUNDLE_DIR)
    build_zip(BUNDLE_DIR, ZIP_PATH)

    print(f"Created bundle directory: {BUNDLE_DIR}")
    print(f"Created bundle zip: {ZIP_PATH}")
    if missing_items:
        print("Missing optional items:")
        for item in missing_items:
            print(f"- {item}")
    else:
        print("All requested bundle items were copied.")


if __name__ == "__main__":
    main()