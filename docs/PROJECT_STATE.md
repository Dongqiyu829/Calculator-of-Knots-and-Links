# Project State

Last updated: 2026-09-22

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

Maintain the installable Python baseline and practical test tiers while retaining
the recovered `src` package and its mathematical behavior. M2 is complete: its
`src.services` API supplies input parsing/evaluation, branch and built-in-example
discovery, structured errors, result DTOs, and application reports. Maintained
workbench and Tkinter compatibility adapters share that path. M3 has begun with
a maintained PySide6 shell that reads lightweight catalog and branch metadata
only through `src.services`; it performs no invariant evaluation on startup.

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

### M3 — Desktop application (in progress)

The first PySide6 `QMainWindow` shell is available through `python -m src.desktop`
after installing the `desktop` dependency group. It provides a service-driven
example source panel, visible formal/candidate branch status, workspace/status
areas, and standard Exit/About routes. It deliberately does not yet edit braids,
evaluate invariants, create workers, export files, or replace Tkinter.

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
normalization and states that boundary prominently; built-in invariant
evaluation remains a separate M3 task.

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
