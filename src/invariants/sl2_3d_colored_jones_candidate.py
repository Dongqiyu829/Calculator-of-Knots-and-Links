"""Candidate colored-Jones-style output layer for the sl2 3-dimensional 9x9 branch."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import sympy as sp

from src.braid.braid_operator import BraidOperatorBuilder, BraidOperatorData
from src.braid.braid_word import BraidWord
from src.catalog.braid_examples import get_braid_example
from src.rmatrix.sl2_rmatrix import build_sl2_spin1_rmatrix

from .quantum_trace import compute_raw_closure_trace


SL2_3D_USER_FACING_NAME = "sl2 的3维表示下的9x9矩阵"
SL2_3D_BRANCH_STATUS = "candidate"
SL2_3D_CANDIDATE_OUTPUT_LABEL = "Colored Jones candidate output"
SL2_3D_KNOT_ATLAS_COMPARISON_RULE = (
    "Knot Atlas uses J_n for the (n+1)-dimensional sl2 representation, so this 3D branch is currently compared "
    "against Knot Atlas n=2 colored Jones data."
)
SL2_3D_KNOT_ATLAS_SCOPE_NOTE = (
    "This is a current calibrated correspondence statement, not a theorem-level final global colored-Jones "
    "normalization claim."
)
SL2_3D_KNOT_ATLAS_TREFOIL_RELATION = "Current trefoil calibration: reduced candidate output for 3_1 = q^6 J_2(3_1; q^2)."
SL2_3D_KNOT_ATLAS_FIVE_ONE_RELATION = "Current direct 5_1 check: reduced candidate output for 5_1 = q^10 J_2(5_1; q^2)."
SL2_3D_KNOT_ATLAS_VERIFICATION_NOTE = (
    "Verification set currently includes 3_1, 5_1, and 5_2. Current direct q-shift checks confirm 3_1 and 5_1; "
    "5_2 remains under verification."
)
SL2_3D_KNOT_ATLAS_BRANCH_NOTE = " ".join(
    (
        "Projector-aware local data are retained, and the branch should still be read as a colored Jones candidate branch.",
        SL2_3D_KNOT_ATLAS_COMPARISON_RULE,
        SL2_3D_KNOT_ATLAS_TREFOIL_RELATION,
        SL2_3D_KNOT_ATLAS_FIVE_ONE_RELATION,
        SL2_3D_KNOT_ATLAS_SCOPE_NOTE,
        SL2_3D_KNOT_ATLAS_VERIFICATION_NOTE,
    )
)
SL2_3D_VARIABLE_CONVENTION = (
    "Current candidate branch uses q as the braid-side variable. "
    "For external comparison we currently inspect Knot Atlas n=2 data via q -> q^2. "
    "No final global colored-Jones variable substitution is fixed yet."
)
_Q_SYMBOL = sp.Symbol("q", nonzero=True)


@dataclass(frozen=True, slots=True)
class Sl2ThreeDimKnotAtlasReferenceCase:
    """Store one current Knot Atlas correspondence reference for the sl2 3D candidate branch."""

    case_id: str
    knot_label: str
    program_braid_label: str
    braid_word: BraidWord | None
    knot_atlas_reference: sp.Expr
    notes: str = ""


@dataclass(frozen=True, slots=True)
class Sl2ThreeDimKnotAtlasCorrespondenceCheck:
    """Store the current comparison status between the candidate branch and Knot Atlas data."""

    case_id: str
    knot_label: str
    program_braid_label: str
    status: str
    knot_atlas_reference: sp.Expr
    substituted_reference: sp.Expr
    candidate_output: sp.Expr | None
    q_shift: int | None
    relation_text: str
    notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def summary(self) -> str:
        lines = [
            f"Case: {self.case_id}",
            f"Knot label: {self.knot_label}",
            f"Program braid label: {self.program_braid_label}",
            f"Status: {self.status}",
            f"Relation: {self.relation_text}",
            f"Knot Atlas J_2 reference: {sp.simplify(self.knot_atlas_reference)}",
            f"Reference after q -> q^2: {sp.simplify(self.substituted_reference)}",
        ]
        if self.candidate_output is None:
            lines.append("Candidate output: not computed yet")
        else:
            lines.append(f"Candidate output: {sp.simplify(self.candidate_output)}")
        if self.q_shift is not None:
            lines.append(f"Detected q-shift: {self.q_shift}")
        if self.notes:
            lines.append(f"Notes: {self.notes}")
        if self.metadata:
            lines.append(f"Metadata: {self.metadata}")
        return "\n".join(lines)


def _sympify_knot_atlas_reference(reference_text: str) -> sp.Expr:
    return sp.sympify(reference_text, locals={"q": _Q_SYMBOL})


def _build_sl2_3d_five_one_braid() -> BraidWord:
    return BraidWord.from_iterable(
        num_strands=2,
        generators=(1, 1, 1, 1, 1),
        label="5_1_cinquefoil",
        notes="Closure of sigma_1^5 on two strands, i.e. the standard T(2,5) braid presentation.",
        metadata={"knot_label": "5_1", "source": "current correspondence helper"},
    )


def get_sl2_3d_knot_atlas_reference_cases() -> tuple[Sl2ThreeDimKnotAtlasReferenceCase, ...]:
    """Return the current external correspondence cases tracked against Knot Atlas data."""

    return (
        Sl2ThreeDimKnotAtlasReferenceCase(
            case_id="3_1",
            knot_label="trefoil / 3_1",
            program_braid_label="catalog: trefoil",
            braid_word=get_braid_example("trefoil").to_braid_word(),
            knot_atlas_reference=_sympify_knot_atlas_reference(
                "q**-2 + q**-5 - q**-7 + q**-8 - q**-9 - q**-10 + q**-11"
            ),
            notes=(
                "Current confirmed calibration case against Knot Atlas n=2 colored Jones data in the braid-side q "
                "convention used by this branch."
            ),
        ),
        Sl2ThreeDimKnotAtlasReferenceCase(
            case_id="5_1",
            knot_label="cinquefoil / 5_1",
            program_braid_label="closure of sigma_1^5",
            braid_word=_build_sl2_3d_five_one_braid(),
            knot_atlas_reference=_sympify_knot_atlas_reference(
                "q**-19 - q**-18 + q**-16 - 2*q**-15 + q**-13 - q**-12 + q**-10 - q**-9 + q**-7 + q**-4"
            ),
            notes=(
                "Direct comparison currently uses the standard 2-strand T(2,5) braid presentation and checks only "
                "for a pure q-shift after the q -> q^2 substitution."
            ),
        ),
        Sl2ThreeDimKnotAtlasReferenceCase(
            case_id="5_2",
            knot_label="5_2",
            program_braid_label="reference polynomial only",
            braid_word=None,
            knot_atlas_reference=_sympify_knot_atlas_reference(
                "q**-2 - q**-3 + 3*q**-5 - 2*q**-6 - q**-7 + 4*q**-8 - 3*q**-9 - q**-10 + 3*q**-11 - 2*q**-12 "
                "- q**-13 + 2*q**-14 - q**-15 - q**-16 + q**-17"
            ),
            notes=(
                "The Knot Atlas J_2 reference is fixed here, but a canonical braid representative in the current "
                "project Artin-generator convention is still under verification."
            ),
        ),
    )


def get_sl2_3d_knot_atlas_summary_lines() -> tuple[str, ...]:
    """Return the shared wording used across GUI, reports, and docs for Knot Atlas comparison."""

    return (
        SL2_3D_KNOT_ATLAS_COMPARISON_RULE,
        SL2_3D_KNOT_ATLAS_TREFOIL_RELATION,
        SL2_3D_KNOT_ATLAS_FIVE_ONE_RELATION,
        SL2_3D_KNOT_ATLAS_SCOPE_NOTE,
        SL2_3D_KNOT_ATLAS_VERIFICATION_NOTE,
    )


def get_sl2_3d_knot_atlas_current_status_lines() -> tuple[str, ...]:
    """Return the current stored status lines for the shared Knot Atlas wording."""

    return (
        "3_1: confirmed by the direct q-shift relation q^6 J_2(3_1; q^2).",
        "5_1: confirmed by the direct q-shift relation q^10 J_2(5_1; q^2).",
        "5_2: under verification because the project-side braid representative is not fixed yet.",
    )


def _extract_laurent_terms(expr: sp.Expr, parameter: sp.Expr) -> tuple[tuple[int, sp.Expr], ...] | None:
    expanded = sp.expand(sp.simplify(expr))
    if expanded == 0:
        return tuple()

    merged_terms: dict[int, sp.Expr] = {}
    for term in sp.Add.make_args(expanded):
        coefficient, exponent = term.as_coeff_exponent(parameter)
        if exponent.is_integer is False:
            return None
        if sp.simplify(term - coefficient * parameter**exponent) != 0:
            return None
        exponent_int = int(exponent)
        merged_terms[exponent_int] = sp.simplify(merged_terms.get(exponent_int, sp.Integer(0)) + coefficient)

    return tuple(
        (exponent, coefficient)
        for exponent, coefficient in sorted(merged_terms.items())
        if sp.simplify(coefficient) != 0
    )


def _detect_q_shift(candidate_output: sp.Expr, reference_output: sp.Expr, parameter: sp.Expr) -> int | None:
    candidate_terms = _extract_laurent_terms(candidate_output, parameter)
    reference_terms = _extract_laurent_terms(reference_output, parameter)
    if candidate_terms is None or reference_terms is None:
        return None
    if len(candidate_terms) != len(reference_terms):
        return None
    if not candidate_terms:
        return 0

    shift = candidate_terms[0][0] - reference_terms[0][0]
    for (candidate_exponent, candidate_coefficient), (reference_exponent, reference_coefficient) in zip(
        candidate_terms,
        reference_terms,
        strict=True,
    ):
        if candidate_exponent != reference_exponent + shift:
            return None
        if sp.simplify(candidate_coefficient - reference_coefficient) != 0:
            return None
    return shift


def get_sl2_3d_knot_atlas_reference_case(case_id: str) -> Sl2ThreeDimKnotAtlasReferenceCase:
    """Return one current Knot Atlas reference case by id."""

    for case in get_sl2_3d_knot_atlas_reference_cases():
        if case.case_id == case_id:
            return case
    raise KeyError(f"Unknown Knot Atlas correspondence case: {case_id}")


def compute_sl2_3d_knot_atlas_correspondence(
    case_id: str,
    *,
    q: sp.Expr | None = None,
) -> Sl2ThreeDimKnotAtlasCorrespondenceCheck:
    """Compare the current candidate branch against one stored Knot Atlas reference case."""

    parameter = q if q is not None else _Q_SYMBOL
    case = get_sl2_3d_knot_atlas_reference_case(case_id)
    substituted_reference = sp.expand(case.knot_atlas_reference.subs(_Q_SYMBOL, parameter**2))

    if case.braid_word is None:
        return Sl2ThreeDimKnotAtlasCorrespondenceCheck(
            case_id=case.case_id,
            knot_label=case.knot_label,
            program_braid_label=case.program_braid_label,
            status="under_verification",
            knot_atlas_reference=case.knot_atlas_reference,
            substituted_reference=substituted_reference,
            candidate_output=None,
            q_shift=None,
            relation_text=(
                "Under verification: Knot Atlas J_2 reference is stored, but the current project braid "
                "representative is not fixed yet."
            ),
            notes=case.notes,
            metadata={
                "comparison_rule": "q -> q^2",
                "comparison_scope": "reference_only",
            },
        )

    candidate_result = compute_sl2_3d_candidate_output(case.braid_word, q=parameter)
    candidate_output = sp.expand(sp.simplify(candidate_result.reduced_candidate_output))
    q_shift = _detect_q_shift(candidate_output, substituted_reference, parameter)
    if q_shift is not None:
        relation_text = f"Confirmed: reduced candidate output for {case.case_id} = q^{q_shift} J_2({case.case_id}; q^2)."
        status = "confirmed"
    else:
        relation_text = (
            f"Under verification: with the current direct q -> q^2 comparison and braid representative for {case.case_id}, "
            "no pure q-shift has been confirmed yet."
        )
        status = "under_verification"

    return Sl2ThreeDimKnotAtlasCorrespondenceCheck(
        case_id=case.case_id,
        knot_label=case.knot_label,
        program_braid_label=case.program_braid_label,
        status=status,
        knot_atlas_reference=case.knot_atlas_reference,
        substituted_reference=substituted_reference,
        candidate_output=candidate_output,
        q_shift=q_shift,
        relation_text=relation_text,
        notes=case.notes,
        metadata={
            "comparison_rule": "q -> q^2",
            "comparison_scope": "direct_q_shift_only",
            "branch_status": SL2_3D_BRANCH_STATUS,
        },
    )


def evaluate_sl2_3d_knot_atlas_correspondence(
    *,
    q: sp.Expr | None = None,
) -> tuple[Sl2ThreeDimKnotAtlasCorrespondenceCheck, ...]:
    """Evaluate all current Knot Atlas correspondence checks for the sl2 3D candidate branch."""

    parameter = q if q is not None else _Q_SYMBOL
    return tuple(
        compute_sl2_3d_knot_atlas_correspondence(case.case_id, q=parameter)
        for case in get_sl2_3d_knot_atlas_reference_cases()
    )


@dataclass(frozen=True, slots=True)
class Sl2ThreeDimCandidateResult:
    """Store the current candidate normalization data for the sl2 3-dimensional branch."""

    representation_name: str
    braid_word: BraidWord
    raw_trace: sp.Expr
    quantum_trace_before_normalization: sp.Expr
    unreduced_candidate_output: sp.Expr
    unknot_normalization: sp.Expr
    reduced_candidate_output: sp.Expr
    candidate_output_label: str
    variable_convention: str
    status: str
    notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def summary(self) -> str:
        lines = [
            f"Representation: {self.representation_name}",
            f"Braid word: {self.braid_word.word_string()}",
            f"Status: {self.status}",
            f"Raw trace: {sp.simplify(self.raw_trace)}",
            f"Quantum trace before normalization: {sp.simplify(self.quantum_trace_before_normalization)}",
            f"Unreduced candidate output: {sp.simplify(self.unreduced_candidate_output)}",
            f"Unknot normalization: {sp.simplify(self.unknot_normalization)}",
            f"Reduced candidate output: {sp.simplify(self.reduced_candidate_output)}",
            f"Candidate output label: {self.candidate_output_label}",
            f"Variable convention: {self.variable_convention}",
        ]
        if self.notes:
            lines.append(f"Notes: {self.notes}")
        if self.metadata:
            lines.append(f"Metadata: {self.metadata}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        return {
            "representation_name": self.representation_name,
            "braid_word": self.braid_word.to_dict(),
            "raw_trace": str(sp.simplify(self.raw_trace)),
            "quantum_trace_before_normalization": str(sp.simplify(self.quantum_trace_before_normalization)),
            "unreduced_candidate_output": str(sp.simplify(self.unreduced_candidate_output)),
            "unknot_normalization": str(sp.simplify(self.unknot_normalization)),
            "reduced_candidate_output": str(sp.simplify(self.reduced_candidate_output)),
            "candidate_output_label": self.candidate_output_label,
            "variable_convention": self.variable_convention,
            "status": self.status,
            "notes": self.notes,
            "metadata": dict(self.metadata),
        }

    def to_string(self) -> str:
        return self.summary()


def _tensor_power(matrix: sp.Matrix, power: int) -> sp.Matrix:
    if power < 1:
        raise ValueError("Tensor power is only defined here for positive integers")

    result = matrix
    for _ in range(1, power):
        result = sp.kronecker_product(result, matrix)
    return result


def _coerce_sl2_3d_operator_data(
    braid: BraidWord | BraidOperatorData,
    *,
    q: sp.Expr,
) -> BraidOperatorData:
    if isinstance(braid, BraidOperatorData):
        return braid
    rmatrix = build_sl2_spin1_rmatrix(q)
    return BraidOperatorBuilder(braid_word=braid, rmatrix=rmatrix).build()


def current_sl2_3d_candidate_mu(q: sp.Expr | None = None) -> sp.Matrix:
    """Return the current candidate quantum-trace weight for the sl2 3-dimensional branch."""

    parameter = q if q is not None else sp.Symbol("q", nonzero=True)
    return sp.diag(parameter**-2, sp.Integer(1), parameter**2)


def current_sl2_3d_candidate_alpha(q: sp.Expr | None = None) -> sp.Expr:
    """Return the current candidate framing scalar for the sl2 3-dimensional branch."""

    parameter = q if q is not None else sp.Symbol("q", nonzero=True)
    return sp.simplify(parameter**4)


def current_sl2_3d_candidate_beta(q: sp.Expr | None = None) -> sp.Expr:
    """Return the current candidate beta scalar for the sl2 3-dimensional branch."""

    _ = q if q is not None else sp.Symbol("q", nonzero=True)
    return sp.Integer(1)


def compute_sl2_3d_candidate_unreduced_output(
    braid: BraidWord | BraidOperatorData,
    *,
    q: sp.Expr | None = None,
) -> tuple[BraidOperatorData, sp.Expr, sp.Expr, sp.Expr]:
    """Return operator data, raw trace, quantum trace, and candidate unreduced output."""

    parameter = q if q is not None else sp.Symbol("q", nonzero=True)
    operator_data = _coerce_sl2_3d_operator_data(braid, q=parameter)
    raw_result = compute_raw_closure_trace(operator_data)
    mu = current_sl2_3d_candidate_mu(parameter)
    mu_tensor_power = _tensor_power(mu, operator_data.num_strands)
    quantum_trace = sp.simplify(sp.trace(operator_data.operator * mu_tensor_power))
    alpha = current_sl2_3d_candidate_alpha(parameter)
    beta = current_sl2_3d_candidate_beta(parameter)
    unreduced_candidate = sp.simplify(
        alpha ** (-operator_data.writhe)
        * beta ** (-operator_data.num_strands)
        * quantum_trace
    )
    return operator_data, sp.simplify(raw_result.raw_closure_trace), quantum_trace, unreduced_candidate


def current_sl2_3d_unknot_normalization(q: sp.Expr | None = None) -> sp.Expr:
    """Return the current candidate unreduced value on the 1-strand unknot."""

    parameter = q if q is not None else sp.Symbol("q", nonzero=True)
    braid_word = get_braid_example("unknot_1").to_braid_word()
    _operator_data, _raw_trace, _quantum_trace, unreduced_candidate = compute_sl2_3d_candidate_unreduced_output(
        braid_word,
        q=parameter,
    )
    return sp.simplify(unreduced_candidate)


def compute_sl2_3d_candidate_output(
    braid: BraidWord | BraidOperatorData,
    *,
    q: sp.Expr | None = None,
) -> Sl2ThreeDimCandidateResult:
    """Return the current candidate colored-Jones-style output layer for the sl2 3-dimensional branch."""

    parameter = q if q is not None else sp.Symbol("q", nonzero=True)
    operator_data, raw_trace, quantum_trace, unreduced_candidate = compute_sl2_3d_candidate_unreduced_output(
        braid,
        q=parameter,
    )
    unknot_normalization = current_sl2_3d_unknot_normalization(parameter)
    reduced_candidate = sp.simplify(unreduced_candidate / unknot_normalization)
    alpha = current_sl2_3d_candidate_alpha(parameter)

    return Sl2ThreeDimCandidateResult(
        representation_name=SL2_3D_USER_FACING_NAME,
        braid_word=operator_data.braid_word,
        raw_trace=raw_trace,
        quantum_trace_before_normalization=quantum_trace,
        unreduced_candidate_output=unreduced_candidate,
        unknot_normalization=unknot_normalization,
        reduced_candidate_output=reduced_candidate,
        candidate_output_label=SL2_3D_CANDIDATE_OUTPUT_LABEL,
        variable_convention=SL2_3D_VARIABLE_CONVENTION,
        status=SL2_3D_BRANCH_STATUS,
        notes=(
            "This branch is no longer kept at ordinary trace only. It now applies a candidate RT-style "
            "quantum trace with mu = diag(q^-2, 1, q^2), followed by a candidate framing correction using "
            f"alpha = {sp.simplify(alpha)} and reduction by the current unknot value. "
            "It should be read as a colored Jones candidate branch rather than as a theorem-level final branch. "
            + SL2_3D_KNOT_ATLAS_COMPARISON_RULE
            + " "
            + SL2_3D_KNOT_ATLAS_TREFOIL_RELATION
            + " "
            + SL2_3D_KNOT_ATLAS_SCOPE_NOTE
        ),
        metadata={
            "branch": "sl2_spin1",
            "user_facing_branch_name": SL2_3D_USER_FACING_NAME,
            "trace_mode": "ordinary_trace + candidate_quantum_trace",
            "mu": [str(entry) for entry in current_sl2_3d_candidate_mu(parameter).diagonal()],
            "alpha": str(sp.simplify(alpha)),
            "beta": str(current_sl2_3d_candidate_beta(parameter)),
            "normalization_kind": "RT / quantum-trace candidate normalization reduced by current unknot value",
            "knot_atlas_comparison_rule": SL2_3D_KNOT_ATLAS_COMPARISON_RULE,
            "knot_atlas_trefoil_relation": SL2_3D_KNOT_ATLAS_TREFOIL_RELATION,
            "knot_atlas_five_one_relation": SL2_3D_KNOT_ATLAS_FIVE_ONE_RELATION,
            "knot_atlas_scope_note": SL2_3D_KNOT_ATLAS_SCOPE_NOTE,
            "knot_atlas_verification_note": SL2_3D_KNOT_ATLAS_VERIFICATION_NOTE,
        },
    )