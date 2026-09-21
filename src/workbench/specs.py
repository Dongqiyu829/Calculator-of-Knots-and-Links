"""Unified input specifications for the ordinary braid workbench."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

import sympy as sp

from src.braid.braid_word import BraidWord
from src.services import (
    BraidInputValidationError,
    DEFAULT_EVALUATION_MODEL_IDS,
    EvaluationBranchDescriptor,
    UnknownEvaluationModelError,
    branch_ids_for_models,
    get_evaluation_model,
    list_evaluation_branches,
)


WORKBENCH_COMPARISON_MODES = ("single", "pairwise", "all")
WORKBENCH_ALLOWED_INPUT_SOURCES = ("manual", "json")
WORKBENCH_DEFAULT_MODELS = DEFAULT_EVALUATION_MODEL_IDS
AI_JSON_TEMPLATE = json.dumps(
    {
        "q_parameter": "q",
        "models": [
            "sl2_fundamental",
            "sl2_3d_9x9",
            "sl3_fundamental",
        ],
        "comparison_mode": "pairwise",
        "braids": [
            {
                "label": "A",
                "num_strands": 3,
                "generators": [1, 2, 1],
                "notes": "optional",
            },
            {
                "label": "B",
                "num_strands": 3,
                "generators": [2, 1, 2],
                "notes": "optional",
            },
        ],
    },
    indent=2,
    ensure_ascii=False,
)


WorkbenchModelSpec = EvaluationBranchDescriptor
WORKBENCH_MODEL_SPECS = {descriptor.model_id: descriptor for descriptor in list_evaluation_branches()}


@dataclass(frozen=True, slots=True)
class WorkbenchBraidSpec:
    label: str
    num_strands: int
    generators: tuple[int, ...]
    notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_braid_word(self) -> BraidWord:
        return BraidWord.from_iterable(
            num_strands=self.num_strands,
            generators=self.generators,
            label=self.label,
            notes=self.notes,
            metadata=dict(self.metadata),
        )


@dataclass(frozen=True, slots=True)
class BraidBatchSpec:
    braids: tuple[WorkbenchBraidSpec, ...]


@dataclass(frozen=True, slots=True)
class WorkbenchInputSpec:
    input_source: str
    q_parameter: Any
    models: tuple[str, ...]
    comparison_mode: str
    batch: BraidBatchSpec
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ComparisonRunSpec:
    input_source: str
    q_parameter_expr: sp.Expr
    q_parameter_text: str
    models: tuple[str, ...]
    comparison_mode: str
    batch: BraidBatchSpec
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def branch_ids(self) -> tuple[str, ...]:
        return branch_ids_for_models(self.models)


class WorkbenchInputValidationError(BraidInputValidationError):
    """Raised when manual or JSON workbench input fails validation."""


def get_workbench_model_ids() -> tuple[str, ...]:
    return tuple(WORKBENCH_MODEL_SPECS)


def get_workbench_model_descriptions() -> tuple[str, ...]:
    return tuple(
        f"{model_id} -> {spec.display_name} ({spec.branch_note})"
        for model_id, spec in WORKBENCH_MODEL_SPECS.items()
    )


def parse_workbench_q_parameter_value(parameter_value: Any) -> tuple[sp.Expr, str]:
    if isinstance(parameter_value, str):
        cleaned = parameter_value.strip()
        if not cleaned:
            raise WorkbenchInputValidationError("q_parameter cannot be empty.")
        try:
            return sp.sympify(cleaned), cleaned
        except Exception as exc:  # pragma: no cover - defensive parsing branch
            raise WorkbenchInputValidationError(f"Invalid q_parameter: {parameter_value}") from exc
    if isinstance(parameter_value, (int, float)):
        return sp.sympify(parameter_value), str(parameter_value)
    raise WorkbenchInputValidationError("q_parameter must be 'q', a numeric string, or a number.")


def _validate_models(models: tuple[str, ...]) -> tuple[str, ...]:
    if not models:
        raise WorkbenchInputValidationError("models must contain at least one allowed model id.")
    try:
        for model_id in models:
            get_evaluation_model(model_id)
    except UnknownEvaluationModelError as exc:
        raise WorkbenchInputValidationError(
            "Invalid model id(s): " + str(exc)
        ) from exc
    ordered_unique: list[str] = []
    for model_id in models:
        if model_id not in ordered_unique:
            ordered_unique.append(model_id)
    return tuple(ordered_unique)


def _validate_comparison_mode(comparison_mode: str) -> str:
    if comparison_mode not in WORKBENCH_COMPARISON_MODES:
        raise WorkbenchInputValidationError(
            f"comparison_mode must be one of {', '.join(WORKBENCH_COMPARISON_MODES)}. Got: {comparison_mode}"
        )
    return comparison_mode


def _validate_input_source(input_source: str) -> str:
    if input_source not in WORKBENCH_ALLOWED_INPUT_SOURCES:
        raise WorkbenchInputValidationError(
            f"input_source must be one of {', '.join(WORKBENCH_ALLOWED_INPUT_SOURCES)}. Got: {input_source}"
        )
    return input_source


def _normalize_generators(num_strands: int, generators: Any, *, braid_label: str) -> tuple[int, ...]:
    if not isinstance(generators, list):
        raise WorkbenchInputValidationError(f"Braid '{braid_label}' generators must be a JSON array of integers.")
    normalized: list[int] = []
    allowed = set(range(1, num_strands))
    for generator in generators:
        if not isinstance(generator, int):
            raise WorkbenchInputValidationError(f"Braid '{braid_label}' generator {generator!r} is not an integer.")
        if abs(generator) not in allowed:
            raise WorkbenchInputValidationError(
                f"Braid '{braid_label}' generator {generator} is out of range for num_strands={num_strands}."
            )
        normalized.append(generator)
    return tuple(normalized)


def normalize_braid_spec_data(raw_braid: dict[str, Any]) -> WorkbenchBraidSpec:
    label = raw_braid.get("label")
    num_strands = raw_braid.get("num_strands")
    generators = raw_braid.get("generators")
    notes = raw_braid.get("notes", "")

    if not isinstance(label, str) or not label.strip():
        raise WorkbenchInputValidationError("Each braid must have a non-empty string label.")
    if not isinstance(num_strands, int) or num_strands < 2:
        raise WorkbenchInputValidationError(f"Braid '{label}' num_strands must be an integer >= 2.")
    normalized_generators = _normalize_generators(num_strands, generators, braid_label=label)
    if notes is None:
        notes = ""
    if not isinstance(notes, str):
        raise WorkbenchInputValidationError(f"Braid '{label}' notes must be a string when provided.")

    return WorkbenchBraidSpec(
        label=label.strip(),
        num_strands=num_strands,
        generators=normalized_generators,
        notes=notes,
    )


def normalize_input_spec(input_spec: WorkbenchInputSpec) -> ComparisonRunSpec:
    input_source = _validate_input_source(input_spec.input_source)
    q_parameter_expr, q_parameter_text = parse_workbench_q_parameter_value(input_spec.q_parameter)
    models = _validate_models(tuple(input_spec.models))
    comparison_mode = _validate_comparison_mode(input_spec.comparison_mode)
    braids = tuple(input_spec.batch.braids)
    if not braids:
        raise WorkbenchInputValidationError("At least one braid is required.")
    if comparison_mode in {"pairwise", "all"} and len(braids) < 2:
        raise WorkbenchInputValidationError(
            f"comparison_mode '{comparison_mode}' requires at least two braids."
        )

    return ComparisonRunSpec(
        input_source=input_source,
        q_parameter_expr=q_parameter_expr,
        q_parameter_text=q_parameter_text,
        models=models,
        comparison_mode=comparison_mode,
        batch=BraidBatchSpec(tuple(braids)),
        metadata=dict(input_spec.metadata),
    )


def build_manual_input_spec(
    *,
    q_parameter: Any,
    models: tuple[str, ...] | list[str],
    comparison_mode: str,
    braids: tuple[WorkbenchBraidSpec, ...] | list[WorkbenchBraidSpec],
) -> WorkbenchInputSpec:
    return WorkbenchInputSpec(
        input_source="manual",
        q_parameter=q_parameter,
        models=tuple(models),
        comparison_mode=comparison_mode,
        batch=BraidBatchSpec(tuple(braids)),
    )


def parse_json_input_spec(json_text: str) -> WorkbenchInputSpec:
    try:
        payload = json.loads(json_text)
    except json.JSONDecodeError as exc:
        raise WorkbenchInputValidationError(f"Invalid JSON: {exc.msg} at line {exc.lineno}, column {exc.colno}.") from exc

    if not isinstance(payload, dict):
        raise WorkbenchInputValidationError("JSON input must be an object with q_parameter, models, comparison_mode, and braids.")

    missing = [key for key in ("q_parameter", "models", "comparison_mode", "braids") if key not in payload]
    if missing:
        raise WorkbenchInputValidationError("JSON input is missing required field(s): " + ", ".join(missing))

    models = payload["models"]
    if not isinstance(models, list) or not all(isinstance(item, str) for item in models):
        raise WorkbenchInputValidationError("models must be an array of allowed model id strings.")

    raw_braids = payload["braids"]
    if not isinstance(raw_braids, list):
        raise WorkbenchInputValidationError("braids must be an array of braid objects.")
    braids = tuple(normalize_braid_spec_data(raw_braid) for raw_braid in raw_braids)

    return WorkbenchInputSpec(
        input_source="json",
        q_parameter=payload["q_parameter"],
        models=tuple(models),
        comparison_mode=str(payload["comparison_mode"]),
        batch=BraidBatchSpec(braids),
        metadata={"raw_payload": payload},
    )
