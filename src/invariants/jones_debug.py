"""Diagnostic tools for comparing the current P2-type output against Jones references."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import sympy as sp

from src.braid.braid_operator import BraidOperatorBuilder
from src.catalog.braid_examples import BraidExample, get_braid_example
from src.rmatrix.sl2_rmatrix import build_sl2_fundamental_rmatrix

from .eyb_invariant import build_sl2_fundamental_eyb_data, compute_eyb_invariant
from .jones_reference_cases import JonesReferenceCase
from .quantum_trace import compute_raw_closure_trace


Q = sp.Symbol("q", nonzero=True)


@dataclass(frozen=True, slots=True)
class SupportSignature:
    """Store a Laurent-support summary for human inspection."""

    variable: str
    term_count: int
    exponents: tuple[int, ...]
    coefficients: tuple[str, ...]
    min_exponent: int | None
    max_exponent: int | None
    notes: str = ""

    def summary(self) -> str:
        lines = [
            f"Variable: {self.variable}",
            f"Term count: {self.term_count}",
            f"Exponents: {list(self.exponents)}",
            f"Coefficients: {list(self.coefficients)}",
            f"Min exponent: {self.min_exponent}",
            f"Max exponent: {self.max_exponent}",
        ]
        if self.notes:
            lines.append(f"Notes: {self.notes}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        return {
            "variable": self.variable,
            "term_count": self.term_count,
            "exponents": list(self.exponents),
            "coefficients": list(self.coefficients),
            "min_exponent": self.min_exponent,
            "max_exponent": self.max_exponent,
            "notes": self.notes,
        }

    def to_string(self) -> str:
        return self.summary()


@dataclass(frozen=True, slots=True)
class TransformationCandidate:
    """Store one variable-substitution plus monomial-rescaling attempt."""

    variable_map_label: str
    substitution_rule: str
    monomial_factor: sp.Expr | None
    matched_exactly: bool
    difference_expression: sp.Expr | None
    notes: str = ""

    def summary(self) -> str:
        lines = [
            f"Variable map label: {self.variable_map_label}",
            f"Substitution rule: {self.substitution_rule}",
            "Monomial factor: unavailable"
            if self.monomial_factor is None
            else f"Monomial factor: {sp.simplify(self.monomial_factor)}",
            f"Matched exactly: {self.matched_exactly}",
            "Difference expression: unavailable"
            if self.difference_expression is None
            else f"Difference expression: {sp.simplify(self.difference_expression)}",
        ]
        if self.notes:
            lines.append(f"Notes: {self.notes}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        return {
            "variable_map_label": self.variable_map_label,
            "substitution_rule": self.substitution_rule,
            "monomial_factor": None if self.monomial_factor is None else str(sp.simplify(self.monomial_factor)),
            "matched_exactly": self.matched_exactly,
            "difference_expression": None
            if self.difference_expression is None
            else str(sp.simplify(self.difference_expression)),
            "notes": self.notes,
        }

    def to_string(self) -> str:
        return self.summary()


@dataclass(frozen=True, slots=True)
class JonesComparisonResult:
    """Store a structured comparison between the current P2-type output and a Jones target."""

    example_label: str
    current_raw_trace: sp.Expr
    current_p2_output: sp.Expr
    current_p2_unknot_normalization: sp.Expr
    current_reduced_p2_output: sp.Expr
    target_expression: str | None
    target_expression_in_q: sp.Expr | None
    term_count_current: int
    term_count_current_reduced: int
    term_count_target: int | None
    support_current: SupportSignature
    support_current_reduced: SupportSignature
    support_target: SupportSignature | None
    exact_matches: tuple[TransformationCandidate, ...]
    near_matches: tuple[TransformationCandidate, ...]
    notes: str = ""
    tried_candidates: tuple[TransformationCandidate, ...] = ()
    diagnosis_summary: str = ""

    def summary(self) -> str:
        lines = [
            f"Example label: {self.example_label}",
            f"Current raw trace: {sp.simplify(self.current_raw_trace)}",
            f"Current P2-type EYB output: {sp.simplify(self.current_p2_output)}",
            f"Current P2 unknot normalization: {sp.simplify(self.current_p2_unknot_normalization)}",
            f"Current reduced P2-type output: {sp.simplify(self.current_reduced_p2_output)}",
            "Target expression: missing reference slot"
            if self.target_expression is None
            else f"Target expression: {self.target_expression}",
            "Target expression in q: unavailable"
            if self.target_expression_in_q is None
            else f"Target expression in q: {sp.simplify(self.target_expression_in_q)}",
            f"Current unreduced term count: {self.term_count_current}",
            f"Current reduced term count: {self.term_count_current_reduced}",
            "Target term count: unavailable"
            if self.term_count_target is None
            else f"Target term count: {self.term_count_target}",
            f"Exact matches found: {len(self.exact_matches)}",
            f"Near matches found: {len(self.near_matches)}",
            f"Diagnosis summary: {self.diagnosis_summary}",
        ]
        if self.notes:
            lines.append(f"Notes: {self.notes}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        return {
            "example_label": self.example_label,
            "current_raw_trace": str(sp.simplify(self.current_raw_trace)),
            "current_p2_output": str(sp.simplify(self.current_p2_output)),
            "current_p2_unknot_normalization": str(sp.simplify(self.current_p2_unknot_normalization)),
            "current_reduced_p2_output": str(sp.simplify(self.current_reduced_p2_output)),
            "target_expression": self.target_expression,
            "target_expression_in_q": None
            if self.target_expression_in_q is None
            else str(sp.simplify(self.target_expression_in_q)),
            "term_count_current": self.term_count_current,
            "term_count_current_reduced": self.term_count_current_reduced,
            "term_count_target": self.term_count_target,
            "support_current": self.support_current.to_dict(),
            "support_current_reduced": self.support_current_reduced.to_dict(),
            "support_target": None if self.support_target is None else self.support_target.to_dict(),
            "exact_matches": [item.to_dict() for item in self.exact_matches],
            "near_matches": [item.to_dict() for item in self.near_matches],
            "notes": self.notes,
            "tried_candidates": [item.to_dict() for item in self.tried_candidates],
            "diagnosis_summary": self.diagnosis_summary,
        }

    def to_string(self) -> str:
        return self.summary()


def _normalize_expr(expr: sp.Expr | None) -> sp.Expr | None:
    return None if expr is None else sp.expand(sp.simplify(expr))


def _compute_current_p2_output_for_braid(braid_word, q: sp.Symbol) -> sp.Expr:
    rmatrix = build_sl2_fundamental_rmatrix(q)
    operator_data = BraidOperatorBuilder(braid_word=braid_word, rmatrix=rmatrix).build()
    result = compute_eyb_invariant(operator_data, eyb_data=build_sl2_fundamental_eyb_data(q))
    return sp.simplify(result.eyb_normalized_expression)


def current_p2_unknot_normalization(q: sp.Symbol | None = None) -> sp.Expr:
    """Return the current unreduced P2-type value on unknot_1 for reduction diagnostics."""

    parameter = Q if q is None else q
    unknot_braid = get_braid_example("unknot_1").to_braid_word()
    return _compute_current_p2_output_for_braid(unknot_braid, parameter)


def reduce_current_p2_output(current_p2_output: sp.Expr, q: sp.Symbol, normalization: sp.Expr | None = None) -> sp.Expr:
    """Return the reduced current P2-type output by dividing by the current unknot value."""

    divisor = current_p2_unknot_normalization(q) if normalization is None else normalization
    return sp.simplify(current_p2_output / divisor)


def _extract_monomial_term(term: sp.Expr, var: sp.Symbol) -> tuple[int, sp.Expr]:
    powers = term.as_powers_dict()
    exponent = int(sp.Integer(powers.get(var, 0)))
    coefficient = sp.simplify(term / (var ** exponent))
    return exponent, coefficient


def _make_signature(expr: sp.Expr | None, var: sp.Symbol) -> SupportSignature | None:
    if expr is None:
        return None
    simplified = _normalize_expr(expr)
    if simplified == 0:
        return SupportSignature(
            variable=str(var),
            term_count=0,
            exponents=(),
            coefficients=(),
            min_exponent=None,
            max_exponent=None,
            notes="Zero expression.",
        )

    terms = []
    for term in sp.Add.make_args(simplified):
        exponent, coefficient = _extract_monomial_term(term, var)
        terms.append((exponent, sp.simplify(coefficient)))
    terms.sort(key=lambda item: item[0])

    exponents = tuple(item[0] for item in terms)
    coefficients = tuple(str(item[1]) for item in terms)
    return SupportSignature(
        variable=str(var),
        term_count=len(terms),
        exponents=exponents,
        coefficients=coefficients,
        min_exponent=exponents[0],
        max_exponent=exponents[-1],
    )


def support_signature(expr: sp.Expr, var: sp.Symbol) -> SupportSignature:
    """Return term-count, exponent, and coefficient data for a Laurent expression."""

    signature = _make_signature(expr, var)
    if signature is None:
        raise ValueError("support_signature expects a non-missing expression")
    return signature


def convert_target_to_q(target_expr: sp.Expr | str | None, target_var: str | sp.Symbol, mode: str) -> sp.Expr | None:
    """Convert one target expression into q using a small set of candidate variable maps."""

    if target_expr is None:
        return None

    expression = sp.sympify(target_expr)
    target_symbol = sp.Symbol(target_var) if isinstance(target_var, str) else target_var
    q = Q
    substitutions = {
        "t=q": q,
        "t=q^-1": q**-1,
        "t=q**2": q**2,
        "t=q**-2": q**-2,
    }
    if mode not in substitutions:
        raise KeyError(f"Unsupported target-to-q mode: {mode}")
    return _normalize_expr(expression.subs(target_symbol, substitutions[mode]))


def search_monomial_match(
    current_expr: sp.Expr,
    target_expr_in_q: sp.Expr | None,
    q: sp.Symbol,
    exponent_window: tuple[int, int] = (-20, 20),
    *,
    variable_map_label: str = "",
) -> tuple[TransformationCandidate, ...]:
    """Search whether current_expr differs from target_expr_in_q by a monomial q^k factor."""

    if target_expr_in_q is None:
        return (
            TransformationCandidate(
                variable_map_label=variable_map_label,
                substitution_rule=variable_map_label,
                monomial_factor=None,
                matched_exactly=False,
                difference_expression=None,
                notes="Target expression is missing, so monomial-match search was skipped.",
            ),
        )

    lower, upper = exponent_window
    candidates: list[TransformationCandidate] = []
    for exponent in range(lower, upper + 1):
        monomial_factor = q**exponent
        difference = _normalize_expr(current_expr - monomial_factor * target_expr_in_q)
        matched = difference == 0
        candidates.append(
            TransformationCandidate(
                variable_map_label=variable_map_label,
                substitution_rule=variable_map_label,
                monomial_factor=monomial_factor,
                matched_exactly=matched,
                difference_expression=difference,
                notes=f"Checked monomial rescaling exponent k = {exponent}.",
            )
        )
    return tuple(candidates)


def _find_near_matches(
    current_signature: SupportSignature,
    candidates: tuple[TransformationCandidate, ...],
    target_expr_in_q: sp.Expr | None,
    q: sp.Symbol,
) -> tuple[TransformationCandidate, ...]:
    if target_expr_in_q is None:
        return ()

    near: list[TransformationCandidate] = []
    for candidate in candidates:
        if candidate.matched_exactly or candidate.monomial_factor is None:
            continue
        shifted_target = _normalize_expr(candidate.monomial_factor * target_expr_in_q)
        shifted_signature = support_signature(shifted_target, q)
        same_support = shifted_signature.exponents == current_signature.exponents
        same_term_count = shifted_signature.term_count == current_signature.term_count
        if same_support or same_term_count:
            note_parts = []
            if same_support:
                note_parts.append("Same exponent support after monomial shift, but coefficients still differ.")
            if same_term_count and not same_support:
                note_parts.append("Same term count after monomial shift, but exponent support still differs.")
            near.append(
                TransformationCandidate(
                    variable_map_label=candidate.variable_map_label,
                    substitution_rule=candidate.substitution_rule,
                    monomial_factor=candidate.monomial_factor,
                    matched_exactly=False,
                    difference_expression=candidate.difference_expression,
                    notes=" ".join(note_parts),
                )
            )
    return tuple(near[:8])


def _diagnose_mismatch(
    current_signature: SupportSignature,
    target_signature: SupportSignature | None,
    exact_matches: tuple[TransformationCandidate, ...],
    near_matches: tuple[TransformationCandidate, ...],
    target_present: bool,
) -> str:
    if not target_present:
        return "Target Jones reference is missing, so only current-output structural diagnostics were produced."
    if exact_matches:
        return "At least one tested variable substitution plus monomial factor matched exactly."
    if target_signature is None:
        return "Target conversion to q failed, so structural comparison could not be completed."
    if current_signature.term_count != target_signature.term_count:
        return "Current P2-type output and target have different term counts, so the mismatch is not just a monomial shift."
    if current_signature.exponents != target_signature.exponents:
        return "Support exponents differ before any monomial correction, so the mismatch is already more than coefficient-only drift."
    if near_matches:
        return "Some variable substitutions can align support or term count, but none gave an exact monomial-rescaled match."
    return "No tested substitution mode reduced the comparison to a simple monomial rescaling or inversion-only match."


def compare_current_p2_with_jones(
    reference_case: JonesReferenceCase,
    *,
    q: sp.Symbol | None = None,
    substitution_modes: tuple[str, ...] = ("t=q", "t=q^-1", "t=q**2", "t=q**-2"),
    exponent_window: tuple[int, int] = (-20, 20),
) -> JonesComparisonResult:
    """Compare the current sl2 fundamental P2-type output against one editable Jones reference."""

    parameter = Q if q is None else q
    rmatrix = build_sl2_fundamental_rmatrix(parameter)
    operator_data = BraidOperatorBuilder(braid_word=reference_case.braid_word, rmatrix=rmatrix).build()
    raw_result = compute_raw_closure_trace(operator_data)
    current_result = compute_eyb_invariant(operator_data, eyb_data=build_sl2_fundamental_eyb_data(parameter))

    current_raw_trace = sp.simplify(raw_result.raw_closure_trace)
    current_p2_output = sp.simplify(current_result.eyb_normalized_expression)
    unknot_normalization = current_p2_unknot_normalization(parameter)
    current_reduced_p2_output = reduce_current_p2_output(current_p2_output, parameter, unknot_normalization)
    current_support = support_signature(current_p2_output, parameter)
    current_reduced_support = support_signature(current_reduced_p2_output, parameter)

    target_in_q_first: sp.Expr | None = None
    target_support_first: SupportSignature | None = None
    all_candidates: list[TransformationCandidate] = []
    exact_matches: list[TransformationCandidate] = []
    near_matches: list[TransformationCandidate] = []

    for mode in substitution_modes:
        target_in_q = convert_target_to_q(reference_case.target_expression, reference_case.variable_name, mode)
        if target_in_q_first is None and target_in_q is not None:
            target_in_q_first = target_in_q
            target_support_first = support_signature(target_in_q, parameter)
        candidates = search_monomial_match(
            current_reduced_p2_output,
            target_in_q,
            parameter,
            exponent_window,
            variable_map_label=mode,
        )
        all_candidates.extend(candidates)
        exact_matches.extend(candidate for candidate in candidates if candidate.matched_exactly)
        if target_in_q is not None:
            near_matches.extend(_find_near_matches(current_reduced_support, candidates, target_in_q, parameter))

    term_count_target = None if target_support_first is None else target_support_first.term_count
    diagnosis_summary = _diagnose_mismatch(
        current_reduced_support,
        target_support_first,
        tuple(exact_matches),
        tuple(near_matches),
        reference_case.target_expression is not None,
    )

    return JonesComparisonResult(
        example_label=reference_case.label,
        current_raw_trace=current_raw_trace,
        current_p2_output=current_p2_output,
        current_p2_unknot_normalization=unknot_normalization,
        current_reduced_p2_output=current_reduced_p2_output,
        target_expression=reference_case.target_expression,
        target_expression_in_q=target_in_q_first,
        term_count_current=current_support.term_count,
        term_count_current_reduced=current_reduced_support.term_count,
        term_count_target=term_count_target,
        support_current=current_support,
        support_current_reduced=current_reduced_support,
        support_target=target_support_first,
        exact_matches=tuple(exact_matches),
        near_matches=tuple(near_matches[:8]),
        notes=(
            "Current unreduced P2-type output is retained for inspection, but Jones comparison is performed on the "
            "reduced current P2 layer obtained by dividing by the current unknot value. This tool does not rename "
            "the current output as Jones; it only diagnoses possible relations."
        ),
        tried_candidates=tuple(all_candidates),
        diagnosis_summary=diagnosis_summary,
    )


def compare_named_current_p2_with_jones(
    label: str,
    reference_cases: tuple[JonesReferenceCase, ...],
    *,
    q: sp.Symbol | None = None,
    substitution_modes: tuple[str, ...] = ("t=q", "t=q^-1", "t=q**2", "t=q**-2"),
    exponent_window: tuple[int, int] = (-20, 20),
) -> JonesComparisonResult:
    """Compare one named example against the matching Jones-reference slot."""

    for case in reference_cases:
        if case.label == label:
            return compare_current_p2_with_jones(
                case,
                q=q,
                substitution_modes=substitution_modes,
                exponent_window=exponent_window,
            )
    raise KeyError(f"No Jones reference case registered for label: {label}")


def make_reference_case_from_example(
    example: BraidExample | str,
    *,
    target_expression: str | None,
    variable_name: str = "t",
    convention_label: str = "editable reference slot",
    notes: str = "",
) -> JonesReferenceCase:
    """Build a one-off reference case from a named or explicit braid example."""

    braid_example = get_braid_example(example) if isinstance(example, str) else example
    return JonesReferenceCase(
        label=braid_example.label,
        braid_word=braid_example.to_braid_word(),
        target_expression=target_expression,
        variable_name=variable_name,
        convention_label=convention_label,
        notes=notes,
    )