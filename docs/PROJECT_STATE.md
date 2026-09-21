# Project State

Last updated: 2026-09-21

## Product

Calculator of Knots and Links is being converted from a research/code bundle into an installable desktop application.

The repository should eventually support both:

1. a reusable mathematical library for knot/link calculations
2. a normal desktop application that non-developers can install and run

## Current stage

**Stage 0 — repository recovery and normalization**

At present, the repository mainly exposes:

- `README.md`
- `CITATION.cff`
- `report_bundle.zip`

The actual implementation is still bundled rather than maintained as a normal source tree.

## Immediate objective

Recover the contents of `report_bundle.zip`, inventory the existing implementation, preserve known mathematical behaviour with regression tests, and convert the codebase into a standard Python project without unnecessary rewrites.

## Architecture direction

Tentative direction, subject to revision after source recovery:

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

- The implementation is hidden inside a ZIP bundle, so the existing architecture has not yet been fully audited.
- Mathematical conventions may be encoded implicitly in scripts or demos.
- Refactoring before baseline tests exist could silently change knot/link invariants.

## Current milestone

### M0 — Recover and normalize the repository

Exit criteria:

- project sources are present as normal repository files
- generated/cache files are excluded
- existing runnable examples are identified
- a source inventory is documented
- baseline commands for running the current program are known
- initial regression tests capture verified behaviour
