"""Summary and export helpers for benchmark experiment runs."""

from __future__ import annotations

import csv
import io
import json
from collections import Counter
from dataclasses import dataclass
from typing import Any

from src.experiments.profile_runner import BenchmarkPairResult


SUMMARY_PROFILE_ORDER = ("(0,0,0)", "(1,1,1)", "(0,1,1)", "(0,0,1)", "(0,1,0)")
SUMMARY_MATCH_ORDER = ("yes", "no", "partial")


@dataclass(frozen=True, slots=True)
class SummaryRow:
    """Store one summary metric row."""

    category: str
    label: str
    count: int

    def to_dict(self) -> dict[str, Any]:
        return {"category": self.category, "label": self.label, "count": self.count}


@dataclass(frozen=True, slots=True)
class BenchmarkSummaryReport:
    """Store profile counts and expected-match counts for a benchmark run."""

    q_mode: str
    total_pairs: int
    rows: tuple[SummaryRow, ...]
    profile_counts: dict[str, int]
    skipped_count: int
    match_expected_counts: dict[str, int]

    def to_rows(self) -> list[dict[str, Any]]:
        return [row.to_dict() for row in self.rows]

    def to_csv_text(self) -> str:
        rows = self.to_rows()
        if not rows:
            return ""
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
        return buffer.getvalue()

    def to_json_text(self) -> str:
        return json.dumps(
            {
                "q_mode": self.q_mode,
                "total_pairs": self.total_pairs,
                "profile_counts": dict(self.profile_counts),
                "skipped": self.skipped_count,
                "match_expected": dict(self.match_expected_counts),
                "rows": self.to_rows(),
            },
            indent=2,
            ensure_ascii=False,
        )

    def to_markdown_text(self) -> str:
        rows = self.to_rows()
        if not rows:
            return "No rows."
        headers = list(rows[0])
        lines = [
            "| " + " | ".join(headers) + " |",
            "| " + " | ".join("---" for _ in headers) + " |",
        ]
        for row in rows:
            lines.append("| " + " | ".join(_markdown_escape(row[header]) for header in headers) + " |")
        return "\n".join(lines)


def build_benchmark_summary(pair_results: tuple[BenchmarkPairResult, ...] | list[BenchmarkPairResult], *, q_mode: str) -> BenchmarkSummaryReport:
    """Build the summary report for a benchmark experiment run."""

    profile_counter = Counter(
        result.observed_profile
        for result in pair_results
        if result.observed_profile != "skipped"
    )
    skipped_count = sum(1 for result in pair_results if result.status == "skipped")
    match_counter = Counter(result.match_expected for result in pair_results)

    rows: list[SummaryRow] = []
    for profile in SUMMARY_PROFILE_ORDER:
        rows.append(SummaryRow(category="profile", label=profile, count=profile_counter.get(profile, 0)))
    extra_profiles = sorted(profile for profile in profile_counter if profile not in SUMMARY_PROFILE_ORDER)
    for profile in extra_profiles:
        rows.append(SummaryRow(category="profile", label=profile, count=profile_counter[profile]))
    rows.append(SummaryRow(category="status", label="skipped", count=skipped_count))
    for label in SUMMARY_MATCH_ORDER:
        rows.append(SummaryRow(category="match_expected", label=label, count=match_counter.get(label, 0)))

    return BenchmarkSummaryReport(
        q_mode=q_mode,
        total_pairs=len(pair_results),
        rows=tuple(rows),
        profile_counts={profile: profile_counter.get(profile, 0) for profile in SUMMARY_PROFILE_ORDER + tuple(extra_profiles)},
        skipped_count=skipped_count,
        match_expected_counts={label: match_counter.get(label, 0) for label in SUMMARY_MATCH_ORDER},
    )


def _markdown_escape(value: Any) -> str:
    return str(value).replace("|", "\\|")
