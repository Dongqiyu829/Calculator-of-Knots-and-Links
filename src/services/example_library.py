"""Curated, user-facing examples built from existing project evidence."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .branch_catalog import list_evaluation_branches
from .catalog_examples import list_catalog_examples
from .errors import ApplicationServiceError
from .projects import ApplicationProjectDocument, build_custom_rmatrix_project, build_invariant_project


CURATED_CATEGORIES = ("knots_links", "braid_demonstration", "custom_rmatrix")
CURATED_STATUSES = ("formal", "candidate", "diagnostic", "negative_control")


@dataclass(frozen=True, slots=True)
class CuratedExample:
    """A searchable preset that can populate one maintained workflow."""

    example_id: str
    display_name: str
    category: str
    description: str
    workflow: str
    mathematical_status: str
    provenance: str
    tags: tuple[str, ...] = ()
    source_mode: str = "custom"
    example_label: str = ""
    num_strands: int = 1
    generators: tuple[int, ...] = ()
    custom_label: str = "custom_braid"
    custom_notes: str = ""
    recommended_q: str = "2"
    recommended_branches: tuple[str, ...] = ()
    input_kind: str | None = None
    matrix_text: str | None = None
    local_dimension: int | None = None
    check_braid_relation: bool = False
    check_standard_r_ybe: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def generator_text(self) -> str:
        return " ".join(str(value) for value in self.generators)

    def to_dict(self) -> dict[str, Any]:
        return {
            "example_id": self.example_id,
            "display_name": self.display_name,
            "category": self.category,
            "description": self.description,
            "workflow": self.workflow,
            "mathematical_status": self.mathematical_status,
            "provenance": self.provenance,
            "tags": list(self.tags),
            "source_mode": self.source_mode,
            "example_label": self.example_label,
            "num_strands": self.num_strands,
            "generators": list(self.generators),
            "generator_text": self.generator_text,
            "custom_label": self.custom_label,
            "custom_notes": self.custom_notes,
            "recommended_q": self.recommended_q,
            "recommended_branches": list(self.recommended_branches),
            "input_kind": self.input_kind,
            "matrix_text": self.matrix_text,
            "local_dimension": self.local_dimension,
            "check_braid_relation": self.check_braid_relation,
            "check_standard_r_ybe": self.check_standard_r_ybe,
            "metadata": dict(self.metadata),
        }

    def build_project(self) -> ApplicationProjectDocument:
        """Create a validated setup document without evaluating it."""

        if self.workflow == "invariant":
            return build_invariant_project(
                source_mode=self.source_mode,
                example_label=self.example_label,
                num_strands=self.num_strands,
                generator_text=self.generator_text,
                custom_label=self.custom_label,
                custom_notes=self.custom_notes,
                q_text=self.recommended_q,
                branch_ids=self.recommended_branches,
                ui_state={
                    "curated_example_id": self.example_id,
                    "curated_example_status": self.mathematical_status,
                    "curated_example_provenance": self.provenance,
                },
            )
        if self.workflow == "custom_rmatrix" and self.matrix_text is not None and self.input_kind is not None:
            return build_custom_rmatrix_project(
                matrix_text=self.matrix_text,
                input_kind=self.input_kind,
                local_dimension=self.local_dimension,
                check_braid_relation=self.check_braid_relation,
                check_standard_r_ybe=self.check_standard_r_ybe,
                num_strands=self.num_strands,
                generator_text=self.generator_text,
                ui_state={
                    "curated_example_id": self.example_id,
                    "curated_example_status": self.mathematical_status,
                    "curated_example_provenance": self.provenance,
                },
            )
        raise ApplicationServiceError(f"Curated example '{self.example_id}' has incomplete workflow data.")


def _default_branches() -> tuple[str, ...]:
    return tuple(descriptor.branch_id for descriptor in list_evaluation_branches())


def _catalog_examples() -> tuple[CuratedExample, ...]:
    result: list[CuratedExample] = []
    catalog_metadata = {item.label: item for item in list_catalog_examples()}
    descriptions = {
        "unknot_1": "The one-strand identity closure used to anchor normalization.",
        "unlink_2": "The two-strand identity closure giving the 2-component unlink.",
        "unknot_2": "The one-crossing T(2,1) presentation of the unknot.",
        "hopf_link": "The standard positive Hopf link closure of sigma_1^2.",
        "trefoil": "The standard positive 2-strand trefoil T(2,3).",
        "figure_eight": "The externally calibrated 3-braid figure-eight word.",
        "unlink_3": "The three-strand identity closure giving the 3-component unlink.",
        "three_strand_trefoil": "The T(3,2) three-strand trefoil presentation.",
    }
    for label, item in catalog_metadata.items():
        result.append(
            CuratedExample(
                example_id=f"catalog.{label}",
                display_name=label.replace("_", " ").title(),
                category="knots_links",
                description=descriptions.get(label, item.notes),
                workflow="invariant",
                mathematical_status="formal",
                provenance="Recovered maintained catalog; braid representative and project sign convention are frozen by source and regressions.",
                tags=("catalog", label),
                source_mode="catalog",
                example_label=label,
                num_strands=item.num_strands,
                generators=tuple(item.generators),
                custom_label=label,
                custom_notes=item.notes,
                recommended_branches=_default_branches(),
                metadata={
                    "expected_components": item.expected_components,
                    "expected_crossing_count": item.expected_crossing_count,
                    "branch_statuses": {descriptor.branch_id: descriptor.status for descriptor in list_evaluation_branches()},
                    **item.metadata,
                },
            )
        )
    return tuple(result)


def _evidence_examples() -> tuple[CuratedExample, ...]:
    branch_ids = _default_branches()
    return (
        CuratedExample(
            example_id="candidate.trefoil_spin1",
            display_name="Trefoil — spin-1 candidate branch",
            category="knots_links",
            description="The maintained trefoil setup narrowed to the explicitly candidate sl2 spin-1 branch.",
            workflow="invariant",
            mathematical_status="candidate",
            provenance="Recovered sl2_spin1 branch and candidate-status documentation; no normalization claim is upgraded.",
            tags=("trefoil", "candidate", "spin-1", "sl2"),
            source_mode="catalog",
            example_label="trefoil",
            num_strands=2,
            generators=(1, 1, 1),
            custom_label="trefoil_spin1_candidate",
            recommended_branches=("sl2_spin1",),
            metadata={"branch_status": "candidate"},
        ),
        CuratedExample(
            example_id="knot.5_1",
            display_name="Cinquefoil (5_1)",
            category="knots_links",
            description="Externally calibrated project-side T(2,5) representative.",
            workflow="invariant",
            mathematical_status="formal",
            provenance="Knot Atlas 5_1 minimum braid mapped by project_generator = -atlas_generator; exact Jones/A2 fixture.",
            tags=("knot", "5_1", "knot-atlas", "calibrated"),
            num_strands=2,
            generators=(1, 1, 1, 1, 1),
            custom_label="5_1_cinquefoil",
            custom_notes="Closure of sigma_1^5; project-side braid from the calibrated Knot Atlas map.",
            recommended_branches=branch_ids,
            metadata={"knot_label": "5_1", "source_url": "https://katlas.org/wiki/5_1"},
        ),
        CuratedExample(
            example_id="knot.5_2",
            display_name="Knot 5_2 (calibrated diagnostic)",
            category="knots_links",
            description="Calibrated project-side 5_2 braid; candidate colored branch remains under verification.",
            workflow="invariant",
            mathematical_status="diagnostic",
            provenance="Knot Atlas 5_2 minimum braid mapped by project_generator = -atlas_generator; project representative is fixture-backed.",
            tags=("knot", "5_2", "knot-atlas", "under-verification"),
            num_strands=3,
            generators=(1, 1, 1, 2, -1, 2),
            custom_label="5_2",
            custom_notes="The project-side braid is fixed for Jones/A2 validation; the sl2 spin-1 branch remains candidate.",
            recommended_branches=branch_ids,
            metadata={"knot_label": "5_2", "source_url": "https://katlas.org/wiki/5_2", "candidate_status": "under_verification"},
        ),
        CuratedExample(
            example_id="braid.5_1_negative_stabilization",
            display_name="5_1 negative stabilization audit",
            category="braid_demonstration",
            description="Benchmark audit presentation; the added -2 is negative under project conventions.",
            workflow="invariant",
            mathematical_status="diagnostic",
            provenance="Recovered P01 benchmark audit; retained label/status because source documents a convention discrepancy.",
            tags=("braid", "stabilization", "negative", "audit"),
            num_strands=3,
            generators=(1, 1, 1, 1, 1, -2),
            custom_label="5_1_stabilized",
            custom_notes="Audit only; historical metadata calls this positive stabilization, but project writhe/sign evidence makes it negative.",
            recommended_branches=branch_ids,
            metadata={"audit_case": "P01", "status": "diagnostic"},
        ),
        CuratedExample(
            example_id="braid.positive_generator",
            display_name="Positive generator sigma_1",
            category="braid_demonstration",
            description="Minimal +1 Artin generator demonstration.",
            workflow="invariant",
            mathematical_status="diagnostic",
            provenance="Project-native BraidWord convention and service parser.",
            tags=("braid", "positive", "sigma_1"),
            num_strands=2,
            generators=(1,),
            custom_label="positive_generator",
            recommended_branches=branch_ids,
        ),
        CuratedExample(
            example_id="braid.negative_generator",
            display_name="Negative generator sigma_1^-1",
            category="braid_demonstration",
            description="Minimal -1 inverse-generator demonstration.",
            workflow="invariant",
            mathematical_status="diagnostic",
            provenance="Project-native BraidWord convention and service parser.",
            tags=("braid", "negative", "inverse"),
            num_strands=2,
            generators=(-1,),
            custom_label="negative_generator",
            recommended_branches=branch_ids,
        ),
        CuratedExample(
            example_id="braid.mixed_sign",
            display_name="Mixed-sign braid",
            category="braid_demonstration",
            description="A short word that keeps positive and negative generators in listed order.",
            workflow="invariant",
            mathematical_status="diagnostic",
            provenance="Project-native Artin input demonstration; no external invariant claim.",
            tags=("braid", "mixed-sign", "ordering"),
            num_strands=3,
            generators=(1, -2, 1),
            custom_label="mixed_sign_braid",
            recommended_branches=branch_ids,
        ),
        CuratedExample(
            example_id="braid.identity",
            display_name="Identity braid",
            category="braid_demonstration",
            description="One-strand identity setup for preview and project-file smoke checks.",
            workflow="invariant",
            mathematical_status="formal",
            provenance="Recovered BraidWord identity validation.",
            tags=("braid", "identity", "one-strand"),
            source_mode="custom",
            num_strands=1,
            generators=(),
            custom_label="identity",
            recommended_branches=branch_ids,
        ),
    )


def _custom_matrix_examples() -> tuple[CuratedExample, ...]:
    return (
        CuratedExample(
            example_id="rmatrix.sl2_fundamental_check_r",
            display_name="sl2 fundamental check-R",
            category="custom_rmatrix",
            description="Recovered sl2 fundamental braid generator reused through the custom operator service.",
            workflow="custom_rmatrix",
            mathematical_status="diagnostic",
            provenance="Recovered src.rmatrix.sl2_rmatrix braid_matrix; custom engine constructs operators only, not invariants.",
            tags=("R-matrix", "check-R", "sl2", "symbolic"),
            num_strands=2,
            generators=(1, -1),
            input_kind="check-R",
            matrix_text="[[q,0,0,0],[0,0,1,0],[0,1,q - 1/q,0],[0,0,0,q]]",
            local_dimension=2,
            check_braid_relation=True,
        ),
        CuratedExample(
            example_id="rmatrix.identity_check_r",
            display_name="Numeric identity check-R",
            category="custom_rmatrix",
            description="Simple verified numeric check-R example for operator smoke tests.",
            workflow="custom_rmatrix",
            mathematical_status="diagnostic",
            provenance="Custom R/check-R service validation regression; no invariant normalization is applied.",
            tags=("R-matrix", "check-R", "numeric", "verified"),
            num_strands=2,
            generators=(1, -1),
            input_kind="check-R",
            matrix_text="[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]",
            local_dimension=2,
            check_braid_relation=True,
        ),
        CuratedExample(
            example_id="rmatrix.diagonal_negative_control",
            display_name="Diagonal relation-failure negative control",
            category="custom_rmatrix",
            description="Structurally valid invertible check-R whose braid relation fails; never a knot invariant.",
            workflow="custom_rmatrix",
            mathematical_status="negative_control",
            provenance="Maintained custom-R negative-control regression for relation status.",
            tags=("R-matrix", "check-R", "negative-control", "relation-failure"),
            num_strands=2,
            generators=(1,),
            input_kind="check-R",
            matrix_text="[[1,0,0,0],[0,2,0,0],[0,0,3,0],[0,0,0,4]]",
            local_dimension=2,
            check_braid_relation=True,
            metadata={"never_invariant": True},
        ),
    )


CURATED_EXAMPLES: tuple[CuratedExample, ...] = _catalog_examples() + _evidence_examples() + _custom_matrix_examples()


def list_curated_examples(*, category: str | None = None, search: str | None = None) -> tuple[CuratedExample, ...]:
    """Return stable-order examples filtered by category and free-text search."""

    if category is not None and category not in CURATED_CATEGORIES:
        return ()
    needle = (search or "").strip().casefold()
    result: list[CuratedExample] = []
    for example in CURATED_EXAMPLES:
        if category is not None and example.category != category:
            continue
        if needle:
            haystack = " ".join((example.example_id, example.display_name, example.description, example.provenance, *example.tags)).casefold()
            if needle not in haystack:
                continue
        result.append(example)
    return tuple(result)


def get_curated_example(example_id: str) -> CuratedExample:
    for example in CURATED_EXAMPLES:
        if example.example_id == example_id:
            return example
    raise ApplicationServiceError(f"Unknown curated example '{example_id}'.")


__all__ = [
    "CURATED_CATEGORIES",
    "CURATED_EXAMPLES",
    "CURATED_STATUSES",
    "CuratedExample",
    "get_curated_example",
    "list_curated_examples",
]
