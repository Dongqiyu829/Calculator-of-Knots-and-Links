"""I/O helpers for the independent benchmark lab."""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Any


ARTIFACT_ROOT = Path("artifacts") / "benchmark_lab"


def ensure_profile_output_dir(input_path: str | Path, q_mode: str) -> Path:
    """Create the profile-run output directory under artifacts/benchmark_lab."""

    input_file = Path(input_path)
    output_dir = ARTIFACT_ROOT / f"{input_file.stem}_q_{_safe_label(q_mode)}"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def ensure_audit_output_dir(input_path: str | Path, q_mode: str) -> Path:
    """Create the audit-run output directory under artifacts/benchmark_lab."""

    return ensure_profile_output_dir(input_path, q_mode)


def rows_to_csv_text(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return ""
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def data_to_json_text(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)


def rows_to_markdown_text(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "No rows."
    headers = list(rows[0])
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(markdown_escape(row[header]) for header in headers) + " |")
    return "\n".join(lines)


def markdown_escape(value: Any) -> str:
    return str(value).replace("|", "\\|")


def write_text(path: str | Path, text: str) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")
    return output_path


def _safe_label(text: str) -> str:
    return text.replace("^", "pow").replace("-", "neg").replace("/", "div")
