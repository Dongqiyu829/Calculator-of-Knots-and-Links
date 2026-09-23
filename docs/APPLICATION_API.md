# Application Service API

`src.services` is the explicit, frontend-neutral application API. Maintained
frontends and workbench code import the names listed in `src.services.__all__`.
The intended direction is `braid / algebra / rmatrix / invariants / catalog ->
services -> GUI / workbench`.

`src.gui.demo_launcher_legacy` is a documented historical compatibility
exception: it retains direct catalog and formatter use to preserve recovered
behavior. It is not a model for M3 code.

## Stable frontend API for M3

The M3 contract consists of branch discovery (`list_evaluation_branches`,
`get_evaluation_model`, `get_evaluation_branch`,
`DEFAULT_EVALUATION_MODEL_IDS`, and `branch_ids_for_models`); built-in example
discovery (`ApplicationCatalogExample`, `list_catalog_examples`, and
`get_catalog_example`); input construction/parsing (`BraidInputState`,
`parse_generator_text`, `parse_q_text`, `build_catalog_braid_input`,
`build_custom_braid_word`, and `build_custom_braid_input`); result-returning
evaluation
(`evaluate_catalog_result`, `evaluate_braid_result`, `evaluate_custom_result`,
and `evaluate_braid_input_result`); result reporting
(`ApplicationBranchResult`, `ApplicationBraidResult`, filtering, formatting,
and serialization helpers); and all `ApplicationServiceError` subclasses.

`parse_q_text` is the maintained frontend boundary for invariant parameters. It
keeps integer and rational input exact, accepts the active symbolic `q`
convention and other SymPy expressions, and reports invalid text as a typed
service error rather than coercing it to floating point.

Built-in result-returning evaluation accepts `backend="explicit"` (the
unchanged default/reference) or `backend="matrix_free"` for scalar-only EYB
evaluation. The latter preserves primary output and formal/candidate status,
but returns no ordinary raw trace or full operator. The custom R/check-R
operator API is unaffected. See `docs/PERFORMANCE.md` for parity and timing.

The stable contract also includes a renderer-neutral braid-preview surface: `BraidPreviewGeometry`, `build_braid_preview_geometry`, and `render_braid_preview_svg`. Maintained desktop code consumes these through the `src.services` facade; the geometry preserves project-native Artin signs, generator order, writhe, strand identities, final permutation, and explicit over/under crossing semantics without changing evaluation behavior. Physical strands are exposed as continuous paths, while every intentional under-crossing gap is localized to a `BraidPreviewCrossing` mask/overpass description shared by both the SVG export and the Qt preview.

The stable contract also includes the custom braid-operator surface:
`parse_custom_matrix`, `validate_custom_matrix`,
`build_custom_rmatrix_model`, `evaluate_custom_braid_operator`, and
`serialize_custom_braid_operator_result`, together with their
`ApplicationCustom*` DTOs and specific errors. This API requires an explicit
`R` or `check-R` input kind and constructs operators only; it is not an
invariant recipe. See `docs/CUSTOM_RMATRIX_ENGINE.md`.

Catalog snapshots expose labels, braid data, display word, notes, expected
components/crossing count, and recovered display metadata without exposing
catalog objects. Result and catalog DTOs are frozen/read-only at the dataclass
field level; their metadata dictionaries deliberately are not recursively
immutable and callers must treat them as read-only. Service text reports are
the application report format, not byte-for-byte historical formatter
compatibility.

The service catalog is the sole frontend authority for branch/model mapping and
status facts. It records `sl2_fundamental` and `sl3_fundamental` as formal, and
maps `sl2_3d_9x9` to internal `sl2_spin1`, which remains candidate. It does not
change mathematical claims or `docs/MATH_CONVENTIONS.md`.

## Compatibility and internals

`evaluate_catalog_example`, `evaluate_braid_word`, `evaluate_custom_braid`,
`evaluate_braid_input`, and the `application_*_from_internal` converters remain
exported only for recovered Tkinter/test compatibility; new M3 code uses the
stable result-returning surface. Service submodules, catalog storage, invariant
evaluators, mathematical builders, R-matrices, normalization, and legacy
helpers such as `braid_word_from_entry` are implementation details.

## M5 curated examples and project files

The maintained desktop application also uses the frontend-neutral curated
example/project surface from `src.services`: `CuratedExample`,
`list_curated_examples`, `get_curated_example`, `ApplicationProjectDocument`,
`build_invariant_project`, `build_custom_rmatrix_project`, `serialize_project`,
`parse_project`, `save_project_file`, and `load_project_file`. These helpers
validate input through the existing braid, branch, q, and custom-matrix
parsers, preserve symbolic text and provenance/status metadata, and never run
an invariant or custom operator as a side effect of loading.

Project documents use `schema_version: 1`, identify either the `invariant` or
`custom_rmatrix` workflow, and contain setup state only. Application-version
mismatches are informational; unsupported schemas, workflows, malformed JSON,
invalid branch ids, braid generators, or matrix inputs raise typed `Project*Error`
subclasses. JSON serialization is UTF-8 and deterministic, with no pickle,
eval, or executable payloads.

## M5 explanations, documentation, and export boundaries

`MathematicalExplanation`, `get_branch_explanation`,
`build_invariant_explanation`, and `build_custom_rmatrix_explanation` provide
frontend-neutral explanation DTOs. Branch status and display names are derived
from the same `list_evaluation_branches` catalog used for evaluation; the
explanation layer is descriptive only and never evaluates an invariant or
constructs an operator. The custom workflow is explicitly `operator-only` and
states the separate structural, braid-relation, raw-R YBE, and knot-invariant
boundaries.

`DocumentationResource`, `list_documentation_resources`,
`documentation_resource_path`, and `read_documentation` identify the offline
Markdown resources used by the maintained Help viewer. The PyInstaller spec
bundles the user guide and mathematical implementation guide under `docs/`.

Result export continues to use `format_application_braid_result`,
`serialize_application_braid_result`, and
`serialize_custom_braid_operator_result`. Desktop workflow `export_result_to_path`
helpers only select a service serializer and write its deterministic output;
they do not reimplement mathematical formatting. Braid SVG/PNG export remains
available through the renderer-neutral preview service and its Qt view.

The maintained result-presentation layer also exposes compact frontend helpers
through `PolynomialPresentation`, `ApplicationBranchPresentation`,
`build_polynomial_presentation`, `build_application_branch_presentation`,
`format_application_branch_compact`, and
`format_application_braid_compact_result`. These descriptors sit above the
stored evaluation DTOs: they may relabel existing symbolic outputs into exact
standard/Atlas-comparable variable forms when the conversion is mathematically
unambiguous, but they do not mutate or truncate the underlying deterministic
JSON export.
