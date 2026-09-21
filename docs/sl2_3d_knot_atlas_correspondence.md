# sl2 3D Knot Atlas Correspondence

## Purpose

This note fixes the current wording for the sl2 3-dimensional 9x9 line.

The branch must still be called the colored Jones candidate branch. The goal here is not to claim that a theorem-level final colored Jones normalization has already been completed, but to state clearly what external correspondence is currently checked against Knot Atlas.

## Current comparison rule

Knot Atlas uses `J_n` for the `(n+1)`-dimensional `sl2` representation.

Therefore the current 3-dimensional sl2 branch in this project is compared against Knot Atlas `n=2` colored Jones data.

In the current program the braid-side variable is still called `q`, so the direct comparison rule is:

- take the Knot Atlas `J_2(K; q)` reference polynomial
- substitute `q -> q^2`
- check whether the current reduced candidate output matches `q^k J_2(K; q^2)` for some knot-dependent shift `k`

This is a calibrated correspondence statement, not a theorem-level final global normalization claim.

## Current verified cases

- `3_1`: `reduced candidate output = q^6 J_2(3_1; q^2)`
- `5_1`: `reduced candidate output = q^10 J_2(5_1; q^2)`

These are direct q-shift confirmations under the current braid-side variable convention.

## Current under-verification case

- `5_2`: the Knot Atlas `J_2` reference polynomial is fixed, but the project-side braid representative is not yet fixed in one final Artin-generator convention, so the case is currently reported as under verification

## Reproducibility

Run:

```bash
python examples/check_sl2_3d_knot_atlas_correspondence.py
```

This prints the shared wording and the current correspondence checks used by the project.