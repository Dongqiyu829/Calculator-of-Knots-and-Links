# Custom R/check-R Braid Operator Engine

This engine constructs braid-group representation matrices from user-supplied
local matrices. It does **not** claim that an arbitrary matrix defines a knot or
link invariant. It adds no quantum trace, enhancement, Markov normalization,
framing correction, or polynomial normalization.

## Explicit input convention

Callers must set `input_kind` to exactly `R` or `check-R`; the engine never
guesses from matrix entries.

- `check-R` input is used directly as the local Artin-generator operator.
- `R` input is converted by `check-R = P R`.
- `P` is the tensor swap `P(e_i tensor e_j) = e_j tensor e_i` on the
  lexicographically ordered basis `(e_0 tensor e_0, e_0 tensor e_1, ...)`.

These rules match the established built-in convention without changing any
built-in provider.

## Braid construction

For a braid on `n` strands with local dimension `d`, generator `sigma_i` is
embedded as

`I^(i-1) tensor check-R tensor I^(n-i-1)`.

Positive integers denote positive Artin generators. Negative integers use the
inverse of the same embedded `check-R`; a singular matrix therefore supports
positive words but fails cleanly when an inverse is requested. Embedded factors
are multiplied from left to right in the exact order stored in
`BraidWord.generators`. Tensor-product bases use induced lexicographic order.

## Validation

`validate_custom_matrix` returns `ApplicationCustomMatrixValidation` rather
than raising for mathematical validation failures. It reports square shape,
inferred/explicit local dimension consistency, invertibility, errors, and
warnings. Relation checks are opt-in because symbolic matrices can be costly:

- `check_braid_relation=True` tests
  `check-R_12 check-R_23 check-R_12 = check-R_23 check-R_12 check-R_23`.
- `check_standard_r_ybe=True` is available only for explicit raw `R` input and
  tests `R_12 R_13 R_23 = R_23 R_13 R_12`.

The two statuses remain distinct in all application DTOs. Simplification can be
disabled for validation and operator construction. Operator dimensions above
1024 produce a warning because tensor growth can be expensive.

## Application API

Use the `src.services` facade:

1. `parse_custom_matrix` accepts rectangular nested numeric/SymPy data or
   SymPy-compatible text.
2. `validate_custom_matrix` performs requested structured checks.
3. `build_custom_rmatrix_model` creates a validated application model.
4. `evaluate_custom_braid_operator` accepts a validated `BraidWord` and returns
   `ApplicationCustomBraidOperatorResult`.
5. `serialize_custom_braid_operator_result` returns deterministic JSON.

The result records the explicit input kind, local dimension, braid word,
operator dimensions and entries, ordered generator diagnostics, relation and
invertibility statuses, and warnings. PySide6 code should use only this service
surface, not `src.rmatrix.custom_rmatrix`.

## PySide6 workflow

The maintained desktop application exposes this engine in the **Custom
R/check-R operator** tab. The user must select `R` or `check-R` explicitly;
the initial selector intentionally has no mathematical default. The tab accepts
matrix text (or text/JSON file contents), an auto-inferred or explicitly
validated local dimension, optional relation checks, strand count, and signed
generator text. It renders structured validation, operator dimensions, matrix
entries, diagnostics, warnings, and deterministic copy/export JSON.

Validation and operator construction run in a Qt worker thread. Negative
generators visibly warn that an invertible `check-R` is required; the service
remains responsible for the definitive failure if an inverse is requested from
a singular matrix. The UI estimates tensor growth before construction and
repeats the operator-only / non-invariant boundary in its results.
