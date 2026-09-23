"""Versioned, deterministic ``.knotcalc.json`` project documents.

Projects preserve calculation *setup*, not executable Python objects or trusted
results.  Validation goes through the same service parsers used by the
maintained workflows, so opening a file never evaluates an invariant or a
custom braid operator.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.version import __version__

from .braid_evaluation import build_catalog_braid_input, build_custom_braid_input, parse_q_text
from .branch_catalog import validate_branch_ids
from .custom_rmatrix import parse_custom_matrix, validate_custom_matrix
from .computation_backends import validate_computation_backend
from .errors import (
    ApplicationServiceError,
    ProjectFileError,
    ProjectSchemaError,
    ProjectValidationError,
    ProjectWorkflowError,
)


PROJECT_SCHEMA_VERSION = 1
PROJECT_APPLICATION = "Calculator of Knots and Links"
INVARIANT_WORKFLOW = "invariant"
CUSTOM_RMATRIX_WORKFLOW = "custom_rmatrix"
SUPPORTED_PROJECT_WORKFLOWS = (INVARIANT_WORKFLOW, CUSTOM_RMATRIX_WORKFLOW)


@dataclass(frozen=True, slots=True)
class ApplicationProjectDocument:
    """Validated frontend-neutral project setup."""

    workflow: str
    input_data: dict[str, Any]
    ui_state: dict[str, Any] = field(default_factory=dict)
    schema_version: int = PROJECT_SCHEMA_VERSION
    application: str = PROJECT_APPLICATION
    application_version: str = __version__

    @property
    def application_version_mismatch(self) -> bool:
        return self.application_version != __version__

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "application": self.application,
            "application_version": self.application_version,
            "workflow": self.workflow,
            "input": dict(self.input_data),
            "ui_state": dict(self.ui_state),
        }

    def to_json(self) -> str:
        """Return the canonical deterministic JSON representation."""

        return serialize_project(self)

    @classmethod
    def from_json(cls, text: str) -> "ApplicationProjectDocument":
        """Parse one project document through the same schema validators."""

        return parse_project(text)


def _string(value: Any, field_name: str, *, allow_empty: bool = True) -> str:
    if not isinstance(value, str) or (not allow_empty and not value.strip()):
        raise ProjectValidationError(f"Project field '{field_name}' must be a {'non-empty ' if not allow_empty else ''}string.")
    return value


def _integer(value: Any, field_name: str, *, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ProjectValidationError(f"Project field '{field_name}' must be an integer.")
    if minimum is not None and value < minimum:
        raise ProjectValidationError(f"Project field '{field_name}' must be at least {minimum}.")
    return value


def _boolean(value: Any, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise ProjectValidationError(f"Project field '{field_name}' must be boolean.")
    return value


def _validate_invariant_input(data: dict[str, Any]) -> dict[str, Any]:
    source_mode = _string(data.get("source_mode"), "input.source_mode", allow_empty=False)
    if source_mode not in {"catalog", "custom"}:
        raise ProjectValidationError("Invariant project source_mode must be 'catalog' or 'custom'.")
    example_label = _string(data.get("example_label", ""), "input.example_label")
    num_strands = _integer(data.get("num_strands"), "input.num_strands", minimum=1)
    generator_text = _string(data.get("generator_text", ""), "input.generator_text")
    custom_label = _string(data.get("custom_label", ""), "input.custom_label")
    custom_notes = _string(data.get("custom_notes", ""), "input.custom_notes")
    q_text = _string(data.get("q_text", "2"), "input.q_text", allow_empty=False)
    branch_ids_raw = data.get("branch_ids", [])
    if not isinstance(branch_ids_raw, list) or any(not isinstance(item, str) for item in branch_ids_raw):
        raise ProjectValidationError("Project field 'input.branch_ids' must be a list of branch-id strings.")
    branch_ids = tuple(branch_ids_raw)
    backend = data.get("computation_backend")
    if backend is not None:
        backend = _string(backend, "input.computation_backend", allow_empty=False)
    try:
        validate_branch_ids(branch_ids)
        if backend is not None:
            validate_computation_backend(backend, branch_ids)
        parse_q_text(q_text)
        if source_mode == "catalog":
            build_catalog_braid_input(example_label)
        else:
            build_custom_braid_input(num_strands, generator_text)
    except ApplicationServiceError as exc:
        raise ProjectValidationError(str(exc)) from exc
    validated = {
        "source_mode": source_mode,
        "example_label": example_label,
        "num_strands": num_strands,
        "generator_text": generator_text,
        "custom_label": custom_label,
        "custom_notes": custom_notes,
        "q_text": q_text,
        "branch_ids": list(branch_ids),
    }
    if backend is not None:
        validated["computation_backend"] = backend
    return validated


def _validate_custom_rmatrix_input(data: dict[str, Any]) -> dict[str, Any]:
    matrix_text = _string(data.get("matrix_text"), "input.matrix_text", allow_empty=False)
    input_kind = _string(data.get("input_kind"), "input.input_kind", allow_empty=False)
    if input_kind not in {"R", "check-R"}:
        raise ProjectValidationError("Custom R/check-R project input_kind must be 'R' or 'check-R'.")
    local_dimension_raw = data.get("local_dimension")
    local_dimension = None if local_dimension_raw is None else _integer(local_dimension_raw, "input.local_dimension", minimum=1)
    check_braid_relation = _boolean(data.get("check_braid_relation", False), "input.check_braid_relation")
    check_standard_r_ybe = _boolean(data.get("check_standard_r_ybe", False), "input.check_standard_r_ybe")
    num_strands = _integer(data.get("num_strands"), "input.num_strands", minimum=1)
    generator_text = _string(data.get("generator_text", ""), "input.generator_text")
    try:
        matrix = parse_custom_matrix(matrix_text)
        validation = validate_custom_matrix(
            matrix,
            input_kind=input_kind,
            local_dimension=local_dimension,
            check_braid_relation=False,
            check_standard_r_ybe=False,
        )
        if validation.errors:
            raise ProjectValidationError("; ".join(validation.errors))
        build_custom_braid_input(num_strands, generator_text)
    except ProjectValidationError:
        raise
    except (ApplicationServiceError, TypeError, ValueError) as exc:
        raise ProjectValidationError(str(exc)) from exc
    return {
        "matrix_text": matrix_text,
        "input_kind": input_kind,
        "local_dimension": local_dimension,
        "check_braid_relation": check_braid_relation,
        "check_standard_r_ybe": check_standard_r_ybe,
        "num_strands": num_strands,
        "generator_text": generator_text,
    }


def build_invariant_project(
    *,
    source_mode: str,
    example_label: str = "",
    num_strands: int = 1,
    generator_text: str = "",
    custom_label: str = "custom_braid",
    custom_notes: str = "",
    q_text: str = "2",
    branch_ids: tuple[str, ...] | list[str] = (),
    computation_backend: str | None = None,
    ui_state: dict[str, Any] | None = None,
) -> ApplicationProjectDocument:
    """Build and validate an invariant calculation setup without evaluating it."""

    input_data = _validate_invariant_input(
        {
            "source_mode": source_mode,
            "example_label": example_label,
            "num_strands": num_strands,
            "generator_text": generator_text,
            "custom_label": custom_label,
            "custom_notes": custom_notes,
            "q_text": q_text,
            "branch_ids": list(branch_ids),
            **({"computation_backend": computation_backend} if computation_backend is not None else {}),
        }
    )
    return ApplicationProjectDocument(INVARIANT_WORKFLOW, input_data, dict(ui_state or {}))


def build_custom_rmatrix_project(
    *,
    matrix_text: str,
    input_kind: str,
    local_dimension: int | None = None,
    check_braid_relation: bool = False,
    check_standard_r_ybe: bool = False,
    num_strands: int = 1,
    generator_text: str = "",
    ui_state: dict[str, Any] | None = None,
) -> ApplicationProjectDocument:
    """Build and validate a custom R/check-R setup without evaluating it."""

    input_data = _validate_custom_rmatrix_input(
        {
            "matrix_text": matrix_text,
            "input_kind": input_kind,
            "local_dimension": local_dimension,
            "check_braid_relation": check_braid_relation,
            "check_standard_r_ybe": check_standard_r_ybe,
            "num_strands": num_strands,
            "generator_text": generator_text,
        }
    )
    return ApplicationProjectDocument(CUSTOM_RMATRIX_WORKFLOW, input_data, dict(ui_state or {}))


def validate_project_document(document: ApplicationProjectDocument) -> ApplicationProjectDocument:
    if document.schema_version != PROJECT_SCHEMA_VERSION:
        raise ProjectSchemaError(f"Unsupported project schema_version {document.schema_version}; supported version is {PROJECT_SCHEMA_VERSION}.")
    if document.application != PROJECT_APPLICATION:
        raise ProjectSchemaError(f"Unsupported project application '{document.application}'.")
    if document.workflow == INVARIANT_WORKFLOW:
        data = _validate_invariant_input(document.input_data)
    elif document.workflow == CUSTOM_RMATRIX_WORKFLOW:
        data = _validate_custom_rmatrix_input(document.input_data)
    else:
        raise ProjectWorkflowError(f"Unsupported project workflow '{document.workflow}'.")
    if not isinstance(document.ui_state, dict):
        raise ProjectValidationError("Project ui_state must be an object.")
    return ApplicationProjectDocument(
        workflow=document.workflow,
        input_data=data,
        ui_state=dict(document.ui_state),
        schema_version=document.schema_version,
        application=document.application,
        application_version=_string(document.application_version, "application_version", allow_empty=False),
    )


def project_from_dict(data: object) -> ApplicationProjectDocument:
    if not isinstance(data, dict):
        raise ProjectSchemaError("Project document must be a JSON object.")
    try:
        schema_version = _integer(data.get("schema_version"), "schema_version", minimum=1)
        application = _string(data.get("application"), "application", allow_empty=False)
        application_version = _string(data.get("application_version"), "application_version", allow_empty=False)
        workflow = _string(data.get("workflow"), "workflow", allow_empty=False)
        input_data = data.get("input")
        ui_state = data.get("ui_state", {})
    except ProjectValidationError as exc:
        raise ProjectSchemaError(str(exc)) from exc
    if not isinstance(input_data, dict):
        raise ProjectSchemaError("Project field 'input' must be an object.")
    if not isinstance(ui_state, dict):
        raise ProjectSchemaError("Project field 'ui_state' must be an object.")
    return validate_project_document(
        ApplicationProjectDocument(
            workflow=workflow,
            input_data=dict(input_data),
            ui_state=dict(ui_state),
            schema_version=schema_version,
            application=application,
            application_version=application_version,
        )
    )


def serialize_project(document: ApplicationProjectDocument) -> str:
    """Serialize one validated document with stable UTF-8 JSON formatting."""

    validated = validate_project_document(document)
    return json.dumps(validated.to_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def parse_project(text: str) -> ApplicationProjectDocument:
    if not isinstance(text, str):
        raise ProjectFileError("Project content must be UTF-8 JSON text.")
    try:
        data = json.loads(text)
    except (json.JSONDecodeError, TypeError) as exc:
        raise ProjectFileError(f"Malformed project JSON: {exc.msg if isinstance(exc, json.JSONDecodeError) else exc}") from exc
    return project_from_dict(data)


def save_project_file(path: str | Path, document: ApplicationProjectDocument) -> Path:
    target = Path(path)
    try:
        target.write_text(serialize_project(document), encoding="utf-8", newline="\n")
    except OSError as exc:
        raise ProjectFileError(f"Could not write project file '{target}': {exc}") from exc
    return target


def load_project_file(path: str | Path) -> ApplicationProjectDocument:
    target = Path(path)
    try:
        text = target.read_text(encoding="utf-8")
    except OSError as exc:
        raise ProjectFileError(f"Could not read project file '{target}': {exc}") from exc
    return parse_project(text)


__all__ = [
    "ApplicationProjectDocument",
    "CUSTOM_RMATRIX_WORKFLOW",
    "INVARIANT_WORKFLOW",
    "PROJECT_APPLICATION",
    "PROJECT_SCHEMA_VERSION",
    "SUPPORTED_PROJECT_WORKFLOWS",
    "build_custom_rmatrix_project",
    "build_invariant_project",
    "load_project_file",
    "parse_project",
    "project_from_dict",
    "save_project_file",
    "serialize_project",
    "validate_project_document",
]
