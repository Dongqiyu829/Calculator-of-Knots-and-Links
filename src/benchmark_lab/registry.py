"""Registry reader and validator for the independent benchmark lab."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.braid.braid_word import BraidWord


CSV_HEADERS = (
    "pair_id",
    "group",
    "label_A",
    "label_B",
    "source_A",
    "source_B",
    "num_strands_A",
    "generators_A",
    "num_strands_B",
    "generators_B",
    "same_jones",
    "same_alexander_or_conway",
    "mutant",
    "status_of_braid_source",
    "expected_sl2_fundamental",
    "expected_sl2_3d_9x9",
    "expected_sl3_fundamental",
    "expected_profile",
    "priority",
    "notes",
)
ALLOWED_YES_NO = {"yes", "no", "unknown", ""}
ALLOWED_RELATIONS = {"same", "different", "skipped", "unknown", ""}
ALLOWED_SOURCE_STATUS = {"safe", "needs_audit", "missing", ""}


class RegistryError(ValueError):
    """Raised when benchmark-lab registry data is malformed."""


@dataclass(frozen=True, slots=True)
class BenchmarkBraidSide:
    """Store one side of a benchmark pair."""

    label: str
    source: str
    num_strands: int
    generators: tuple[int, ...]

    @property
    def is_placeholder(self) -> bool:
        return self.num_strands <= 0

    def to_braid_word(self) -> BraidWord | None:
        if self.is_placeholder:
            return None
        return BraidWord.from_iterable(
            self.num_strands,
            self.generators,
            label=self.label,
            notes=self.source,
            metadata={"source": self.source},
        )

    def writhe(self) -> int | None:
        braid_word = self.to_braid_word()
        return None if braid_word is None else braid_word.writhe()

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "source": self.source,
            "num_strands": self.num_strands,
            "generators": list(self.generators),
            "is_placeholder": self.is_placeholder,
            "writhe": self.writhe(),
        }


@dataclass(frozen=True, slots=True)
class BenchmarkPairDefinition:
    """Store one benchmark pair entry loaded by the benchmark lab."""

    pair_id: str
    group: str
    braid_a: BenchmarkBraidSide
    braid_b: BenchmarkBraidSide
    same_jones: str
    same_alexander_or_conway: str
    mutant: str
    status_of_braid_source: str
    expected_sl2_fundamental: str
    expected_sl2_3d_9x9: str
    expected_sl3_fundamental: str
    expected_profile: str
    priority: str
    notes: str = ""
    warnings: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def expected_relations(self) -> dict[str, str]:
        return {
            "sl2_fundamental": self.expected_sl2_fundamental,
            "sl2_3d_9x9": self.expected_sl2_3d_9x9,
            "sl3_fundamental": self.expected_sl3_fundamental,
        }

    @property
    def skip_reason(self) -> str | None:
        if self.status_of_braid_source == "needs_audit":
            return "needs_audit"
        if self.braid_a.is_placeholder or self.braid_b.is_placeholder:
            return "missing_braid"
        return None

    @property
    def should_skip(self) -> bool:
        return self.skip_reason is not None

    def to_dict(self) -> dict[str, Any]:
        return {
            "pair_id": self.pair_id,
            "group": self.group,
            "braid_a": self.braid_a.to_dict(),
            "braid_b": self.braid_b.to_dict(),
            "same_jones": self.same_jones,
            "same_alexander_or_conway": self.same_alexander_or_conway,
            "mutant": self.mutant,
            "status_of_braid_source": self.status_of_braid_source,
            "expected_sl2_fundamental": self.expected_sl2_fundamental,
            "expected_sl2_3d_9x9": self.expected_sl2_3d_9x9,
            "expected_sl3_fundamental": self.expected_sl3_fundamental,
            "expected_profile": self.expected_profile,
            "priority": self.priority,
            "notes": self.notes,
            "warnings": list(self.warnings),
            "metadata": dict(self.metadata),
            "should_skip": self.should_skip,
            "skip_reason": self.skip_reason,
        }


def safe_parse_generators(raw_value: Any) -> tuple[int, ...]:
    """Safely parse generator data from CSV/JSON into tuple[int, ...]."""

    if raw_value is None:
        return ()
    if isinstance(raw_value, tuple):
        raw_value = list(raw_value)
    if isinstance(raw_value, list):
        normalized: list[int] = []
        for item in raw_value:
            if not isinstance(item, int):
                raise RegistryError(f"Generator entry {item!r} is not an integer.")
            normalized.append(item)
        return tuple(normalized)
    if isinstance(raw_value, int):
        return (raw_value,)
    if not isinstance(raw_value, str):
        raise RegistryError(f"Unsupported generator field type: {type(raw_value)!r}")

    cleaned = raw_value.strip()
    if not cleaned or cleaned in {"[]", "()"}:
        return ()
    if cleaned.startswith("[") and cleaned.endswith("]"):
        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise RegistryError(f"Invalid generator JSON list: {raw_value!r}") from exc
        return safe_parse_generators(parsed)

    tokens = cleaned.replace(",", " ").split()
    try:
        return tuple(int(token) for token in tokens)
    except ValueError as exc:
        raise RegistryError(f"Invalid generator token in {raw_value!r}") from exc


def load_registry(input_path: str | Path) -> tuple[BenchmarkPairDefinition, ...]:
    """Load the benchmark-lab registry from CSV or JSON."""

    path = Path(input_path)
    if path.suffix.lower() == ".csv":
        return load_registry_csv(path)
    if path.suffix.lower() == ".json":
        return load_registry_json(path)
    raise RegistryError(f"Unsupported input format: {path.suffix}")


def load_registry_csv(path: str | Path) -> tuple[BenchmarkPairDefinition, ...]:
    input_path = Path(path)
    with input_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise RegistryError(f"CSV file {input_path} is missing a header row.")
        if tuple(reader.fieldnames) != CSV_HEADERS:
            raise RegistryError("CSV header mismatch for benchmark lab template.")
        return tuple(_normalize_row(row, row_index=index + 2, source_name=str(input_path)) for index, row in enumerate(reader))


def load_registry_json(path: str | Path) -> tuple[BenchmarkPairDefinition, ...]:
    input_path = Path(path)
    with input_path.open("r", encoding="utf-8") as handle:
        try:
            payload = json.load(handle)
        except json.JSONDecodeError as exc:
            raise RegistryError(f"Invalid JSON in {input_path}: {exc}") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("benchmarks"), list):
        raise RegistryError("Benchmark JSON must contain top-level key 'benchmarks' with an array value.")
    return tuple(
        _normalize_row(item, row_index=index + 1, source_name=str(input_path))
        for index, item in enumerate(payload["benchmarks"])
    )


def find_pair_by_id(pairs: tuple[BenchmarkPairDefinition, ...] | list[BenchmarkPairDefinition], pair_id: str) -> BenchmarkPairDefinition:
    """Find one benchmark pair by stable id."""

    for pair in pairs:
        if pair.pair_id == pair_id:
            return pair
    raise RegistryError(f"Unknown benchmark pair id: {pair_id}")


def _normalize_row(raw_row: dict[str, Any], *, row_index: int, source_name: str) -> BenchmarkPairDefinition:
    if not isinstance(raw_row, dict):
        raise RegistryError(f"Row {row_index} in {source_name} is not an object.")

    warnings: list[str] = []
    pair_id = _required_text(raw_row, "pair_id", row_index=row_index, source_name=source_name)
    group = _required_text(raw_row, "group", row_index=row_index, source_name=source_name)
    source_status = _normalized_choice(
        raw_row.get("status_of_braid_source", ""),
        allowed=ALLOWED_SOURCE_STATUS,
        field_name="status_of_braid_source",
        row_index=row_index,
        source_name=source_name,
    )
    braid_a = _normalize_side(raw_row, suffix="A", row_index=row_index, source_name=source_name)
    braid_b = _normalize_side(raw_row, suffix="B", row_index=row_index, source_name=source_name)

    if braid_a.is_placeholder or braid_b.is_placeholder:
        warnings.append("Missing braid data detected; this pair will be skipped by the lab runner.")
    if source_status == "needs_audit":
        warnings.append("status_of_braid_source=needs_audit; the lab runner must warn and skip evaluation.")

    return BenchmarkPairDefinition(
        pair_id=pair_id,
        group=group,
        braid_a=braid_a,
        braid_b=braid_b,
        same_jones=_normalized_choice(raw_row.get("same_jones", ""), allowed=ALLOWED_YES_NO, field_name="same_jones", row_index=row_index, source_name=source_name),
        same_alexander_or_conway=_normalized_choice(raw_row.get("same_alexander_or_conway", ""), allowed=ALLOWED_YES_NO, field_name="same_alexander_or_conway", row_index=row_index, source_name=source_name),
        mutant=_normalized_choice(raw_row.get("mutant", ""), allowed=ALLOWED_YES_NO, field_name="mutant", row_index=row_index, source_name=source_name),
        status_of_braid_source=source_status,
        expected_sl2_fundamental=_normalized_choice(raw_row.get("expected_sl2_fundamental", ""), allowed=ALLOWED_RELATIONS, field_name="expected_sl2_fundamental", row_index=row_index, source_name=source_name),
        expected_sl2_3d_9x9=_normalized_choice(raw_row.get("expected_sl2_3d_9x9", ""), allowed=ALLOWED_RELATIONS, field_name="expected_sl2_3d_9x9", row_index=row_index, source_name=source_name),
        expected_sl3_fundamental=_normalized_choice(raw_row.get("expected_sl3_fundamental", ""), allowed=ALLOWED_RELATIONS, field_name="expected_sl3_fundamental", row_index=row_index, source_name=source_name),
        expected_profile=str(raw_row.get("expected_profile", "")).strip(),
        priority=str(raw_row.get("priority", "")).strip(),
        notes=str(raw_row.get("notes", "")).strip(),
        warnings=tuple(warnings),
        metadata={"row_index": row_index, "source_name": source_name},
    )


def _normalize_side(raw_row: dict[str, Any], *, suffix: str, row_index: int, source_name: str) -> BenchmarkBraidSide:
    label = _required_text(raw_row, f"label_{suffix}", row_index=row_index, source_name=source_name)
    source = _required_text(raw_row, f"source_{suffix}", row_index=row_index, source_name=source_name)
    num_strands = _parse_int(raw_row.get(f"num_strands_{suffix}", 0), field_name=f"num_strands_{suffix}", row_index=row_index, source_name=source_name)
    generators = safe_parse_generators(raw_row.get(f"generators_{suffix}", []))

    if num_strands <= 0:
        if generators:
            raise RegistryError(
                f"Row {row_index} in {source_name} has placeholder num_strands_{suffix} <= 0 but non-empty generators_{suffix}."
            )
        return BenchmarkBraidSide(label=label, source=source, num_strands=0, generators=())

    try:
        BraidWord.from_iterable(num_strands, generators, label=label, notes=source)
    except ValueError as exc:
        raise RegistryError(f"Invalid braid data for side {suffix} in row {row_index} of {source_name}: {exc}") from exc
    return BenchmarkBraidSide(label=label, source=source, num_strands=num_strands, generators=generators)


def _required_text(raw_row: dict[str, Any], field_name: str, *, row_index: int, source_name: str) -> str:
    value = raw_row.get(field_name, "")
    if not isinstance(value, str):
        value = str(value)
    cleaned = value.strip()
    if not cleaned:
        raise RegistryError(f"Missing required field {field_name!r} in row {row_index} of {source_name}.")
    return cleaned


def _parse_int(raw_value: Any, *, field_name: str, row_index: int, source_name: str) -> int:
    if isinstance(raw_value, bool):
        raise RegistryError(f"Field {field_name!r} in row {row_index} of {source_name} must be an integer.")
    if isinstance(raw_value, int):
        return raw_value
    if isinstance(raw_value, str):
        cleaned = raw_value.strip()
        if not cleaned:
            return 0
        try:
            return int(cleaned)
        except ValueError as exc:
            raise RegistryError(f"Field {field_name!r} in row {row_index} of {source_name} must be an integer.") from exc
    raise RegistryError(f"Field {field_name!r} in row {row_index} of {source_name} must be an integer.")


def _normalized_choice(raw_value: Any, *, allowed: set[str], field_name: str, row_index: int, source_name: str) -> str:
    cleaned = str(raw_value).strip().lower()
    if cleaned not in allowed:
        raise RegistryError(
            f"Field {field_name!r} in row {row_index} of {source_name} must be one of {sorted(allowed)}. Got: {raw_value!r}"
        )
    return cleaned
