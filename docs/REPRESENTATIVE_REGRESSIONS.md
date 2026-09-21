# Representative Invariant Regression Manifest

`tests/fixtures/representative_invariant_regressions.json` is the compact,
machine-readable compatibility contract for representative outputs of the
authoritative recovered implementation. Each case records the catalog label,
the corresponding strand count and ordered signed generator word, branch, q
mode, expected SymPy expression, branch status, and provenance.

The manifest is an implementation regression baseline only. It is not a new
external theorem or literature reference. In particular, the `sl2_spin1`
entries remain explicitly `candidate` values; they must not be presented as a
final colored-Jones normalization. The `sl2_fundamental` and
`sl3_fundamental` entries are marked `formal` only in the sense already
established by the recovered program and described in
`docs/MATH_CONVENTIONS.md`.

The q=2 cases cover every required catalog example (`unknot_1`, `unlink_2`,
`unknot_2`, `hopf_link`, `trefoil`, `figure_eight`, and
`three_strand_trefoil`) across all current branch evaluators. They belong to
the fast tier. The symbolic `sl2_fundamental` cases for the unknot, trefoil,
and figure-eight are kept in the extended tier. The manifest also records the
two formal q=2 trefoil-presentation comparisons which the recovered program
currently supports. It deliberately does not assert the same relation for the
candidate branch.

Expressions are compared using `sympy.simplify(actual - expected) == 0`, so
the JSON remains readable while retaining symbolic equivalence. The catalog
metadata is also checked before evaluation, ensuring the contract does not
silently drift to a different braid presentation.
