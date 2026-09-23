"""Frontend-neutral result DTOs, conversion, reporting, and serialization."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable

import sympy as sp

from src.invariants.branch_results import InvariantBranchResult
from src.invariants.multibranch_benchmark import MultiBranchBenchmarkEntry

from .branch_catalog import get_evaluation_branch
from .explanations import get_branch_explanation


def _text(value: object | None) -> str | None:
    return None if value is None else str(sp.simplify(value))


@dataclass(frozen=True, slots=True)
class ApplicationBranchResult:
    """Stable frontend-facing representation of one branch evaluation."""

    model_id: str
    branch_id: str
    display_name: str
    status: str
    representation_name: str
    raw_trace: str | None
    primary_output: str | None
    primary_output_label: str
    normalization_label: str
    variable_convention: str
    notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    primary_output_expression: Any | None = field(default=None, repr=False, compare=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "branch_id": self.branch_id,
            "display_name": self.display_name,
            "status": self.status,
            "representation_name": self.representation_name,
            "raw_trace": self.raw_trace,
            "primary_output": self.primary_output,
            "primary_output_label": self.primary_output_label,
            "normalization_label": self.normalization_label,
            "variable_convention": self.variable_convention,
            "notes": self.notes,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class ApplicationBraidResult:
    """Stable frontend-facing result for one catalog or custom braid input."""

    example_label: str
    num_strands: int
    generators: tuple[int, ...]
    word_string: str
    notes: str
    source_mode: str
    selected_branch_ids: tuple[str, ...] | None
    branch_results: tuple[ApplicationBranchResult, ...]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "example_label": self.example_label,
            "braid": {
                "num_strands": self.num_strands,
                "generators": list(self.generators),
                "word_string": self.word_string,
            },
            "notes": self.notes,
            "source_mode": self.source_mode,
            "selected_branch_ids": None if self.selected_branch_ids is None else list(self.selected_branch_ids),
            "branch_results": [result.to_dict() for result in self.branch_results],
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class PolynomialPresentation:
    """Frontend-neutral polynomial/variable display information."""

    primary_project_expression: str | None
    project_variable_convention: str
    standard_polynomial_expression: str | None = None
    standard_variable_name: str | None = None
    atlas_comparable_expression: str | None = None
    atlas_variable_name: str | None = None
    conversion_status: str = "not_applicable"
    conversion_reason: str = ""
    evaluation_parameter_text: str | None = None


@dataclass(frozen=True, slots=True)
class ApplicationBranchPresentation:
    """Compact display descriptor built from an existing branch DTO."""

    display_name: str
    status: str
    primary_output_label: str
    primary_output: str | None
    concise_variable_label: str
    candidate_warning: str | None
    polynomial: PolynomialPresentation


def _presentation_text(value: sp.Expr) -> str:
    return str(sp.expand(value))


def _is_scalar_q_parameter(q_parameter: Any | None) -> bool:
    if q_parameter is None:
        return False
    try:
        parsed = sp.sympify(q_parameter)
        return not parsed.free_symbols
    except (sp.SympifyError, TypeError):
        return False


def _laurent_terms(expression: sp.Expr, symbol: sp.Symbol) -> dict[int, sp.Expr] | None:
    expanded = sp.expand(sp.cancel(expression))
    if expanded == 0:
        return {0: sp.Integer(0)}
    terms: dict[int, sp.Expr] = {}
    for term in sp.Add.make_args(expanded):
        coefficient, exponent = term.as_coeff_exponent(symbol)
        if exponent.is_integer is not True:
            return None
        if sp.simplify(term - coefficient * symbol**exponent) != 0:
            return None
        if coefficient.free_symbols:
            return None
        integer_exponent = int(exponent)
        terms[integer_exponent] = sp.simplify(terms.get(integer_exponent, sp.Integer(0)) + coefficient)
    return {exponent: coefficient for exponent, coefficient in terms.items() if coefficient != 0}


def _convert_laurent_expression(
    expression: sp.Expr | None,
    *,
    source_symbol: sp.Symbol | None,
    target_symbol: str,
    exponent_map: Callable[[int], int | None],
) -> str | None:
    if expression is None or source_symbol is None:
        return None
    target = sp.Symbol(target_symbol)
    laurent_terms = _laurent_terms(expression, source_symbol)
    if laurent_terms is None:
        return None
    converted = sp.Integer(0)
    for exponent, coefficient in laurent_terms.items():
        mapped_exponent = exponent_map(exponent)
        if mapped_exponent is None:
            return None
        converted += coefficient * target**mapped_exponent
    return _presentation_text(converted)


def _project_symbol(expression: sp.Expr | None) -> sp.Symbol | None:
    if expression is None:
        return None
    symbols = tuple(expression.free_symbols)
    return symbols[0] if len(symbols) == 1 else None


def build_polynomial_presentation(
    result: ApplicationBranchResult,
    *,
    q_parameter: Any | None = None,
    q_parameter_text: str | None = None,
) -> PolynomialPresentation:
    """Build compact variable/polynomial presentation for one branch DTO."""

    if _is_scalar_q_parameter(q_parameter):
        return PolynomialPresentation(
            primary_project_expression=result.primary_output,
            project_variable_convention=result.variable_convention,
            conversion_status="scalar_only",
            conversion_reason="Numeric q input gives a scalar evaluation only; no polynomial is inferred from that value.",
            evaluation_parameter_text=q_parameter_text,
        )

    if result.branch_id == "sl2_fundamental":
        source_symbol = _project_symbol(result.primary_output_expression)
        standard_expression = _convert_laurent_expression(
            result.primary_output_expression,
            source_symbol=source_symbol,
            target_symbol="t",
            exponent_map=lambda exponent: None if exponent % 2 else -exponent // 2,
        )
        atlas_expression = _convert_laurent_expression(
            result.primary_output_expression,
            source_symbol=source_symbol,
            target_symbol="q_atlas",
            exponent_map=lambda exponent: None if exponent % 2 else exponent // 2,
        )
        if standard_expression is None:
            return PolynomialPresentation(
                primary_project_expression=result.primary_output,
                project_variable_convention=result.variable_convention,
                atlas_comparable_expression=atlas_expression,
                atlas_variable_name="Knot Atlas-comparable q_atlas" if atlas_expression is not None else None,
                conversion_status="unavailable",
                conversion_reason="The current project-q expression is not an exact even-exponent Laurent polynomial, so no standard Jones t-form is shown.",
                evaluation_parameter_text=q_parameter_text,
            )
        return PolynomialPresentation(
            primary_project_expression=result.primary_output,
            project_variable_convention=result.variable_convention,
            standard_polynomial_expression=standard_expression,
            standard_variable_name="Standard Jones variable t",
            atlas_comparable_expression=atlas_expression,
            atlas_variable_name="Knot Atlas-comparable q_atlas" if atlas_expression is not None else None,
            conversion_status="exact",
            conversion_reason="Exact Laurent conversion from project q is available.",
            evaluation_parameter_text=q_parameter_text,
        )

    if result.branch_id == "sl3_fundamental":
        source_symbol = _project_symbol(result.primary_output_expression)
        atlas_expression = _convert_laurent_expression(
            result.primary_output_expression,
            source_symbol=source_symbol,
            target_symbol="q_atlas",
            exponent_map=lambda exponent: -exponent,
        )
        if atlas_expression is None:
            return PolynomialPresentation(
                primary_project_expression=result.primary_output,
                project_variable_convention=result.variable_convention,
                conversion_status="unavailable",
                conversion_reason="The current project-q expression is not an exact Laurent polynomial in the maintained A2 variable conversion.",
                evaluation_parameter_text=q_parameter_text,
            )
        return PolynomialPresentation(
            primary_project_expression=result.primary_output,
            project_variable_convention=result.variable_convention,
            atlas_comparable_expression=atlas_expression,
            atlas_variable_name="Knot Atlas-comparable A2 variable q_atlas" if atlas_expression is not None else None,
            conversion_status="exact",
            conversion_reason="Exact Laurent conversion to the maintained A2 Atlas-comparable variable is available.",
            evaluation_parameter_text=q_parameter_text,
        )

    return PolynomialPresentation(
        primary_project_expression=result.primary_output,
        project_variable_convention=result.variable_convention,
        conversion_status="not_applicable",
        conversion_reason="No standard polynomial relabeling is presented for this branch.",
        evaluation_parameter_text=q_parameter_text,
    )


def build_application_branch_presentation(
    result: ApplicationBranchResult,
    *,
    q_parameter: Any | None = None,
    q_parameter_text: str | None = None,
) -> ApplicationBranchPresentation:
    """Build the compact user-facing presentation descriptor for one branch."""

    explanation = get_branch_explanation(result.branch_id)
    polynomial = build_polynomial_presentation(result, q_parameter=q_parameter, q_parameter_text=q_parameter_text)
    candidate_warning = None
    warnings = explanation.warnings
    if result.status == "candidate" and warnings:
        candidate_warning = warnings[0]
    concise_variable_label = {
        "sl2_fundamental": "Project q; standard Jones variable t = q_project^-2; Atlas-comparable q_atlas = q_project^2.",
        "sl3_fundamental": "Project q; Atlas-comparable A2 variable q_atlas = q_project^-1.",
        "sl2_spin1": "Project q only; no final standard colored-Jones variable identification is presented.",
    }.get(result.branch_id, explanation.variable_convention)
    if polynomial.conversion_status == "scalar_only" and polynomial.evaluation_parameter_text is not None:
        concise_variable_label = f"Scalar evaluation at q = {polynomial.evaluation_parameter_text}."
    return ApplicationBranchPresentation(
        display_name=result.display_name,
        status=result.status,
        primary_output_label=result.primary_output_label,
        primary_output=result.primary_output,
        concise_variable_label=concise_variable_label,
        candidate_warning=candidate_warning,
        polynomial=polynomial,
    )


def application_branch_result_from_internal(result: InvariantBranchResult) -> ApplicationBranchResult:
    """Convert the existing mathematical-program result at the service boundary."""

    descriptor = get_evaluation_branch(result.branch_id)
    return ApplicationBranchResult(
        model_id=descriptor.model_id,
        branch_id=result.branch_id,
        display_name=descriptor.display_name,
        status=result.status,
        representation_name=result.representation_name,
        raw_trace=_text(result.raw_trace),
        primary_output=_text(result.primary_output),
        primary_output_label=result.primary_output_label,
        normalization_label=result.normalization_label,
        variable_convention=result.variable_convention,
        notes=result.notes,
        metadata=dict(result.metadata),
        primary_output_expression=None if result.primary_output is None else sp.simplify(result.primary_output),
    )


def application_braid_result_from_internal(entry: MultiBranchBenchmarkEntry) -> ApplicationBraidResult:
    """Convert a recovered multibranch entry without changing evaluator behavior."""

    if entry.branch_results:
        braid_word = entry.branch_results[0].braid_word
    else:
        braid_data = entry.metadata.get("braid_word", {})
        braid_word = None
        num_strands = int(braid_data.get("num_strands", 0))
        generators = tuple(int(value) for value in braid_data.get("generators", ()))
        word_string = str(braid_data.get("word") or "identity")
    if braid_word is not None:
        num_strands = braid_word.num_strands
        generators = tuple(braid_word.generators)
        word_string = braid_word.word_string()
    selected = entry.metadata.get("selected_branch_ids")
    return ApplicationBraidResult(
        example_label=entry.example_label,
        num_strands=num_strands,
        generators=generators,
        word_string=word_string,
        notes=entry.notes,
        source_mode=str(entry.metadata.get("input_mode", "catalog")),
        selected_branch_ids=None if selected is None else tuple(str(value) for value in selected),
        branch_results=tuple(application_branch_result_from_internal(result) for result in entry.branch_results),
        metadata=dict(entry.metadata),
    )


def filter_application_braid_result(result: ApplicationBraidResult, branch_ids: tuple[str, ...] | list[str]) -> ApplicationBraidResult:
    """Return one DTO limited to currently visible branch ids."""

    selected = set(branch_ids)
    return ApplicationBraidResult(
        example_label=result.example_label,
        num_strands=result.num_strands,
        generators=result.generators,
        word_string=result.word_string,
        notes=result.notes,
        source_mode=result.source_mode,
        selected_branch_ids=tuple(branch_ids),
        branch_results=tuple(item for item in result.branch_results if item.branch_id in selected),
        metadata=dict(result.metadata),
    )


def format_application_branch_result(result: ApplicationBranchResult) -> str:
    """Format one DTO using the recovered formatter's visible report fields."""

    lines = [
        f"=== {result.display_name} ===",
        f"Representation: {result.representation_name}",
        f"Status: {result.status}",
        f"Raw trace: {result.raw_trace or 'not available'}",
        f"Primary output label: {result.primary_output_label}",
        f"Primary output: {result.primary_output or 'not available'}",
        f"Normalization label: {result.normalization_label}",
        f"Variable convention: {result.variable_convention}",
    ]
    for label, key in (
        ("Unreduced P2", "unreduced_p2_output"),
        ("Quantum trace before normalization", "quantum_trace_before_normalization"),
        ("Unreduced candidate output", "unreduced_candidate_output"),
        ("Unknot normalization", "unknot_normalization"),
        ("Reduced P2", "reduced_p2_output"),
        ("Reduced candidate output", "reduced_candidate_output"),
        ("Branch note", "branch_note"),
        ("Projector-aware checks", "projector_checks"),
    ):
        if key in result.metadata:
            lines.append(f"{label}: {result.metadata[key]}")
    if result.notes:
        lines.append(f"Notes: {result.notes}")
    return "\n".join(lines)


def format_application_branch_compact(
    result: ApplicationBranchResult,
    *,
    q_parameter: Any | None = None,
    q_parameter_text: str | None = None,
) -> str:
    """Format one branch in the maintained compact on-screen presentation."""

    presentation = build_application_branch_presentation(result, q_parameter=q_parameter, q_parameter_text=q_parameter_text)
    lines = [
        presentation.display_name,
        f"Status: {presentation.status}",
        f"Primary output ({presentation.primary_output_label}): {presentation.primary_output or 'not available'}",
    ]
    if presentation.polynomial.conversion_status == "scalar_only":
        lines.append(f"Variable summary: {presentation.concise_variable_label}")
        lines.append(presentation.polynomial.conversion_reason)
    else:
        lines.append(f"Variable summary: {presentation.concise_variable_label}")
        lines.append(f"Project q expression: {presentation.polynomial.primary_project_expression or 'not available'}")
        if presentation.polynomial.standard_polynomial_expression is not None and presentation.polynomial.standard_variable_name is not None:
            lines.append(
                f"{presentation.polynomial.standard_variable_name} (t = q_project^-2): {presentation.polynomial.standard_polynomial_expression}"
            )
        elif result.branch_id == "sl2_fundamental":
            lines.append(f"Standard Jones conversion: {presentation.polynomial.conversion_reason}")
        if presentation.polynomial.atlas_comparable_expression is not None and presentation.polynomial.atlas_variable_name is not None:
            lines.append(f"{presentation.polynomial.atlas_variable_name}: {presentation.polynomial.atlas_comparable_expression}")
        elif result.branch_id == "sl3_fundamental":
            lines.append(f"Atlas-comparable conversion: {presentation.polynomial.conversion_reason}")
    if presentation.candidate_warning:
        lines.append(f"Warning: {presentation.candidate_warning}")
    return "\n".join(lines)


def format_application_braid_result(result: ApplicationBraidResult) -> str:
    """Format a full application result for text-oriented frontends."""

    lines = [f"########## {result.example_label} ##########"]
    if result.notes:
        lines.append(f"Notes: {result.notes}")
    for branch_result in result.branch_results:
        lines.extend(("", format_application_branch_result(branch_result)))
    return "\n".join(lines)


def format_application_braid_compact_result(
    result: ApplicationBraidResult,
    *,
    q_parameter: Any | None = None,
    q_parameter_text: str | None = None,
) -> str:
    """Format a compact result view from the existing application DTOs."""

    lines = [f"########## {result.example_label} ##########"]
    if result.notes:
        lines.append(f"Notes: {result.notes}")
    for branch_result in result.branch_results:
        lines.extend(("", format_application_branch_compact(branch_result, q_parameter=q_parameter, q_parameter_text=q_parameter_text)))
    return "\n".join(lines)


def serialize_application_braid_result(result: ApplicationBraidResult) -> str:
    """Return deterministic JSON suitable for raw views and export."""

    return json.dumps(result.to_dict(), indent=2, ensure_ascii=False, sort_keys=True)
