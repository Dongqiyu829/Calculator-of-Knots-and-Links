# Project State

Last updated: 2026-09-21

## Product

Calculator of Knots and Links is being converted from a research/code bundle into an installable desktop application.

The repository should eventually support both:

1. a reusable mathematical library for knot/link calculations
2. a normal desktop application that non-developers can install and run

## Current stage

**Stage 1 — package and test baseline (established)**

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
the recovered `src` package and its mathematical behavior. The remaining M1
work is to broaden explicit regression cases and recorded reference outputs.
Core/service/UI separation and any PySide6 work remain later milestones.

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

- The recovered GUI is Tkinter and mixes evaluator helpers with UI code; the
  workbench service layer imports the GUI launcher.
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
historical `src` package remains in place. M2 refactoring and PySide6 migration
are not part of this milestone.
