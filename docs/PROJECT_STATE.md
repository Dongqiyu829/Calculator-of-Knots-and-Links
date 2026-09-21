# Project State

Last updated: 2026-09-21

## Product

Calculator of Knots and Links is being converted from a research/code bundle into an installable desktop application.

The repository should eventually support both:

1. a reusable mathematical library for knot/link calculations
2. a normal desktop application that non-developers can install and run

## Current stage

**Stage 0 — repository recovery and normalization (partial recovery complete)**

The original ZIP has been inspected and retained at `archive/report_bundle.zip`. Its recoverable implementation is now exposed as normal files:

- `src/benchmark_lab/` — seven Python modules for registry loading, branch adaptation, profile runs, summaries, audits, and output helpers
- `examples/benchmark_lab/` — two intended CLI entry points
- `data/benchmark_lab/` — CSV and JSON benchmark registries
- `tests/` — snapshot-integrity and stored-output regression coverage
- `docs/SOURCE_INVENTORY.md` and `docs/MATH_CONVENTIONS.md` — recovery evidence and convention audit

The snapshot is not the complete application described by its own README. It omits `src.braid`, `src.invariants`, the GUI/workbench, its original tests, and its bundle-creation tool. As a result, the benchmark CLIs remain blocked at import time and stored mathematical outputs cannot yet be recomputed.

## Immediate objective

Obtain the missing braid and invariant evaluator source (or another authoritative snapshot), reproduce the archived benchmark outputs, and only then continue normalization into an installable Python project. The recovered benchmark files must remain byte-for-byte stable until that baseline is reproducible.

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

- Core mathematical implementations referenced by the recovered benchmark layer are absent.
- The ZIP's “positive stabilization” description conflicts with the sign/writhe visible in its P01 data, so braid sign/orientation remains unresolved.
- R-matrix, tensor ordering, Markov/framing, eigenvalue, and polynomial normalizations cannot be established from the recovered files.
- Stored P01 and P04 results disagree with their expected metadata; they are audit cases, not validated conclusions.
- Refactoring or recreating the missing evaluators before authoritative source is found could silently change knot/link invariants.

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

- Complete for all source/data actually contained in `report_bundle.zip`.
- Blocked for a runnable mathematical program because the snapshot omitted required internal modules.
- The original ZIP must remain archived until the missing source is recovered and the stored outputs are independently reproduced.
