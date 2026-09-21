"""Experiment-log data structures and export helpers for the braid workbench."""

from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .comparison import WorkbenchPairComparisonResult
from .runner import WorkbenchBatchRunResult


EXPERIMENT_LOG_FIELD_NAMES = (
    "record_id",
    "timestamp",
    "label",
    "input_source",
    "braid_a_num_strands",
    "braid_a_generators",
    "braid_a_word",
    "braid_b_num_strands",
    "braid_b_generators",
    "braid_b_word",
    "sl2_jones_output_a",
    "sl2_jones_output_b",
    "sl2_jones_same",
    "sl2_3d_output_a",
    "sl2_3d_output_b",
    "sl2_3d_same",
    "sl3_output_a",
    "sl3_output_b",
    "sl3_same",
    "classification",
    "notes",
)


@dataclass(frozen=True, slots=True)
class ExperimentLogRecord:
    """Store one exported comparison record for later analysis."""

    record_id: str
    timestamp: str
    label: str
    input_source: str
    braid_a_num_strands: int
    braid_a_generators: tuple[int, ...]
    braid_a_word: str
    braid_b_num_strands: int
    braid_b_generators: tuple[int, ...]
    braid_b_word: str
    sl2_jones_output_a: str
    sl2_jones_output_b: str
    sl2_jones_same: bool
    sl2_3d_output_a: str
    sl2_3d_output_b: str
    sl2_3d_same: bool
    sl3_output_a: str
    sl3_output_b: str
    sl3_same: bool
    classification: str
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "timestamp": self.timestamp,
            "label": self.label,
            "input_source": self.input_source,
            "braid_a_num_strands": self.braid_a_num_strands,
            "braid_a_generators": list(self.braid_a_generators),
            "braid_a_word": self.braid_a_word,
            "braid_b_num_strands": self.braid_b_num_strands,
            "braid_b_generators": list(self.braid_b_generators),
            "braid_b_word": self.braid_b_word,
            "sl2_jones_output_a": self.sl2_jones_output_a,
            "sl2_jones_output_b": self.sl2_jones_output_b,
            "sl2_jones_same": self.sl2_jones_same,
            "sl2_3d_output_a": self.sl2_3d_output_a,
            "sl2_3d_output_b": self.sl2_3d_output_b,
            "sl2_3d_same": self.sl2_3d_same,
            "sl3_output_a": self.sl3_output_a,
            "sl3_output_b": self.sl3_output_b,
            "sl3_same": self.sl3_same,
            "classification": self.classification,
            "notes": self.notes,
        }

    def to_csv_row(self) -> dict[str, str]:
        data = self.to_dict()
        return {
            **{key: str(value) for key, value in data.items() if key not in {"braid_a_generators", "braid_b_generators"}},
            "braid_a_generators": json.dumps(data["braid_a_generators"], ensure_ascii=False),
            "braid_b_generators": json.dumps(data["braid_b_generators"], ensure_ascii=False),
        }


@dataclass(slots=True)
class ExperimentLog:
    """Mutable in-memory experiment log with GUI-friendly export helpers."""

    records: list[ExperimentLogRecord] = field(default_factory=list)

    def _next_record_id(self) -> str:
        return f"exp-{len(self.records) + 1:04d}"

    def add_comparison_result(
        self,
        comparison_result: WorkbenchPairComparisonResult,
        *,
        label: str = "",
        notes: str = "",
        input_source: str = "manual",
        timestamp: datetime | None = None,
    ) -> ExperimentLogRecord:
        """Append one pair-comparison result as a persistent log record."""

        moment = datetime.now() if timestamp is None else timestamp
        record = ExperimentLogRecord(
            record_id=self._next_record_id(),
            timestamp=moment.isoformat(timespec="seconds"),
            label=label or comparison_result.label,
            input_source=input_source,
            braid_a_num_strands=comparison_result.braid_a.num_strands,
            braid_a_generators=comparison_result.braid_a.generators,
            braid_a_word=comparison_result.braid_a.word_string(),
            braid_b_num_strands=comparison_result.braid_b.num_strands,
            braid_b_generators=comparison_result.braid_b.generators,
            braid_b_word=comparison_result.braid_b.word_string(),
            sl2_jones_output_a=str(comparison_result.jones_output_a),
            sl2_jones_output_b=str(comparison_result.jones_output_b),
            sl2_jones_same=comparison_result.jones_same,
            sl2_3d_output_a=str(comparison_result.sl2_3d_output_a),
            sl2_3d_output_b=str(comparison_result.sl2_3d_output_b),
            sl2_3d_same=comparison_result.sl2_3d_same,
            sl3_output_a=str(comparison_result.sl3_output_a),
            sl3_output_b=str(comparison_result.sl3_output_b),
            sl3_same=comparison_result.sl3_same,
            classification=comparison_result.classification,
            notes=notes or comparison_result.notes,
        )
        self.records.append(record)
        return record

    def add_batch_run_result(
        self,
        run_result: WorkbenchBatchRunResult,
        *,
        notes: str = "",
        timestamp: datetime | None = None,
    ) -> list[ExperimentLogRecord]:
        """Append all pairwise rows from one unified workbench run result."""

        moment = datetime.now() if timestamp is None else timestamp
        single_rows_by_label = {row.label: row for row in run_result.single_rows}
        records: list[ExperimentLogRecord] = []
        for pair_row in run_result.pairwise_rows:
            braid_a_row = single_rows_by_label[pair_row.braid_a]
            braid_b_row = single_rows_by_label[pair_row.braid_b]
            record = ExperimentLogRecord(
                record_id=self._next_record_id(),
                timestamp=moment.isoformat(timespec="seconds"),
                label=pair_row.pair_label,
                input_source=run_result.run_spec.input_source,
                braid_a_num_strands=braid_a_row.num_strands,
                braid_a_generators=braid_a_row.generators,
                braid_a_word=" ".join(str(generator) for generator in braid_a_row.generators) if braid_a_row.generators else "identity",
                braid_b_num_strands=braid_b_row.num_strands,
                braid_b_generators=braid_b_row.generators,
                braid_b_word=" ".join(str(generator) for generator in braid_b_row.generators) if braid_b_row.generators else "identity",
                sl2_jones_output_a=braid_a_row.sl2_fundamental_output,
                sl2_jones_output_b=braid_b_row.sl2_fundamental_output,
                sl2_jones_same=pair_row.sl2_fundamental_same == "same",
                sl2_3d_output_a=braid_a_row.sl2_3d_9x9_output,
                sl2_3d_output_b=braid_b_row.sl2_3d_9x9_output,
                sl2_3d_same=pair_row.sl2_3d_9x9_same == "same",
                sl3_output_a=braid_a_row.sl3_fundamental_output,
                sl3_output_b=braid_b_row.sl3_fundamental_output,
                sl3_same=pair_row.sl3_fundamental_same == "same",
                classification=pair_row.classification,
                notes=notes,
            )
            self.records.append(record)
            records.append(record)
        return records

    def clear(self) -> None:
        self.records.clear()

    def get_record(self, record_id: str) -> ExperimentLogRecord | None:
        for record in self.records:
            if record.record_id == record_id:
                return record
        return None

    def filter_records(
        self,
        *,
        label_query: str = "",
        classification: str = "",
        input_source: str = "",
        sl2_jones_same: bool | None = None,
        sl2_3d_same: bool | None = None,
        sl3_same: bool | None = None,
    ) -> list[ExperimentLogRecord]:
        filtered: list[ExperimentLogRecord] = []
        normalized_query = label_query.strip().casefold()
        normalized_classification = classification.strip()
        normalized_input_source = input_source.strip()
        for record in self.records:
            if normalized_query and normalized_query not in record.label.casefold() and normalized_query not in record.notes.casefold():
                continue
            if normalized_classification and record.classification != normalized_classification:
                continue
            if normalized_input_source and record.input_source != normalized_input_source:
                continue
            if sl2_jones_same is not None and record.sl2_jones_same != sl2_jones_same:
                continue
            if sl2_3d_same is not None and record.sl2_3d_same != sl2_3d_same:
                continue
            if sl3_same is not None and record.sl3_same != sl3_same:
                continue
            filtered.append(record)
        return filtered

    def to_dict(self, records: list[ExperimentLogRecord] | None = None) -> dict[str, Any]:
        record_list = self.records if records is None else records
        return {
            "record_count": len(record_list),
            "records": [record.to_dict() for record in record_list],
        }

    def to_json_text(self, records: list[ExperimentLogRecord] | None = None) -> str:
        return json.dumps(self.to_dict(records), indent=2, ensure_ascii=False)

    def to_csv_text(self, records: list[ExperimentLogRecord] | None = None) -> str:
        record_list = self.records if records is None else records
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=list(EXPERIMENT_LOG_FIELD_NAMES))
        writer.writeheader()
        for record in record_list:
            writer.writerow(record.to_csv_row())
        return buffer.getvalue()

    def to_markdown_table(self, records: list[ExperimentLogRecord] | None = None) -> str:
        record_list = self.records if records is None else records
        if not record_list:
            return "No experiment records."

        headers = [
            "record_id",
            "timestamp",
            "label",
            "input_source",
            "classification",
            "sl2_jones_same",
            "sl2_3d_same",
            "sl3_same",
            "braid_a_word",
            "braid_b_word",
        ]
        lines = [
            "| " + " | ".join(headers) + " |",
            "| " + " | ".join("---" for _ in headers) + " |",
        ]
        for record in record_list:
            lines.append(
                "| " + " | ".join(
                    str(
                        getattr(record, header)
                    ).replace("\n", " ")
                    for header in headers
                ) + " |"
            )
        return "\n".join(lines)
