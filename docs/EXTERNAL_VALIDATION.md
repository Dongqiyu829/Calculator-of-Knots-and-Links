# External Knot Atlas Validation

Last updated: 2026-09-22

This suite treats Knot Atlas as an independent external oracle. It does not
define the project's mathematics and it must never be used as a reason to alter
a built-in R-matrix, trace, framing factor, generator order, or normalization.
The offline source snapshot is
`tests/fixtures/knot_atlas_oracles.json`.

## Sources and provenance

The fixture was transcribed on 2026-09-22 from the Knot Atlas pages for
[`3_1`](https://katlas.org/wiki/3_1),
[`4_1`](https://katlas.org/wiki/4_1),
[`5_1`](https://katlas.org/wiki/5_1),
[`5_2`](https://katlas.org/wiki/5_2), and
[`6_1`](https://katlas.org/wiki/6_1). Each record retains its source URL,
retrieval date, minimum `BR` presentation, Jones polynomial, A2 fundamental
polynomial, A1 weight-2 polynomial, provenance, and status. The
[KnotTheory manual](https://katlas.org/wiki/Printable_Manual) states that a
positive `BR` index is a right-handed crossing and a negative index is a
left-handed crossing.

The JSON fixture is intentionally offline and reviewable. Tests never scrape
the network.

## Calibrated braid and variable conventions

The Atlas braid cannot be copied directly into the project. Exact Jones checks
on `3_1`, `4_1`, `5_1`, and `5_2` establish

`project_generator = -atlas_generator`.

This is a multi-knot calibration. The identity sign map fails `3_1`, `5_1`, and
`5_2`; `4_1` alone cannot choose a sign because the figure-eight is
amphicheiral. The project convention itself is unchanged: positive project
integers still mean positive Artin generators, and negative integers still use
the inverse check-R operator.

Variable maps are branch-specific:

- Jones / sl2 fundamental: `q_atlas = q_project^2`.
- A2 / sl3 fundamental: `q_atlas = q_project^-1`.

One substitution is not forced across differently normalized Atlas tables.
With the calibrated braid sign, the Jones rule is exact for all five fixture
knots, including `6_1`, and the A2 rule is exact for `3_1`, `4_1`, `5_1`, and
`5_2`. The Jones suite also evaluates direct `q_project=2` and `3` spot checks.

The catalog `trefoil`, `three_strand_trefoil`, and `figure_eight`
presentations agree with their calibrated Atlas Jones values. In particular,
the two- and three-strand trefoil presentations provide a presentation-change
check rather than merely repeating the Atlas braid.

## A1 weight 2 / sl2 spin-1 status

Knot Atlas labels A1 weight 2 as the three-dimensional representation, so it
is the appropriate external comparison target for the current spin-1/9x9
candidate branch. Direct checks for `3_1`, `5_1`, and `5_2` find no equality
under any single tested substitution
`q_atlas in {q_project, q_project^-1, q_project^2, q_project^-2}` plus a pure
monomial shift. That result is a diagnostic mismatch, not permission to change
the implementation.

This also exposes a provenance discrepancy in the recovered candidate helper:
its older stored expressions and statements such as `q^6 J_2(3_1; q^2)` are
not the A1 weight-2 table entries transcribed by this independent suite. Those
historical checks remain compatibility evidence. The external fixture is kept
separate, and the branch remains explicitly `candidate`; no theorem-level
colored-Jones convention is frozen here.

## Custom check-R parity and negative controls

For the calibrated `3_1`, `4_1`, and `5_2` braids at `q=2`, the custom
check-R service produces the same global operator as the built-in sl2
fundamental `BraidOperatorBuilder`. A symbolic trefoil check gives the same
result. This validates operator plumbing only; the custom service still makes
no trace or link-invariant claim.

Negative controls ensure that the suite can fail for the intended reasons:

- the un-negated Atlas braid signs fail the chiral calibration set;
- an altered Jones coefficient fails exact comparison;
- singular custom matrices remain unusable for inverse generators in the
  custom-service contract tests; and
- the square, tensor-dimension-valid, invertible matrix
  `diag(1,2,3,4)` explicitly reports
  `check_r_braid_relation_satisfied == false`. Its structural validity does
  not make it a verified braid-group representation.

## Running the suite

Run the fast oracle and parity checks with:

```text
python -m pytest -q tests/test_knot_atlas_external_oracles.py -m "not slow"
```

Run the more expensive symbolic A1 weight-2 diagnostic with:

```text
python -m pytest -q tests/test_knot_atlas_external_oracles.py
```

Hard regressions and candidate diagnostics are deliberately separated. A
future mathematical change must explain an oracle discrepancy; it must not
silently rewrite this fixture or the representative compatibility fixture.
