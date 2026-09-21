# Observed Mathematical Conventions

Last updated: 2026-09-21

This document records only conventions evidenced by `archive/report_bundle.zip`. It does not fill gaps by inference. The evaluator modules that define the braid representations, R-matrices, traces, and invariant normalizations are missing from the snapshot.

## Braid representation

- A braid side is stored as `num_strands` plus an ordered list of signed integers called `generators`.
- The data labels `[1, 1, 1, 1, 1]` on two strands as the closure of `sigma_1^5`.
- Generator order is preserved exactly as listed; no commutation, cancellation, conjugation, or braid-relation simplification occurs in the recovered benchmark layer.
- The maximum permitted index and the meaning of the sign are delegated to the missing `BraidWord.from_iterable` implementation.
- Stored audits report writhe as the sum of generator signs: for example, five `1` entries give writhe 5, `[1, 1, 1, 1, 1, -2]` gives 4, and the two P03 words both give 1.

### Unresolved sign/orientation ambiguity

P01 side B is described as a “Positive stabilization candidate of 5_1”, but its added generator is `-2` and its stored writhe decreases from 5 to 4. Without `BraidWord` and the branch evaluators, the archive does not establish whether positive integers mean positive crossings in the conventional geometric sense. Do not rename or invert generators until that source is recovered.

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

## Normalizations that cannot be recovered

The snapshot provides branch names and final SymPy expressions but no implementation or derivation for any of the following:

- braid-generator orientation/sign convention;
- R-matrix entries or normalization;
- tensor-factor ordering;
- Markov trace normalization;
- framing/writhe correction;
- eigenvalue ordering;
- Laurent-polynomial variable or normalization convention;
- the precise relationship between `sl2_3d_9x9` and the internal `sl2_spin1` branch.

No claim about those conventions should be added until the missing evaluator source or equivalent primary evidence is recovered. Future implementations must treat the exact stored baselines as compatibility evidence, while recognizing that P01/P04 expose unresolved convention or input issues rather than authoritative invariant values.
