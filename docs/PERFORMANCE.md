# Built-in invariant performance (M6)

This is a measurement record, not a new mathematical convention. All times are
illustrative wall times, not CI thresholds. The reference backend remains the
quantum-group matrix implementation, with its established exact outputs.

## Reproduce

From the repository root, with the `test` dependencies installed:

```text
python -m tools.profile_invariants --case all
python -m tools.profile_invariants --case sl2_spin1_trefoil_symbolic --profile
python -m tools.profile_invariants --case all --repeat 2
python -m tools.profile_invariants --case all --repeat 2 --backend matrix_free
python -m tools.profile_invariants --case all --repeat 2 --backend temperley_lieb
```

`--case NAME` starts a fresh process for a cold comparison. `--profile` adds
the top cumulative cProfile functions; cProfile has substantial overhead, so
use unprofiled wall time for before/after comparisons. `--repeat 2` shows
first and warm-cache times in one process and asserts identical output text.
The harness reports branch, exact q mode, generator list/count, matrix dimension
`d^n`, branch status, and exact primary expression. It does not run in CI and
asserts no performance threshold.

## Baseline and measured change

Recorded on 2026-09-23 on Windows 11, Python 3.12.4, SymPy 1.12. The baseline
was taken from `origin/main` (`6d1fd9b`) before the changes in issue #55;
the after column is from the focused performance branch. The cases run in
the displayed order in one fresh process. CPU scheduling and SymPy internal
caches cause variation; these are single-run observations, not statistics.

| Branch / word | q | `d^n` | generators | Before (s) | After first (s) | After warm (s) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| sl2 fundamental / trefoil | symbolic | 4 | 3 | 0.403 | 0.215 | 0.059 |
| sl2 fundamental / trefoil | 2 | 4 | 3 | 0.021 | 0.004 | 0.002 |
| sl2 fundamental / figure-eight | symbolic | 8 | 4 | 0.374 | 0.146 | 0.085 |
| sl2 fundamental / figure-eight | 2 | 8 | 4 | 0.022 | 0.004 | 0.004 |
| sl3 fundamental / trefoil | symbolic | 9 | 3 | 0.767 | 0.089 | 0.048 |
| sl3 fundamental / trefoil | 2 | 9 | 3 | 0.045 | 0.009 | 0.004 |
| sl2 spin-1 / trefoil | symbolic | 9 | 3 | 13.292 | 4.721 | 0.257 |
| sl2 spin-1 / trefoil | 2 | 9 | 3 | 0.159 | 0.062 | 0.008 |
| sl2 fundamental / 5-strand `[1,2,3,4]` | symbolic | 32 | 4 | 0.282 | 0.079 | 0.062 |
| sl2 fundamental / 5-strand `[1,2,3,4]` | 2 | 32 | 4 | 0.043 | 0.028 | 0.030 |

All ten primary-output strings were identical before and after. The 5-strand
word is a moderate embedding control, not a difficult knot benchmark; its
closure is the unknot in this implementation. The q=2 cases guard against a
symbolic-only fast path.

## Hotspot analysis and phases

Cold `cProfile` on symbolic spin-1 trefoil showed 37.2 profiled seconds for
the branch evaluation (versus 13.3 unprofiled). `build_sl2_spin1_rmatrix`
was called **three times** and consumed 36.3 cumulative profiled seconds:
once for the branch's projector metadata, once for the braid, and once for
one-strand normalization. Within those overlapping cumulative totals,
projector construction consumed 14.2 s, projector-family checks 8.4 s, and
full YBE checks 11.7 s. The local R builder itself accounted for 21.4 s
cumulatively; the remaining measured time includes embedding, braid products,
weighted/raw trace, normalization and final simplification. These cProfile
figures overlap and must **not** be added together.

For symbolic sl3 trefoil, 2.21 of 2.46 profiled seconds were in local R
construction; its YBE checks consumed 1.08 s, projector construction 0.63 s,
and eigenvalue analysis 0.34 s (again overlapping). Generator embedding and
braid multiplication were not the dominant costs in these cases. `sp.simplify`
inside the repeated diagnostic/projector path dominated the call profile,
so removing that path from ordinary formal-branch execution is better supported
than changing algebra inside matrix multiplication. The harness retains full
function-level profiling for later cases; no precision is claimed for phase
costs below the profiler's call granularity.

## Implemented boundary and cache safety

- `build_sl2_fundamental_rmatrix` and `build_sl3_fundamental_rmatrix` retain
  their validated default. Built-in branch evaluation requests the same raw R
  and `check-R` matrices with `diagnostics=False`, skipping eigen/minpoly,
  projectors, and YBE. Direct research/test calls still get every diagnostic.
- The candidate spin-1 branch still uses the **validated** builder because its
  result metadata exposes `projector_checks`. It now builds that local data
  once, then reuses it for the braid and normalization rather than three times.
- One-strand normalization is cached as an immutable scalar. For the identity
  braid, `rho=I`, writhe is zero, and beta is one, so the old EYB/candidate
  pipeline exactly reduces to `Tr(mu)`. Equivalence tests compare against the
  original full one-strand pipelines at symbolic q and q=2.
- A bounded 32-entry local-data cache uses `(branch_id, exact SymPy q)` as its
  key. It returns deep copies, so callers cannot mutate cached matrix or
  metadata objects. The scalar unknot caches are bounded to 64 entries keyed
  by exact q. No floating-point approximations or value-based q coercion are
  introduced.
- The existing `BraidOperatorBuilder` already reuses each signed embedded
  generator and check-R inverse within one braid word. Cross-request embedded
  matrix caching was not added: the profiled representative cases did not
  justify retaining potentially large `d^n` matrices globally.
- Simplification in diagnostic builders is left intact. No inner-loop symbolic
  simplification or branch-specific canonicalization was changed without
  independent evidence. Full diagnostics and raw traces remain in results;
  no misleading primary-only service profile was introduced.

Exact-output tests include representative symbolic and numeric regressions,
the independent offline Knot Atlas oracles, local runtime-versus-validated
matrix equality, one-strand equivalence, candidate projector metadata, and
cache isolation. A future larger optimization must keep these constraints.

## Issue #60: opt-in matrix-free EYB scalar backend

The new `backend="matrix_free"` option on built-in `src.services` evaluation
functions contracts exact local signed `check-R` gates without constructing a
`d^n` by `d^n` operator. Each lexicographic input basis row is propagated
through the listed gates from left to right; only its closing diagonal entry
is retained and multiplied by that input state's diagonal `mu` weight. The
normalization remains exactly `alpha^-w beta^-n`. The inverse is the same
`simplify(check_R.inv())` used by the explicit builder. Non-diagonal `mu` is
rejected, since the built-in branches use diagonal enhancement data and a
non-diagonal weight would require a different contraction.

The result contains only the weighted scalar and normalized scalar. It does
not claim a full operator or ordinary raw closure trace. In service DTOs,
`raw_trace` is `None` and the notes identify the matrix-free path. The
explicit global-matrix backend remains the **default and reference path**,
including all existing diagnostics and Custom R/check-R full-operator calls.
This avoids changing existing diagnostic output while the opt-in path can be
used for scalar-only workloads. It is not a Temperley–Lieb or Hecke backend.

Exact parity tests compare the weighted trace and normalized scalar against
the explicit builder for all three branches at symbolic `q` and q=2/3/5,
one- to three-strand words, positive/inverse generators at both adjacent
placements, and the five-strand sl2 control. Service-level tests compare
all q=2 representative fixture strings, symbolic fixtures, and trefoil
outputs at q=3/5; formal/candidate statuses are unchanged. Existing archived
benchmark and offline Knot Atlas suites continue to exercise the explicit
reference backend. Additional slow matrix-free tests reproduce both sides of
the archived P03 benchmark at q=2/3/5 exactly and all three stored symbolic
P03 differences, including the six-strand spin-1 candidate side.

Measured on 2026-09-23, Windows 11, Python 3.12.4, SymPy 1.12. Each column
was produced by a fresh `--case all --repeat 2` process in the same case
order. “First” means first invocation within that process, not an independent
fresh process per row; later branch cases can benefit from SymPy/import caches.
Wall times are illustrative, not thresholds:

| Branch / word | q | Explicit first / warm (s) | Matrix-free first / warm (s) |
| --- | --- | ---: | ---: |
| sl2 fundamental / trefoil | symbolic | 0.208 / 0.058 | 0.157 / 0.018 |
| sl2 fundamental / figure-eight | symbolic | 0.149 / 0.087 | 0.053 / 0.027 |
| sl3 fundamental / trefoil | symbolic | 0.091 / 0.048 | 0.054 / 0.028 |
| sl2 spin-1 / trefoil | symbolic | 4.698 / 0.246 | 4.527 / 0.088 |
| sl2 fundamental / five-strand `[1,2,3,4]` | symbolic | 0.076 / 0.060 | 0.020 / 0.011 |
| sl2 fundamental / five-strand `[1,2,3,4]` | q=2 | 0.029 / 0.029 | 0.001 / 0.001 |
| sl3 fundamental / figure-eight | q=2 | 0.030 / 0.016 | 0.034 / 0.003 |
| sl2 spin-1 / figure-eight | q=2 | 0.113 / 0.025 | 0.084 / 0.003 |

The spin-1 cold call remains dominated by validated local projector/R data;
matrix-free contraction does not remove that cost. Sparse row propagation
avoids the global matrix but still enumerates up to `d^n` input basis states,
so it is not a polynomial-complexity solution for arbitrarily many strands.
The sl3 q=2 figure-eight cold sample regressed slightly (0.034 versus
0.030 s); those two rows were timed as separate fresh `--case` processes,
not in the ordered all-case run. No automatic default switch or performance
claim for all inputs is made.

## Issue #64: opt-in Hecke / Temperley–Lieb Jones backend

For **sl2 fundamental only**, `backend="temperley_lieb"` evaluates an exact
scalar in a sparse planar-pairing basis. The source-derived local relation is
`E_i=q I-check-R_i`, with `E_i^2=(q+q^-1)E_i`; the positive and inverse Artin
generators are `q I-E_i` and `q^-1 I-E_i`. Diagrams multiply in input order.
Each closed planar loop contributes `delta=q+q^-1`, and the final reduced
scalar is `q^(-2 writhe) * planar_closure / delta`. The explicit matrix
derivation and weighted-trace/Markov checks are in `docs/MATH_CONVENTIONS.md`.
This is not a textbook-normalization assumption. The standard presentation
still uses `t=q_project^-2`.

The implementation never constructs a tensor-space braid operator. It reports
the planar closure and sparse basis-term count in metadata, but no ordinary
raw operator trace. `src.services` exposes the same opt-in backend selector
for sl2-fundamental evaluations; selecting it for sl3 or spin-1 fails
explicitly. The explicit matrix backend remains default/reference, and the
matrix-free EYB contraction remains an independent scalar backend.

Exact tests compare source-level Hecke/TL relations and weighted traces,
unknot/unlink, both trefoil presentations, figure-eight, positive/inverse and
mixed-sign words, symbolic q and q=2/3/5, representative fixtures, both sides
of archived P03 at q=2/3/5 and its symbolic difference, the complete offline Knot Atlas Jones set,
positive/negative stabilization, and four- through eight-strand controls.
Service tests also check exact output strings, unchanged formal status,
standard-Jones presentation parity, and explicit rejection of unsupported
branches. No test changes an oracle or reference output to fit the new path.

Measurements below were recorded on 2026-09-23, Windows 11, Python 3.12.4,
SymPy 1.12. Each backend/case cell was run with a separate fresh
`--case NAME --repeat 2` process; figures are first/warm wall seconds, not
CI thresholds. All three backends returned the **same exact primary-output
string** per row:

| sl2-fundamental case | q | explicit (s) | matrix-free (s) | TL (s) |
| --- | --- | ---: | ---: | ---: |
| trefoil `[1,1,1]` | symbolic | 0.193 / 0.054 | 0.146 / 0.017 | 0.139 / 0.019 |
| figure-eight `[1,-2,1,-2]` | symbolic | 0.249 / 0.090 | 0.167 / 0.024 | 0.147 / 0.021 |
| eight-strand cyclic `[1,…,7]` twice | symbolic | 2.218 / 2.067 | 0.241 / 0.109 | 0.417 / 0.254 |
| eight-strand cyclic `[1,…,7]` twice | 2 | 1.834 / 1.808 | 0.048 / 0.021 | 0.086 / 0.059 |
| eight-strand local `[1]` forty times | 2 | 1.578 / 1.506 | 0.068 / 0.040 | 0.028 / 0.002 |

TL is especially effective when a long word retains few planar basis terms,
as in the repeated single-generator row. The cyclic eight-strand word creates
many pairings, so matrix-free EYB is faster there. Planar basis growth is
potentially Catalan in strand count; no universal speedup or automatic
routing is claimed. A symbolic 40-crossing eight-strand explicit-reference
trial was stopped because it was not a practical comparison; the long-word
benchmark instead uses exact rational q=2 output.

## Issue #66: maintained desktop backend selection

The PySide6 invariant workflow now defaults to `matrix_free` **only in the
desktop request**. Public `src.services` calls that omit `backend` still use
`explicit`. The desktop request records the chosen id immutably and forwards
it for both catalog and manual braids. The offscreen worker test forbids
`BraidOperatorBuilder` while running a default-shaped three-branch request;
all three results identify `matrix_free`, demonstrating that no global braid
operator is built. TL remains selectable only for sl2 fundamental. Scalar-only
Detailed results accurately omit ordinary raw trace/full-operator diagnostics.

For a small, reproducible desktop-shaped q=2 trefoil measurement, run each
command in a fresh process (no GUI or CI timing threshold):

```text
python -m tools.profile_desktop_selection --backend explicit
python -m tools.profile_desktop_selection --backend matrix_free
python -m tools.profile_desktop_selection --backend temperley_lieb
```

Measured 2026-09-23 on Windows 11, Python 3.12.4, SymPy 1.12. Each first/warm
pair is two calls in one process. Explicit and matrix-free use the desktop's
three selected built-in branches; TL necessarily uses sl2 fundamental only.
All compatible primary-output strings matched exactly:

| Desktop-shaped selection | First / warm (s) | Ordinary raw trace available? |
| --- | ---: | --- |
| Reference / diagnostics, three branches | 0.092 / 0.013 | Yes |
| Fast scalar, three branches | 0.086 / 0.003 | No |
| TL, sl2 only | 0.017 / 0.0002 | No |

These tiny examples are illustrative, not evidence that one backend is always
fastest. The higher-strand comparisons above show that relative performance
depends on the braid. The desktop control therefore exposes all compatible
choices instead of silently auto-routing by an unverified speed rule.
