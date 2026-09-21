"""Profile-summary helpers for the independent benchmark lab."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any

from .profile_runner import PairResultRecord


PROFILE_BUCKETS = ("(0,0,0)", "(1,1,1)", "(0,1,1)", "(0,0,1)", "(0,1,0)")
MATCH_BUCKETS = ("yes", "no", "partial")


@dataclass(frozen=True, slots=True)
class SummaryRow:
    """Store one benchmark-lab summary row."""

    category: str
    label: str
    count: int

    def to_dict(self) -> dict[str, Any]:
        return {"category": self.category, "label": self.label, "count": self.count}


@dataclass(frozen=True, slots=True)
class ProfileSummaryReport:
    """Store summary counts for a benchmark-lab run."""

    q_mode: str
    total_pairs: int
    rows: tuple[SummaryRow, ...]
    profile_counts: dict[str, int]
    skipped_count: int
    match_expected_counts: dict[str, int]

    def to_rows(self) -> list[dict[str, Any]]:
        return [row.to_dict() for row in self.rows]

    def to_dict(self) -> dict[str, Any]:
        return {
            "q_mode": self.q_mode,
            "total_pairs": self.total_pairs,
            "profile_counts": dict(self.profile_counts),
            "skipped": self.skipped_count,
            "match_expected": dict(self.match_expected_counts),
            "rows": self.to_rows(),
        }


def build_profile_summary(pair_results: tuple[PairResultRecord, ...] | list[PairResultRecord], *, q_mode: str) -> ProfileSummaryReport:
    """Build the summary view for the benchmark-lab profile run."""

    profile_counter = Counter(result.observed_profile for result in pair_results if result.observed_profile != "skipped")
    skipped_count = sum(1 for result in pair_results if result.status == "skipped")
    match_counter = Counter(result.match_expected for result in pair_results)

    rows: list[SummaryRow] = []
    for profile in PROFILE_BUCKETS:
        rows.append(SummaryRow(category="profile", label=profile, count=profile_counter.get(profile, 0)))
    extra_profiles = sorted(profile for profile in profile_counter if profile not in PROFILE_BUCKETS)
    for profile in extra_profiles:
        rows.append(SummaryRow(category="profile", label=profile, count=profile_counter[profile]))
    rows.append(SummaryRow(category="status", label="skipped", count=skipped_count))
    for bucket in MATCH_BUCKETS:
        rows.append(SummaryRow(category="match_expected", label=bucket, count=match_counter.get(bucket, 0)))

    return ProfileSummaryReport(
        q_mode=q_mode,
        total_pairs=len(pair_results),
        rows=tuple(rows),
        profile_counts={profile: profile_counter.get(profile, 0) for profile in PROFILE_BUCKETS + tuple(extra_profiles)},
        skipped_count=skipped_count,
        match_expected_counts={bucket: match_counter.get(bucket, 0) for bucket in MATCH_BUCKETS},
    )
