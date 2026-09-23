# Project State

Last updated: 2026-09-23

## Product

Calculator of Knots and Links is being converted from a research/code bundle into an installable desktop application.

The repository should eventually support both:

1. a reusable mathematical library for knot/link calculations
2. a normal desktop application that non-developers can install and run

## Current stage

**Stage 1 — package and test baseline (complete)**

The original ZIP remains at `archive/report_bundle.zip`. Issue #5 recovered the
authoritative historical tree from `C:\cpp\comp2012\Quantum Group Knot` without
redesigning or changing its mathematical conventions. The repository now contains:

- the braid, algebra, R-matrix, invariant, catalog, experiment, GUI, and workbench modules under `src/`;
- the historical examples, benchmark inputs, tests, and report-bundle tool;
- the previously recovered `benchmark_lab` snapshot and its archived outputs; and
- an exact recovery record in `docs/AUTHORITATIVE_RECOVERY.md`.

The formerly missing `BraidWord`, `src.braid`, `src.invariants`, sl2 fundamental,
sl2 spin-1/3D, and sl3 fundamental evaluators now import and run. The recovered
benchmark CLI reproduces the archived q=2, q=3, and q=5 JSON outputs exactly.
The archived P01 and P03 symbolic audit JSON outputs also reproduce exactly.

## Immediate objective

M3 desktop functionality, M4 Windows distribution, and M5 productization are complete. **v0.1.3 is the current published stable release.** It includes the merged M6 preview-continuity, Compact/Detailed presentation, exact variable relabeling, and measured performance work. Mathematical behavior is unchanged.

## Architecture direction

Future direction (not implemented by the recovery pass):

- mathematical engine: plain Python / SymPy-compatible modules
- application layer: thin service boundary
- desktop UI: PySide6
- tests: pytest
- packaging: PyInstaller
- CI: GitHub Actions

## Priority order

1. Mathematical correctness
2. Reproducibility and regression coverage
3. Maintainability
4. Desktop usability
5. Performance
6. UI polish

## Current risks

- The recovered GUI is Tkinter and retains its presentation-oriented rendering
  and workbench UI code. Input parsing/evaluation is now in `src.services`, and
  architecture tests prevent `src.workbench` or `src.services` from importing
  `src.gui`.
- The recovered import package is named `src`; it is retained for compatibility
  and will not be moved merely to satisfy packaging conventions.
- The source establishes that positive integers mean positive Artin generators;
  therefore P01's added `-2` is a negative stabilization and its archived
  “positive stabilization” label is inconsistent with the implementation.
- The sl2 3D branch is explicitly a candidate normalization and still requests
  comparison with an external reference.
- Stored P01 and P04 results disagree with their expected metadata; they are audit cases, not validated conclusions.
- The current Anaconda/Tcl installation cannot create a Tk root. GUI tests retain
  their assertions but skip environment-dependent root creation when Tk is
  unavailable.

## Current milestone

### M0 — Recover and normalize the repository

Exit criteria:

- project sources are present as normal repository files
- generated/cache files are excluded
- existing runnable examples are identified
- a source inventory is documented
- baseline commands for running the current program are known
- initial regression tests capture verified behaviour

Recovery status:

- Complete for the authoritative historical source supplied for issue #5.
- Generated artifacts, caches, IDE settings, compiled bytecode, and bundled report
  duplicates were intentionally excluded; see `docs/AUTHORITATIVE_RECOVERY.md`.
- The original ZIP remains archived as provenance even though its numeric outputs
  have now been reproduced.

### M1 — Package and test baseline

The project now has explicit package metadata, runtime/test dependency groups,
pytest configuration, and separate fast versus extended test workflows. The
historical `src` package remains in place. The representative q=2 outputs and
the established symbolic sl2 cases are centralized in
`tests/fixtures/representative_invariant_regressions.json`; see
`docs/REPRESENTATIVE_REGRESSIONS.md` for scope and provenance. M2 refactoring
and PySide6 migration are not part of this milestone.

### M2 — Core refactor (complete)

The initial dependency-direction repair is complete: `src.services` owns the
small provisional API for generator parsing, validated custom braid creation,
catalog/custom evaluation, selected branch execution, and reusable input-source
metadata. `src.workbench.runner` and the Tkinter GUI use this service without
altering recovered branch behavior or mathematical conventions. Further core
refactoring remains deliberately out of scope until separately planned.

The API now has an explicit facade, structured application errors, and one
frontend-neutral branch catalog. It records the formal sl2/sl3 branches and the
workbench `sl2_3d_9x9` to internal `sl2_spin1` candidate mapping. See
`docs/APPLICATION_API.md`. GUI styling remains local to `src.gui`; no
mathematical claims or conventions changed.

Application result DTOs now isolate maintained frontend rendering from internal
invariant result/formatter classes. The service facade provides deterministic
JSON serialization and text reports; the legacy launcher remains an explicitly
documented historical compatibility path. No mathematical objects or values are
changed by this reporting boundary.

Maintained pair comparison now uses the same service DTO evaluations as batch
workbench execution, keeping the branch/model association at the application
boundary. Maintained frontend catalog access also uses service catalog snapshots.
Architecture tests prevent service/workbench GUI dependencies, workbench branch
evaluator imports, and maintained frontend catalog implementation imports.

M2 exit criteria are satisfied: no R-matrix, braid, q, trace, framing,
eigenvalue, polynomial, formal/candidate, or representative-regression behavior
changed. The candidate sl2 spin-1 normalization remains deliberately unresolved
research but does not block an M3 frontend that displays its established status.
There is no known engineering dependency blocking M3.

### M3 — Desktop application (complete)

The maintained PySide6 `QMainWindow` is available through `python -m src.desktop`
after installing the `desktop` dependency group. It provides service-driven
catalog/custom-braid inputs, visible formal/candidate branch status, worker-
thread evaluation, result reporting/export, and standard Exit/About routes. The
recovered Tkinter code remains available as compatibility/reference code.

A frontend-neutral custom R/check-R braid-operator engine is now available
through `src.services`. It accepts explicit raw `R` or direct `check-R` input,
validates tensor-square dimension/invertibility and optional relation checks,
and returns deterministic operator DTOs. It intentionally provides no enhanced
trace or link-invariant recipe and does not alter any built-in branch.

An offline independent Knot Atlas oracle suite now calibrates Atlas braid signs
across four knots, freezes exact Jones checks through `6_1`, and records the
coherent A2 fundamental variable map. It also preserves the A1 weight-2 versus
spin-1 candidate mismatch as diagnostic evidence. Custom check-R parity and
negative controls, including an invertible matrix that fails the braid
relation, protect the convention boundary. See `docs/EXTERNAL_VALIDATION.md`.

The maintained PySide6 application now has a dedicated Custom R/check-R
operator tab. It accepts explicit convention-labelled matrix text or a small
text/JSON file, validates shape/dimension/invertibility and optional relations,
constructs a signed custom braid operator through `src.services`, and renders
the resulting matrix, diagnostics, warnings, and copy/export JSON. Expensive
service operations run in a Qt worker thread. This UI adds no invariant
normalization and states that boundary prominently.

Custom-matrix validation now distinguishes structural input validity from
verified braid-representation evidence. The optional check-R relation is shown
as verified, failed, not checked, or symbolically undecidable; a structurally
valid matrix is never presented as a braid representation solely because it
has no input errors. The known `diag(1,2,3,4)` negative control remains
constructible by the intentionally permissive operator engine but is visibly
reported as relation failure.

The primary PySide6 tab now supports the maintained built-in invariant
workflow. Users can select a service-catalog example or enter a project-native
signed Artin braid, select one or more service-owned branches, and provide an
exact or symbolic `q` value. Evaluation runs in a Qt worker thread and returns
service DTO reports with their formal/candidate status, normalization, variable
convention, representation, metadata, and warnings intact. Copy, JSON, and
file export use service report/serialization helpers; no live Atlas lookup or
mathematical convention change is introduced.


### M4 — Distribution (complete; v0.1.2 published)

Issue #34 introduces the first maintained Windows distribution path. A checked-in PyInstaller `onedir` specification packages the PySide6 desktop application and SymPy runtime without requiring the user to install Python. A Windows GitHub Actions workflow runs the fast regression suite, builds the executable, smoke-tests the packaged application, creates a deterministic Windows ZIP, extracts it, and smoke-tests the extracted executable before upload.

The first M4 step deliberately favors a reliable folder-style bundle over a fragile one-file executable. The maintained application version is sourced only from `src/version.py` as `0.1.3`; setuptools metadata, desktop `--version`, packaged `--version`, and Help/About use that source. The tag validator accepts only exact `vX.Y.Z` tags and requires equality with the maintained version. The shared Windows build script runs fast tests, the existing onedir build, packaged and extracted portable smoke/version checks, Inno Setup 6 compilation, and expected-file/checksum verification. The tagged workflow publishes the stable installer, portable ZIP, and `SHA256SUMS.txt` only for a real tag push using `GITHUB_TOKEN`. Manual dispatch with `v0.1.3` is explicitly non-publishing and uploads the same three candidate assets for validation; clean-machine install/uninstall remains documented rather than forcing fragile silent UI automation.

The `v0.1.2` tag and GitHub Release are published. The installer remains unsigned
and installs per-user under `%LOCALAPPDATA%\Programs` without PATH changes or
elevation. The release workflow validated the tag/version match, rebuilt and
smoke-tested the packaged and portable applications, compiled the Inno Setup
installer, verified the stable asset names and checksums, and published the
installer, portable ZIP, and `SHA256SUMS.txt`. See `docs/DISTRIBUTION.md`.

Issue #47 prepared this release with a single-source version, bilingual release
notes, exact tag/version guard, and final Windows candidate validation. The
non-publishing workflow-dispatch dry run also completed successfully before the
real tag-driven publication.


### M5 — Productization (complete)

The maintained PySide6 frontend now includes a deterministic Qt-native braid preview for both built-in/custom-braid invariant input and the custom R/check-R workflow. It consumes validated service-layer braid words, preserves project-native Artin signs and generator order, renders explicit over/under crossing semantics, reports writhe/final permutation metadata, and supports fit, zoom/pan, SVG export, and PNG export. Renderer-independent geometry tests cover positive/negative crossings, mixed-sign words, identity braids, long words, permutation, and deterministic SVG output.

Issue #43 adds a curated, provenance-labelled example browser and deterministic
versioned `.knotcalc.json` project documents. The public service facade validates
invariant/custom-R setup state, preserves symbolic q and matrix text, and routes
loads into the appropriate maintained workflow without evaluating anything.
The browser includes the recovered catalog, calibrated 5_1/5_2 evidence, braid
convention demonstrations, and custom check-R diagnostics including the
relation-failure negative control. No branch status or mathematical behavior is
changed.

Issue #45 completes the remaining M5 productization layer. A frontend-neutral
`src.services` explanation catalog now owns branch descriptions, formula lines,
normalization/variable statements, formal/candidate/operator-only status, and
documentation references; the PySide6 workflows render that data in a
contextual Mathematics dock. File → Export provides result text/JSON,
custom-operator JSON, and braid preview SVG/PNG actions with unavailable
formats disabled. The bilingual offline user guide is available from Help and
is included in the PyInstaller onedir bundle. README documents a maintainer
refresh script that captures the real maintained app, rather than fabricated
mockups. No invariant, R-matrix, braid, q, normalization, Knot Atlas fixture,
external-oracle, or application-version behavior changed.

The post-v0.1.1 desktop usability hotfix divides the maintained invariant tab
into braid setup/preview and calculation/results pages. Manual braid input is
explicit in the setup mode selector; the preview has a larger minimum area.
Resizable splitters and scrollable branch selection keep the workflow usable
at normal window size. Curated examples and Mathematics remain available from
View as tabified side docks, closed by default. Existing services, project
documents, exports, and mathematical behavior are unchanged; release preparation
bumps only the maintained application version to `0.1.2`.

### M6 — Performance baseline and low-risk fast path

Issue #55 adds a reproducible benchmark/profiling harness and before/after
measurements in `docs/PERFORMANCE.md`. Profiling identified repeated local
spin-1 projector/YBE/eigen diagnostics as the dominant symbolic trefoil cost.
Formal built-in runtime evaluation now constructs the same raw R and check-R
without eagerly repeating those research diagnostics; direct validated builders
remain the default. The spin-1 candidate retains its public projector-check
metadata and reuses one validated local construction. Bounded caches isolate
mutable local data by copy, and the one-strand identity normalization uses its
exact trace-of-mu scalar. Representative outputs, external oracle mappings,
formal/candidate status, and all mathematical conventions remain unchanged.
That issue did not implement matrix-free or Hecke/Temperley–Lieb backends;
the subsequent opt-in matrix-free work is recorded below under issue #60.


### M6 — Result presentation and preview continuity

Issue #54 adds one maintained post-release presentation pass without changing invariant mathematics. The braid-preview service now describes continuous physical strands plus crossing-local mask/overpass semantics shared by the Qt preview and SVG export, preventing false non-crossing strand breaks from segment-wide halos. The maintained invariant workflow also defaults to a Compact result view backed by service presentation descriptors. Symbolic sl2 results can show an exact standard Jones-variable `t` form and an Atlas-comparable `q_atlas` form when the conversion is an unambiguous Laurent relabeling; symbolic sl3 can show the maintained Atlas-comparable A2 variable form, while numeric `q` inputs remain scalar-only presentations and the spin-1 branch remains explicitly candidate-only.

Issue #59 published the merged M6 work as
[v0.1.3](https://github.com/Dongqiyu829/Calculator-of-Knots-and-Links/releases/tag/v0.1.3)
with a single-source version bump and bilingual release notes. The tagged
Windows workflow passed packaging and smoke checks and uploaded all three
stable assets. The existing onedir installer/portable/checksum machinery and
tag/version guard remain intact. No matrix-free or Temperley–Lieb backend is
part of this release.

### M6 — Matrix-free EYB scalar evaluation

Issue #60 adds an opt-in `matrix_free` built-in backend after the verified
v0.1.3 release. It contracts signed local `check-R` gates and diagonal
enhancement weights with exact SymPy arithmetic, without materializing the
global braid-operator matrix. The explicit backend remains the default and
diagnostic reference; Custom R/check-R operator evaluation is unchanged.
Matrix-free service results expose the same primary formal/candidate scalar
but explicitly omit ordinary raw trace and full-operator claims. Exact
parity, archived/current fixture coverage, and benchmark measurements are
recorded in `docs/PERFORMANCE.md`. No established convention changed.

### M8 — sl2-fundamental Temperley–Lieb scalar evaluation

Issue #64 adds a separate, opt-in `temperley_lieb` backend for the formal
sl2-fundamental Jones-compatible scalar. Its Hecke generator, planar loop
weight, closure trace, and writhe/unknot normalization are derived from the
maintained check-R and EYB data in `docs/MATH_CONVENTIONS.md`, not assumed
from an external Jones convention. Exact parity checks include representative
and archived fixtures, the complete offline Knot Atlas Jones set, positive
and negative Markov stabilization, and higher-strand words. This backend
does not create a global tensor-space operator or claim an ordinary raw trace.
The explicit backend remains the default/reference and matrix-free EYB remains
a distinct option; neither sl3 nor spin-1 accepts the TL backend. Benchmark
results and workload-dependent limitations are in `docs/PERFORMANCE.md`.
No branch status, mathematical convention, version, or release changed.

### M9 — Desktop access to verified scalar backends

Issue #66 connects the three already-validated built-in backends to the
maintained PySide6 invariant workflow. New desktop calculations choose
`matrix_free` by default, with explicit user choices for the global-matrix
reference/diagnostic path and the sl2-only Temperley–Lieb scalar path. The
public `src.services` evaluation default remains `explicit` for existing
callers. Backend selection is included in immutable worker requests for both
catalog and manual braids; evaluation remains off the UI thread. Scalar-only
results identify missing ordinary raw trace/full-operator diagnostics and
offer reference recomputation rather than inventing data. TL eligibility is
checked through the service facade and visibly reset when a new branch makes
it incompatible. Invariant project files use an optional validated backend
field within schema version 1; old files remain valid and load with the new
desktop default without evaluating. Mathematical outputs, branch statuses,
Custom R/check-R, and the published version remain unchanged.


### M9 — Custom R/check-R desktop layout parity

Issue #70 brings the maintained Custom R/check-R operator workflow in line with the invariant workflow's desktop structure. Matrix and braid setup now live on a scrollable setup/preview page with a large resizable braid diagram, while validation controls and operator diagnostics live on a separate results page with a vertical splitter. Existing widget/service semantics, project save/load behavior, operator-only mathematical boundary, and custom matrix serialization remain unchanged. The worker lifecycle also uses bound Qt signal/slot cleanup rather than Python lambda lifecycle callbacks.
