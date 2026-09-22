# Mathematical Implementation Guide

This document is the main mathematical guide to **Calculator of Knots and Links**. Its goal is to make the implementation understandable without requiring a reader—or another AI agent—to reverse-engineer the repository module by module.

It explains the path

$$
\text{braid word}
\longrightarrow
\text{local }R/\check R
\longrightarrow
\text{global braid operator}
\longrightarrow
\text{weighted trace / normalization}
\longrightarrow
\text{branch output},
$$

and it records where each mathematical step is implemented, what convention is used, what has been externally validated, and what remains candidate status.

This document should be read together with:

- `docs/MATH_CONVENTIONS.md` for the exact convention record;
- `docs/CUSTOM_RMATRIX_ENGINE.md` for the custom-matrix contract;
- `docs/EXTERNAL_VALIDATION.md` for independent Knot Atlas checks;
- `docs/REPRESENTATIVE_REGRESSIONS.md` for implementation compatibility baselines;
- `docs/APPLICATION_API.md` for the frontend-neutral service boundary.

The repository also contains older explanatory documents such as
`docs/mathematical_status_note.md` and `docs/simple_examples.md`. Those were important historical project notes, but this file is intended to be the current canonical end-to-end mathematical implementation guide.

---

## 1. What the program actually computes

The maintained mathematical engine currently has three built-in branches:

| Branch | Representation | Local dimension | Status | Primary output |
| --- | --- | ---: | --- | --- |
| `sl2_fundamental` | fundamental $U_q(\mathfrak{sl}_2)$ | $2$ | formal | reduced P2 / Jones-compatible output |
| `sl3_fundamental` | fundamental $U_q(\mathfrak{sl}_3)$ | $3$ | formal | P3-type EYB output |
| `sl2_spin1` | spin-1 / 3D $U_q(\mathfrak{sl}_2)$ | $3$ | candidate | reduced colored-Jones-style candidate |

Here **formal** is a project status. It means the branch convention, implementation, regression behavior, and current external comparison are fixed strongly enough to be treated as a maintained output of this codebase. It is not a claim that this repository proves a new theorem.

The program also contains a custom $R/\check R$ engine. That engine constructs and validates braid operators, but it deliberately does **not** turn an arbitrary matrix into a knot invariant automatically.

---

## 2. End-to-end pipeline

The mathematical flow of a built-in calculation is:

```text
BraidWord
   |
   v
RepresentationSpec
   |
   v
raw R matrix
   |
   |  check-R = P R
   v
local braid generator check-R on V tensor V
   |
   |  tensor embedding
   v
rho(beta) on V^(tensor n)
   |
   +------------------------------+
   |                              |
   v                              v
ordinary trace               weighted / EYB trace
diagnostic only              alpha^(-w) beta^(-n)
                             Tr(rho(beta) mu^(tensor n))
                                    |
                                    v
                         branch-specific normalization
                                    |
                                    v
                            application branch result
```

At the source level, the principal modules are:

| Mathematical role | Main implementation |
| --- | --- |
| braid input | `src/braid/braid_word.py` |
| representation metadata | `src/algebra/representations.py` |
| raw/local R data | `src/rmatrix/rmatrix_base.py` |
| $U_q(\mathfrak{sl}_2)$ local matrices | `src/rmatrix/sl2_rmatrix.py` |
| $U_q(\mathfrak{sl}_3)$ local matrix | `src/rmatrix/sl3_rmatrix.py` |
| spectral channel projectors | `src/rmatrix/projectors.py` |
| global braid operator | `src/braid/braid_operator.py` |
| raw closure trace | `src/invariants/quantum_trace.py` |
| enhanced Yang-Baxter normalization | `src/invariants/eyb_invariant.py` |
| formal Jones-compatible layer | `src/invariants/jones_invariant.py` |
| spin-1 candidate layer | `src/invariants/sl2_3d_colored_jones_candidate.py` |
| unified built-in branch dispatch | `src/invariants/branch_registry.py` |
| maintained frontend API | `src/services/` |
| PySide6 frontend | `src/desktop/` |

The important architectural rule is that the desktop frontend does not reproduce any of this mathematics. It calls `src.services`, which calls the mathematical core.

---

## 3. Braid words and the sign convention

A braid on $n$ strands is represented by an ordered word

$$
\beta
=
\sigma_{i_1}^{\varepsilon_1}
\sigma_{i_2}^{\varepsilon_2}
\cdots
\sigma_{i_m}^{\varepsilon_m},
\qquad
\varepsilon_k\in\{+1,-1\}.
$$

The code stores this as:

- `num_strands = n`;
- an ordered tuple of signed integers;
- positive $i$ means $\sigma_i$;
- negative $-i$ means $\sigma_i^{-1}$.

For example,

```text
[1, -2, 1, -2]
```

means

$$
\sigma_1\sigma_2^{-1}\sigma_1\sigma_2^{-1}.
$$

This is the project presentation of the figure-eight knot used by the catalog.

The implementation rejects:

- generator $0$;
- $|i|>n-1$;
- nontrivial generators on a one-strand braid.

The writhe is

$$
w(\beta)=\sum_{k=1}^m \varepsilon_k.
$$

It is used later in the EYB framing/Markov normalization factor.

### Multiplication order

The order stored in `BraidWord.generators` is the order used by the matrix builder.

If the word is

$$
(g_1,g_2,\ldots,g_m),
$$

the global operator is built as

$$
\rho(\beta)
=
\rho(g_1)\rho(g_2)\cdots\rho(g_m).
$$

In code, `BraidOperatorBuilder` starts with the identity matrix and repeatedly performs

```python
total_operator = total_operator * embedded
```

from left to right.

This convention matters. Reversing matrix multiplication would in general produce a different operator.

---

## 4. Representations and basis order

The representation layer is intentionally explicit because a matrix is meaningless unless its basis order is known.

### 4.1 $U_q(\mathfrak{sl}_2)$ fundamental

The local representation $V$ has dimension $2$, with basis ordered from highest to lowest weight:

$$
(v_1,v_2).
$$

The tensor-square basis is lexicographic:

$$
(v_1\otimes v_1,\,
v_1\otimes v_2,\,
v_2\otimes v_1,\,
v_2\otimes v_2).
$$

The decomposition is

$$
V\otimes V \cong V_{J=1}\oplus V_{J=0},
$$

with dimensions

$$
2\otimes2=3\oplus1.
$$

The maintained braid eigenvalues are

$$
\lambda_{J=1}=q,
\qquad
\lambda_{J=0}=-q^{-1}.
$$

### 4.2 $U_q(\mathfrak{sl}_2)$ spin-1

The representation has dimension $3$, with weight basis

$$
(w_1,w_0,w_{-1}).
$$

The tensor-square decomposition is

$$
3\otimes3=5\oplus3\oplus1,
$$

corresponding to

$$
J=2,\quad J=1,\quad J=0.
$$

The current local braid eigenvalues are

$$
\lambda_{J=2}=q^4,
\qquad
\lambda_{J=1}=-1,
\qquad
\lambda_{J=0}=q^{-2}.
$$

This local $9\times9$ structure is internally validated, but the final branch normalization is still candidate status.

### 4.3 $U_q(\mathfrak{sl}_3)$ fundamental

The representation has dimension $3$, with basis

$$
(e_1,e_2,e_3).
$$

The tensor square decomposes as

$$
3\otimes3=6\oplus\overline 3.
$$

The maintained braid eigenvalues are

$$
\lambda_{\mathrm{sym}}=q,
\qquad
\lambda_{\mathrm{antisym}}=-q^{-1}.
$$

The tensor basis is again lexicographic:

$$
e_1\otimes e_1,\,
e_1\otimes e_2,\ldots,
e_3\otimes e_3.
$$

---

## 5. Raw $R$ versus braid operator $\check R$

This distinction is one of the most important conventions in the repository.

The data object `RMatrixData` stores two different matrices:

- `matrix`: the raw literature-facing $R$;
- `braid_matrix`: the matrix actually used for an Artin generator.

They are related by

$$
\check R = P R,
$$

where $P$ is the tensor-factor swap,

$$
P(v_i\otimes v_j)=v_j\otimes v_i.
$$

The implementation of $P$ is `swap_operator(local_dim)`.

All braid-word code consumes $\check R$, not raw $R$.

This is why the custom-matrix UI never guesses whether the user pasted $R$ or $\check R$. The distinction changes the equation that should be checked and changes how the matrix acts in a braid word.

---

## 6. Yang-Baxter equations used by the program

For a direct braid operator $\check R$, the relevant relation is the braid-form Yang-Baxter relation

$$
\check R_{12}\check R_{23}\check R_{12}
=
\check R_{23}\check R_{12}\check R_{23}.
$$

This is exactly the Artin braid relation for adjacent generators on three tensor factors.

For a raw $R$, the program can separately check the standard form

$$
R_{12}R_{13}R_{23}
=
R_{23}R_{13}R_{12}.
$$

These are intentionally represented as different validation statuses.

For built-in `RMatrixData`, the helper `check_yang_baxter` implements both checks.

For custom matrices, `ApplicationCustomMatrixValidation` distinguishes:

- structural validity;
- invertibility;
- check-$R$ braid-relation status;
- raw-$R$ standard-YBE status.

A matrix can be square, dimension-compatible, and invertible while still failing the braid relation. The test suite explicitly uses

$$
\operatorname{diag}(1,2,3,4)
$$

as such a negative control.

---

## 7. How the $U_q(\mathfrak{sl}_2)$ matrices are built

The sl2 implementation is not a hard-coded table for each representation. Both the 2D fundamental and the 3D spin-1 model are produced by the same highest-weight construction in `src/rmatrix/sl2_rmatrix.py`.

Let the highest weight be $m$, so $\dim V=m+1$. The ordered weights are

$$
m,\;m-2,\;m-4,\ldots,-m.
$$

The implementation constructs $E$ and $F$ using q-integers

$$
[n]_q=\frac{q^n-q^{-n}}{q-q^{-1}},
$$

and

$$
[n]_q! = \prod_{k=1}^{n}[k]_q.
$$

In the code normalization, define the diagonal factor $D$ on a weight basis vector $v_a\otimes v_b$ by

$$
D(v_a\otimes v_b)
=
q^{h_a h_b/2}(v_a\otimes v_b),
$$

where $h_a,h_b$ are the corresponding weights.

The nilpotent part implemented is

$$
N
=
\sum_{r=0}^{m}
q^{r(r-1)/2}
\frac{(q-q^{-1})^r}{[r]_q!}
E^r\otimes F^r.
$$

The raw matrix used by this project is

$$
R_{\mathrm{raw}}
=
q^{m^2/2} D N.
$$

This scalar normalization is important: it is the one chosen in the recovered code so that $m=1$ reproduces the existing fundamental $4\times4$ matrix exactly.

Then the local braid operator is

$$
\check R = P R_{\mathrm{raw}}.
$$

For:

- $m=1$, the result is the sl2 fundamental $4\times4$ local model;
- $m=2$, the result is the spin-1 $9\times9$ local model.

The repository therefore does not maintain two unrelated sl2 normalizations at the local-matrix construction stage.

---

## 8. How the $U_q(\mathfrak{sl}_3)$ fundamental matrix is built

The sl3 fundamental builder uses the standard Hecke-type matrix formula in terms of matrix units $E_{ij}$.

The exact raw matrix implemented is

$$
R
=
q\sum_i E_{ii}\otimes E_{ii}
+
\sum_{i\ne j}E_{ii}\otimes E_{jj}
+
(q-q^{-1})\sum_{i<j}E_{ij}\otimes E_{ji}.
$$

Then

$$
\check R = PR.
$$

The resulting $9\times9$ braid operator has the two channel eigenvalues

$$
q
\quad\text{on }6,
\qquad
-q^{-1}
\quad\text{on }\overline3.
$$

The project also constructs explicit spectral projectors for these channels.

---

## 9. Spectral projectors and channel reconstruction

When a braid matrix $B$ has distinct channel eigenvalues, the repository constructs the projector onto the $\lambda$-eigenspace by Lagrange interpolation:

$$
P_\lambda
=
\prod_{\mu\ne\lambda}
\frac{B-\mu I}{\lambda-\mu}.
$$

This is implemented by `spectral_projector` in `src/rmatrix/projectors.py`.

For a family of projectors, the code validates:

### Idempotency

$$
P_\lambda^2=P_\lambda.
$$

### Sum to identity

$$
\sum_\lambda P_\lambda=I.
$$

### Pairwise orthogonality

$$
P_\lambda P_\mu=0
\qquad(\lambda\ne\mu).
$$

### Reconstruction

$$
B=\sum_\lambda \lambda P_\lambda.
$$

For sl3, this realizes the $6\oplus\overline3$ channel split.

For sl2 spin-1, it realizes the $5\oplus3\oplus1$ channel split.

This distinction is mathematically important: both local operators are $9\times9$, but their representation-theoretic channel structures are different.

---

## 10. From a local $\check R$ to an $n$-strand braid operator

Suppose $V$ has dimension $d$, and $\check R\in\operatorname{End}(V\otimes V)$.

For an $n$-strand braid, the positive Artin generator is represented by

$$
\rho(\sigma_i)
=
I^{\otimes(i-1)}
\otimes \check R
\otimes
I^{\otimes(n-i-1)}.
$$

For a negative generator,

$$
\rho(\sigma_i^{-1})
=
I^{\otimes(i-1)}
\otimes \check R^{-1}
\otimes
I^{\otimes(n-i-1)}.
$$

The full space has dimension

$$
d^n.
$$

Therefore $\rho(\beta)$ is a

$$
d^n\times d^n
$$

matrix.

This exponential growth is why the desktop application warns about large custom tensor products and sends expensive symbolic work to a background worker.

The implementation is `BraidOperatorBuilder` in `src/braid/braid_operator.py`.

For every generator it stores diagnostics including:

- step index;
- signed generator;
- affected strand pair;
- whether the inverse was used;
- local matrix shape;
- embedded matrix shape.

---

## 11. Why ordinary trace is not yet a knot invariant

Given a global braid operator $\rho(\beta)$, the most immediate scalar is

$$
\operatorname{Tr}(\rho(\beta)).
$$

The code computes this in `compute_raw_closure_trace`.

This quantity is useful diagnostically, but the repository intentionally does not call it Jones, HOMFLY-PT, or a fully normalized link invariant.

The reason is that passing from braid-group data to an invariant of the closed braid requires the correct behavior under Markov moves, especially stabilization.

An ordinary matrix trace alone does not provide the needed normalization in general.

So the program keeps

$$
\text{raw closure trace}
$$

as a separate output layer.

---

## 12. Enhanced Yang-Baxter normalization

The maintained formal braid-side normalization is implemented in `src/invariants/eyb_invariant.py`.

For a braid $\beta$ on $n$ strands, with writhe $w(\beta)$, the code computes

$$
F(\beta)
=
\alpha^{-w(\beta)}
\beta_0^{-n}
\operatorname{Tr}
\left(
\rho(\beta)\mu^{\otimes n}
\right).
$$

To avoid confusing the scalar $\beta_0$ with the braid word $\beta$, this guide writes the EYB scalar as $\beta_0$. In the Python API its field name is simply `beta`.

The pieces have distinct roles:

- $\rho(\beta)$: global braid operator;
- $\mu^{\otimes n}$: quantum/enhanced trace weight;
- $\alpha^{-w}$: writhe/framing correction;
- $\beta_0^{-n}$: strand-count normalization.

The code separately records

$$
\operatorname{Tr}(\rho(\beta))
$$

and

$$
\operatorname{Tr}
\left(
\rho(\beta)\mu^{\otimes n}
\right)
$$

before normalization.

### sl2 fundamental EYB data

The current project uses

$$
\mu=
\begin{pmatrix}
q^{-1}&0\\
0&q
\end{pmatrix},
\qquad
\alpha=q^2,
\qquad
\beta_0=1.
$$

### sl3 fundamental EYB data

The current project uses

$$
\mu=
\operatorname{diag}(q^{-2},1,q^2),
\qquad
\alpha=q^3,
\qquad
\beta_0=1.
$$

### sl2 spin-1 candidate data

The current candidate layer uses

$$
\mu=
\operatorname{diag}(q^{-2},1,q^2),
\qquad
\alpha=q^4,
\qquad
\beta_0=1.
$$

The local spin-1 matrix and projector structure are validated, but this final normalization remains candidate status.

---

## 13. The formal sl2 Jones-compatible branch

The formal sl2 branch is not defined as “whatever comes out of the raw trace.”

The pipeline is:

$$
\text{sl2 fundamental }\check R
\longrightarrow
\rho(\beta)
\longrightarrow
F_{\mathrm{EYB}}(\beta)
\longrightarrow
\frac{F_{\mathrm{EYB}}(\beta)}
{F_{\mathrm{EYB}}(\text{1-strand unknot})}.
$$

The code calls:

- the EYB value: **unreduced P2**;
- the one-strand value: **unknot normalization**;
- the quotient: **reduced P2**;
- the reduced P2: **Jones-compatible output**.

Thus

$$
J_{\mathrm{project}}(\beta;q)
=
\frac{
F_{\mathrm{EYB}}(\beta;q)
}{
F_{\mathrm{EYB}}(\bigcirc;q)
}.
$$

The maintained project variable statement is

$$
t=q^{-2}.
$$

Independent Knot Atlas calibration is recorded using a different Atlas variable name and gives

$$
q_{\mathrm{Atlas}}=q_{\mathrm{project}}^2.
$$

These are not contradictory: they refer to different naming conventions used by different comparison layers.

The implementation is in `src/invariants/jones_invariant.py`.

---

## 14. Worked example: the trefoil

The catalog trefoil is represented by

$$
\beta=\sigma_1^3
$$

on two strands, stored as

```text
[1, 1, 1]
```

with writhe

$$
w=3.
$$

For the sl2 fundamental branch,

$$
\rho(\beta)=\check R^3.
$$

The EYB layer computes

$$
q^{-6}
\operatorname{Tr}
\left(
\check R^3(\mu\otimes\mu)
\right),
$$

because $\alpha=q^2$, $w=3$, and $\beta_0=1$.

After reduction by the one-strand unknot value, the frozen symbolic output is

$$
J_{\mathrm{project}}(3_1;q)
=
\frac{q^6+q^2-1}{q^8}.
$$

At $q=2$, the representative regression value is

$$
\frac{67}{256}.
$$

The external Knot Atlas fixture stores

$$
J_{\mathrm{Atlas}}(3_1;Q)
=
-Q^{-4}+Q^{-3}+Q^{-1}.
$$

With

$$
Q=q^2,
$$

this becomes exactly

$$
-q^{-8}+q^{-6}+q^{-2}
=
\frac{q^6+q^2-1}{q^8}.
$$

This is a useful end-to-end example because it simultaneously checks:

1. braid-sign convention;
2. local $\check R$;
3. braid multiplication;
4. EYB normalization;
5. unknot reduction;
6. external variable substitution.

---

## 15. Worked example: the figure-eight knot

The project catalog uses the 3-strand braid

$$
\beta
=
\sigma_1
\sigma_2^{-1}
\sigma_1
\sigma_2^{-1},
$$

stored as

```text
[1, -2, 1, -2]
```.

For a local $d$-dimensional representation, the two embedded positive generators are

$$
\rho(\sigma_1)=\check R\otimes I_d,
$$

and

$$
\rho(\sigma_2)=I_d\otimes\check R.
$$

Hence the project constructs

$$
\rho(\beta)
=
(\check R\otimes I)
(I\otimes\check R^{-1})
(\check R\otimes I)
(I\otimes\check R^{-1}).
$$

For the formal sl2 branch, the frozen symbolic result is

$$
J_{\mathrm{project}}(4_1;q)
=
\frac{q^{10}+1}
{q^4(q^2+1)}.
$$

At $q=2$,

$$
J_{\mathrm{project}}(4_1;2)
=
\frac{205}{16}.
$$

The Knot Atlas fixture stores

$$
J_{\mathrm{Atlas}}(4_1;Q)
=
Q^2+Q^{-2}-Q-Q^{-1}+1,
$$

and the same global substitution

$$
Q=q^2
$$

matches the project result.

---

## 16. The formal sl3 fundamental branch

The sl3 branch uses:

1. the Hecke-type raw $R$;
2. $\check R=PR$;
3. the global braid operator;
4. the sl3 EYB data
$$
   \mu=\operatorname{diag}(q^{-2},1,q^2),
   \quad
   \alpha=q^3,
   \quad
   \beta_0=1.
$$

Its primary branch output is the resulting **P3-type EYB output**.

Unlike the sl2 Jones-compatible branch, the current sl3 primary output is not divided by a one-strand unknot value in `branch_registry.py`.

That is why the one-strand catalog value is not normalized to $1$. For example, at $q=2$, the representative sl3 value for `unknot_1` is

$$
\frac{21}{4}.
$$

This behavior is intentional and part of the frozen branch convention.

Independent Knot Atlas A2 calibration finds a coherent variable correspondence

$$
q_{\mathrm{Atlas}}
=
q_{\mathrm{project}}^{-1}
$$

for the tested $3_1,4_1,5_1,5_2$ cases.

The branch is therefore formal and externally checked within this stated normalization, but it should not be silently renamed to a differently normalized literature polynomial.

---

## 17. The sl2 spin-1 candidate branch

The spin-1 branch starts from mathematically coherent local data:

$$
3\otimes3=5\oplus3\oplus1
$$

and braid eigenvalues

$$
q^4,\quad -1,\quad q^{-2}.
$$

Its projectors pass the structural checks described earlier.

The candidate invariant layer then computes:

1. raw closure trace;
2. weighted trace using
$$
   \mu=\operatorname{diag}(q^{-2},1,q^2);
$$
3. candidate EYB-style normalization with
$$
   \alpha=q^4,\qquad\beta_0=1;
$$
4. reduction by the one-strand unknot candidate value.

So the candidate reduced output is

$$
C(\beta;q)
=
\frac{
q^{-4w(\beta)}
\operatorname{Tr}
\left(
\rho(\beta)\mu^{\otimes n}
\right)
}{
C_{\mathrm{unreduced}}(\bigcirc;q)
}.
$$

The repository deliberately labels this output

```text
Colored Jones candidate output
```

rather than simply “colored Jones polynomial.”

### Why it remains candidate

The independent Knot Atlas suite compares the branch with A1 weight-2 data, which is the natural three-dimensional sl2 target.

The current external validation found no single coherent rule among the tested substitutions

$$
Q\in
\{q,\;q^{-1},\;q^2,\;q^{-2}\}
$$

plus a pure monomial shift that simultaneously resolves the calibration cases.

Therefore:

- the local representation-theoretic structure is retained;
- the candidate calculations remain useful;
- the implementation is not modified merely to make an external table match;
- the status remains **candidate**.

This is an important design principle of the project: an external mismatch is evidence to study, not a reason to silently rewrite normalization.

---

## 18. Same matrix size does not mean same invariant information

Both

- sl3 fundamental, and
- sl2 spin-1

have a 3-dimensional local representation, so both produce $9\times9$ local braid matrices.

But the decomposition data differ:

$$
3\otimes3=6\oplus\overline3
$$

for sl3 fundamental, versus

$$
3\otimes3=5\oplus3\oplus1
$$

for sl2 spin-1.

Thus they have different spectral channels and different trace/normalization data.

The repository's benchmark infrastructure treats “which branch separates which knot pair?” as an empirical computational question. It does not assume that a representation with more channels must always be a stronger invariant.

---

## 19. Custom $R/\check R$ engine

The custom-matrix layer is designed to reuse the same braid-operator mathematics without forcing user matrices into one of the built-in quantum-group branches.

A user can provide either:

### Raw $R$

The program computes

$$
\check R=PR.
$$

### Direct $\check R$

The matrix is used directly as the local Artin generator.

The engine then validates:

- square shape;
- whether the matrix dimension is $d^2$ for an integer local dimension $d$;
- consistency with an explicitly supplied $d$;
- invertibility;
- optional braid relation;
- optional raw-R YBE.

For a validated matrix, it constructs arbitrary braid words by the same embedding rule used by the built-in engine.

### What this proves—and what it does not

If $\check R$ satisfies the braid relation, then the local data support the braid-group representation step:

$$
B_n\longrightarrow
\operatorname{GL}(V^{\otimes n})
$$

when the required inverses exist.

That alone does **not** supply a link invariant.

A link invariant still needs suitable closure data, for example an enhanced Yang-Baxter package

$$
(\check R,\mu,\alpha,\beta_0)
$$

or equivalent ribbon/quantum-trace structure satisfying the needed Markov compatibility.

This is why the current custom engine stops at the braid-operator layer.

A future custom invariant system should treat the trace/enhancement data as a separate explicit recipe rather than guessing them from matrix entries.

---

## 20. Knot Atlas external calibration

The project deliberately separates two kinds of tests:

### Compatibility regression

“Does the current program still reproduce the authoritative recovered implementation?”

Source:

`tests/fixtures/representative_invariant_regressions.json`.

### Independent external oracle

“Does the maintained formal branch agree with an external mathematical reference under one coherent convention map?”

Source:

`tests/fixtures/knot_atlas_oracles.json`.

The Knot Atlas calibration currently establishes:

### Braid sign conversion

For Atlas `BR` data,

$$
g_{\mathrm{project}}=-g_{\mathrm{Atlas}}.
$$

This was calibrated across $3_1,4_1,5_1,5_2$, not inferred from a single trefoil.

For example, Atlas stores the trefoil braid as

$$
(-1,-1,-1),
$$

while the project uses

$$
(1,1,1).
$$

### Jones variable map

$$
q_{\mathrm{Atlas}}
=
q_{\mathrm{project}}^2.
$$

This is a hard regression across the external fixture set, including $6_1$.

### A2/sl3 variable map

$$
q_{\mathrm{Atlas}}
=
q_{\mathrm{project}}^{-1}.
$$

This is a hard external regression for the calibrated sl3/A2 fundamental cases.

### Spin-1

A1 weight-2 comparison remains diagnostic only, preserving candidate status.

No live web request is required to run these tests; the external reference data and provenance are stored offline.

---

## 21. Built-in/custom operator parity

The custom $\check R$ path is tested against the built-in sl2 fundamental path.

Conceptually, the test does:

1. construct the built-in sl2 fundamental $\check R$;
2. give exactly that matrix to the custom engine;
3. build the same braid in both engines;
4. compare the full global operator matrices.

This has been checked on calibrated braids including $3_1,4_1,5_2$, with a symbolic small case as well as numeric checks.

This test is stronger than merely comparing final scalar invariants. It checks that the custom engine reproduces the built-in tensor embedding, inversion, and multiplication conventions before any trace normalization is applied.

---

## 22. q handling

The maintained application boundary parses q through `src.services.parse_q_text`.

Examples:

```text
2
3/2
q
```

are interpreted as exact SymPy objects.

The program does not coerce $3/2$ to a floating-point approximation.

The literal symbolic `q` is created with a nonzero assumption because inverses such as $q^{-1}$ are fundamental to the matrix formulas.

The mathematical core itself is not restricted to positive real q or generic q. However, special values such as roots of unity can introduce degeneracies, vanishing denominators, projector collisions, or representation-theoretic behavior outside the assumptions behind some generic symbolic formulas. Such cases should therefore be treated explicitly rather than assumed to behave like generic q.

---

## 23. Minimal polynomials and eigenvalue reporting

For a local braid matrix $B$, the current helper constructs the polynomial

$$
m_{\mathrm{candidate}}(x)
=
\prod_{\lambda\in\operatorname{Spec}_{\mathrm{distinct}}(B)}
(x-\lambda).
$$

For the semisimple built-in channel models this is the expected spectral minimal-polynomial form.

The implementation is intentionally transparent: it derives this expression from distinct symbolic eigenvalues and does not currently perform general Jordan-block analysis.

Therefore, for future non-semisimple custom models, this helper should not be overinterpreted as a full general-purpose minimal-polynomial algorithm.

---

## 24. Formal, candidate, diagnostic, and validation language

The project uses status words carefully.

### Formal

A maintained branch whose current convention is fixed and regression-tested as a supported mathematical output.

Current examples:

- sl2 fundamental Jones-compatible;
- sl3 fundamental P3-type EYB.

### Candidate

A mathematically structured branch that is intentionally not promoted to the strongest literature identification.

Current example:

- sl2 spin-1 colored-Jones-style output.

### Diagnostic

An output useful for investigating structure but not itself promoted to a topological invariant.

Examples:

- ordinary closure trace;
- raw-vs-braid convention audits;
- some external candidate comparisons.

### Verified braid relation

A statement about the local operator satisfying the braid relation.

This is not the same as “verified knot invariant.”

---

## 25. Implementation map for humans and AI agents

When changing the project, the safest reading order is:

### To understand a braid

Read:

- `src/braid/braid_word.py`
- `docs/MATH_CONVENTIONS.md`

### To understand a built-in representation

Read:

- `src/algebra/representations.py`

### To understand raw $R$ and $\check R$

Read:

- `src/rmatrix/rmatrix_base.py`
- `src/rmatrix/sl2_rmatrix.py`
- `src/rmatrix/sl3_rmatrix.py`

### To understand channel projectors

Read:

- `src/rmatrix/projectors.py`

### To understand the global braid matrix

Read:

- `src/braid/braid_operator.py`

### To understand the raw trace

Read:

- `src/invariants/quantum_trace.py`

### To understand the EYB formula

Read:

- `src/invariants/eyb_invariant.py`

### To understand Jones normalization

Read:

- `src/invariants/jones_invariant.py`

### To understand the spin-1 candidate branch

Read:

- `src/invariants/sl2_3d_colored_jones_candidate.py`

### To see which output is officially exposed by each branch

Read:

- `src/invariants/branch_registry.py`
- `src/services/branch_catalog.py`

### To understand what the desktop application is allowed to call

Read:

- `docs/APPLICATION_API.md`
- `src/services/__init__.py`

### To verify mathematical compatibility

Read:

- `docs/REPRESENTATIVE_REGRESSIONS.md`
- `tests/fixtures/representative_invariant_regressions.json`

### To verify against an independent source

Read:

- `docs/EXTERNAL_VALIDATION.md`
- `tests/fixtures/knot_atlas_oracles.json`
- `tests/test_knot_atlas_external_oracles.py`

---

## 26. End-to-end pseudocode

The built-in calculation can be summarized without GUI details as:

```text
input:
    braid word beta
    selected branch
    exact/symbolic q

branch:
    choose representation V
    build raw R
    set check-R = P R

global braid operator:
    B = identity on V^(tensor n)
    for signed generator g in beta:
        if g > 0:
            local = check-R
        else:
            local = inverse(check-R)

        embedded = I tensor ... tensor local tensor ... tensor I
        B = B * embedded

raw diagnostic:
    raw = Tr(B)

normalized branch:
    weighted = Tr(B * mu^(tensor n))
    eyb = alpha^(-writhe(beta)) * beta0^(-n) * weighted

    if branch == sl2_fundamental:
        output = eyb / eyb(one-strand unknot)

    if branch == sl3_fundamental:
        output = eyb

    if branch == sl2_spin1:
        output = eyb / candidate_eyb(one-strand unknot)
        mark status = candidate

return:
    branch id
    representation
    status
    output
    normalization label
    variable convention
    metadata
```

This is the essential mathematical skeleton of the current program.

---

## 27. What the program does not yet implement

The current repository does **not** yet provide all of the following:

- arbitrary planar knot-diagram input;
- automatic conversion of arbitrary diagrams to braid words;
- a general Reshetikhin-Turaev category framework;
- a universal custom invariant recipe inferred from an arbitrary $R$-matrix;
- a theorem-level settled spin-1 colored Jones normalization;
- a general non-semisimple projector/minimal-polynomial framework;
- root-of-unity representation-theory handling as a separate specialized mode.

These are possible future directions, but they should be added as explicit mathematical contracts rather than hidden changes to existing branches.

---

## 28. Natural future extension: custom enhanced invariant recipes

The current architecture leaves a clean extension point.

A future custom invariant layer can require the user to supply, in addition to $R$ or $\check R$,

$$
\mu,\qquad
\alpha,\qquad
\beta_0,
$$

together with the exact convention being claimed.

The engine could then validate:

1. the braid/Yang-Baxter relation;
2. invertibility where needed;
3. enhancement compatibility conditions;
4. Markov stabilization behavior on test braids;
5. unknot normalization;
6. framing convention.

Only after these checks should a custom recipe be presented as a knot/link invariant rather than merely a braid operator.

That separation is already reflected in the code architecture:

```text
custom local operator
        |
        v
braid representation
        |
        v
future enhancement / trace recipe
        |
        v
future custom invariant
```

No GUI rewrite should be necessary to add this layer if it is introduced through `src.services`.

---

## 29. Testing philosophy

The project intentionally uses several independent kinds of evidence.

### Structural algebra tests

Examples:

- YBE / braid relation;
- projector idempotency;
- projector orthogonality;
- spectral reconstruction.

### Internal regression tests

These freeze behavior recovered from the authoritative historical implementation.

### Presentation/equivalence tests

Examples include the two-strand and three-strand trefoil presentations for formal branches.

### External oracle tests

Knot Atlas checks detect convention or normalization errors that an internally self-consistent test suite could miss.

### Negative controls

The suite also contains inputs that must fail, so a validator cannot pass merely because it never rejects anything.

This layered strategy is important for research software: “all tests pass” is meaningful only if not all tests inherit the same assumption.

---

## 30. Recommended reading order

For a mathematician new to the repository:

1. this document;
2. `docs/MATH_CONVENTIONS.md`;
3. `docs/EXTERNAL_VALIDATION.md`;
4. `src/algebra/representations.py`;
5. `src/rmatrix/rmatrix_base.py`;
6. one concrete builder such as `src/rmatrix/sl2_rmatrix.py`;
7. `src/braid/braid_operator.py`;
8. `src/invariants/eyb_invariant.py`;
9. `src/invariants/jones_invariant.py`;
10. the representative and external tests.

For an AI coding agent, additionally read:

1. `AGENTS.md`;
2. `docs/AUTOPILOT.md`;
3. `docs/APPLICATION_API.md`;
4. `docs/TASKS.md`.

Do not infer a new convention when the implementation and documentation disagree. Treat such a disagreement as a blocker requiring explicit investigation.

---

## 31. One-page conceptual summary

The central idea of the program is simple:

A quantum-group representation supplies a local operator on $V\otimes V$. After converting raw $R$ to the braid operator $\check R=PR$, the program embeds $\check R$ into adjacent tensor factors to obtain a representation of a braid word on $V^{\otimes n}$.

The resulting matrix is not yet automatically a knot invariant. The closure step requires the correct weighted trace and normalization. The maintained fundamental branches use enhanced Yang-Baxter data

$$
(\mu,\alpha,\beta_0)
$$

and compute

$$
\alpha^{-w}
\beta_0^{-n}
\operatorname{Tr}
\left(
\rho(\beta)\mu^{\otimes n}
\right).
$$

For sl2 fundamental, the result is additionally divided by the one-strand unknot value and exposed as the formal Jones-compatible output. For sl3 fundamental, the current formal branch exposes the P3-type EYB value in its present normalization. For sl2 spin-1, an analogous reduced output exists, but external comparison has not yet justified promoting that normalization beyond candidate status.

The custom $R/\check R$ engine reuses the same braid-representation machinery while deliberately stopping before the invariant layer unless enhancement data are supplied in a future extension.

That separation—local algebra, braid representation, closure normalization, branch claim—is the organizing mathematical principle of the repository.
