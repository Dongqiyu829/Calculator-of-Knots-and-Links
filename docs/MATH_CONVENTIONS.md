# Observed Mathematical Conventions

Last updated: 2026-09-22

This document records conventions evidenced by the recovered authoritative
source. The incomplete `archive/report_bundle.zip` supplied output evidence;
issue #5 supplied the implementations that resolve the earlier unknowns. This
is a recovery record, not an attempt to improve or reconcile the mathematics.

## Braid representation

- A braid side is stored as `num_strands` plus an ordered list of signed integers called `generators`.
- The data labels `[1, 1, 1, 1, 1]` on two strands as the closure of `sigma_1^5`.
- Generator order is preserved exactly as listed; no commutation, cancellation, conjugation, or braid-relation simplification occurs in the recovered benchmark layer.
- Positive `i` means `sigma_i`; negative `-i` means `sigma_i^-1`.
- A braid has at least one strand; a one-strand braid must be the identity;
  generator zero and indices greater than `num_strands - 1` are rejected.
- Stored audits report writhe as the sum of generator signs: for example, five `1` entries give writhe 5, `[1, 1, 1, 1, 1, -2]` gives 4, and the two P03 words both give 1.

### Historical sign-label discrepancy

P01 side B is described as a “Positive stabilization candidate of 5_1”, but its
added generator is `-2` and its stored writhe decreases from 5 to 4. The
recovered `BraidWord` and operator builder establish that `-2` uses the inverse
of the local braid matrix. P01 is therefore a negative stabilization under the
actual program convention. The historical data and label remain unchanged.

## Operator and basis conventions

- `RMatrixData.matrix` stores the raw literature-facing R matrix.
- `RMatrixData.braid_matrix` stores the local braid generator obtained as the
  tensor-factor swap times the raw matrix (`P R`).
- The global braid operator uses only `braid_matrix`; negative generators use
  its inverse.
- Embedded generators are multiplied from left to right in the order supplied
  by `BraidWord.generators`.
- Representation bases are ordered from highest to lowest weight. Tensor-product
  bases use the induced lexicographic order.

### Custom R/check-R inputs

The custom operator engine preserves these conventions without modifying the
built-in matrices. A caller must explicitly label input as raw `R` or braid
operator `check-R`; values are never inspected to guess the kind. Raw `R` is
converted by `check-R = P R`, where `P(v_i tensor v_j) = v_j tensor v_i` in the
lexicographic tensor basis. Custom braid generators use only `check-R`, negative
generators use its inverse, and word factors multiply left-to-right in listed
order. The check-R braid relation and standard raw-R YBE are separate optional
validation statuses. No custom matrix receives trace, Markov, framing, or
invariant normalization in this layer.

## R-matrix eigenvalue conventions

- sl2 fundamental: J=1/symmetric eigenvalue `q`; J=0/antisymmetric eigenvalue
  `-q^-1`.
- sl2 spin-1 (3D/9x9): on basis `(w_1,w_0,w_-1)` and its lexicographic tensor
  square, J=2 has `q^4`, J=1 has `-1`, and J=0 has `q^-2`.
- sl3 fundamental: the symmetric 6 has `q`; the antisymmetric 3-bar has
  `-q^-1`.

The source builds both sl2 cases from the same universal-R normalization. It
also explicitly marks the spin-1 channel normalization for future external
reference comparison; recovery does not upgrade that claim.

## Trace and invariant normalizations

The implemented EYB formula is
`alpha^-w beta^-n Tr(braid_operator * mu^(tensor n))`.

- sl2 fundamental uses `mu=diag(q^-1,q)`, `alpha=q^2`, and `beta=1`.
- sl3 fundamental uses `mu=diag(q^-2,1,q^2)`, `alpha=q^3`, and `beta=1`.
- The sl2 fundamental branch divides the current P2 expression by its
  one-strand unknot value. Its Jones variable convention is `t=q^-2`.
- The sl2 spin-1/3D branch uses `mu=diag(q^-2,1,q^2)`, `alpha=q^4`, and
  `beta=1`, then divides by its one-strand unknot value. It is intentionally
  labelled a candidate colored-Jones normalization, not a theorem-level final
  convention. Knot Atlas comparison substitutes `q -> q^2`.
- Ordinary raw closure trace is diagnostic output and is not Markov normalized.

### Derived sl2-fundamental Hecke / Temperley–Lieb calibration (issue #64)

This is derived from the maintained local `check-R` and EYB data above, not
adopted from a named textbook Jones convention. On the lexicographic basis
`(v_1 v_1, v_1 v_2, v_2 v_1, v_2 v_2)`, source evaluation gives

```text
check-R = [[q,0,0,0], [0,0,1,0], [0,1,q-q^-1,0], [0,0,0,q]]
E = q I - check-R
  = [[0,0,0,0], [0,q,-1,0], [0,-1,q^-1,0], [0,0,0,0]].
```

Its established eigenvalues `(q,-q^-1)` imply the Hecke relation
`(check-R-q I)(check-R+q^-1 I)=0`. Direct symbolic multiplication of this
source matrix gives `E^2=delta E` with `delta=q+q^-1`, and on three tensor
factors gives `E_1 E_2 E_1=E_1` and `E_2 E_1 E_2=E_2`. Thus the project-native
positive generator is `g_i=q I-E_i` and its inverse is
`g_i^-1=q^-1 I-E_i`; input factors remain left-to-right. No raw `R` is used.

The source enhancement is `mu=diag(q^-1,q)`, `alpha=q^2`, `beta=1`.
Directly, `Tr(mu)=delta` and
`Tr(E (mu tensor mu))=delta`; consequently the two-strand positive and
negative weighted closures are `q^2 delta` and `q^-2 delta` respectively.
For a planar TL diagram, close each top endpoint to its corresponding bottom
endpoint and assign `delta` per resulting loop. This trace has
`tau_n(1)=delta^n`, `tau_{n+1}(X tensor I)=delta tau_n(X)`, and
`tau_{n+1}((X tensor I) E_n)=tau_n(X)`. These are the closure rules calibrated
by the actual one- and two-strand source values, then checked against the
quantum-group reference on higher strands; they are not an independent
normalization assumption.

The resulting project Jones-compatible scalar is exactly
`J(beta)=q^(-2 writhe(beta)) tau_n(TL(beta))/delta`, matching the current
EYB expression divided by its one-strand unknot value. It sends the
one-strand identity to 1. The closure rules give positive stabilization
factor `q delta-1=q^2` and negative factor `q^-1 delta-1=q^-2` before the
`q^-2w` correction, so both cancel under the existing Artin sign convention.
The maintained Jones-variable presentation remains `t=q_project^-2`.

## Independent Knot Atlas calibration

The offline external-oracle suite documented in `docs/EXTERNAL_VALIDATION.md`
calibrates Knot Atlas minimum braids across `3_1`, `4_1`, `5_1`, and `5_2`.
Atlas generator signs must be globally negated before they are interpreted in
the project: `project_generator = -atlas_generator`. This does not redefine the
project's positive Artin generator; it is an explicit source-to-project map.

The exact Jones comparison uses `q_atlas = q_project^2`. The independent A2
fundamental comparison has a different coherent map,
`q_atlas = q_project^-1`. The Knot Atlas A1 weight-2 table does not currently
admit a coherent tested substitution and monomial shift for the sl2 spin-1
candidate branch. That mismatch preserves the candidate status and does not
change any built-in matrix or normalization. The recovered helper's older
`J_2` expressions are compatibility evidence, not the authoritative external
fixture used by this calibration.

## Fixed branch order and profile encoding

The benchmark layer fixes the comparison order as:

1. `sl2_fundamental` (`Jones / sl2 fundamental`)
2. `sl2_3d_9x9` (implemented by the missing branch ID `sl2_spin1`)
3. `sl3_fundamental`

Pair relations are encoded as:

- `same` -> `0`
- `different` -> `1`

Thus `(0,1,1)` means the first branch agrees and the two 9x9-labelled branches differ. If any branch is skipped, the whole observed profile is the string `skipped`.

## `q` handling and equality

- CLI text is parsed with `sympy.sympify`.
- The literal mode text `q` selects symbolic comparison.
- Symbolic equality is decided by testing `sympy.simplify(output_A - output_B) == 0`.
- Numeric modes simplify each output and then compare the resulting SymPy expressions with strict equality.
- The recorded numeric modes are `q=2`, `q=3`, and `q=5`.

The recovered layer does not constrain `q` to positive integers, roots of unity, or any other domain.

## Stored output baseline

The only mathematical results available for independent preservation are the generated artifacts inside the ZIP. Regression fixtures record their exact strings rather than converting them to floating point.

For P03 (`10_22` versus `10_35`):

| Mode | `sl2_fundamental` | `sl2_3d_9x9` | `sl3_fundamental` | Profile |
| --- | --- | --- | --- | --- |
| `q=2` | same | different | different | `(0,1,1)` |
| `q=3` | same | different | different | `(0,1,1)` |
| `q=5` | same | different | different | `(0,1,1)` |
| symbolic `q` audit | same | different | different | `(0,1,1)` by branch relations |

P01 and P04 must remain audit cases:

- P01 has stored profile `(0,1,0)` at `q=2`, `q=3`, and `q=5`, while its metadata expects `(0,0,0)`.
- P04 has stored profile `(1,1,1)` at those numeric values, while its metadata expects `(0,0,0)`.
- P05 is a placeholder and must be skipped because it is marked `needs_audit` and contains zero-strand, empty-generator inputs.

## Discrepancies from the pre-recovery document

The earlier version correctly left sign, operator, tensor, trace, eigenvalue, and
polynomial conventions unresolved because the ZIP lacked their source. The
authoritative files now establish the conventions above. Two caveats remain:

- `sl2_3d_9x9` is the benchmark-facing model ID for the internal
  `sl2_spin1` branch, whose normalization is expressly candidate status.
- P01 and P04 remain audit/metadata mismatches rather than validated invariant
  conclusions. No convention was changed to make their expected profiles pass.
