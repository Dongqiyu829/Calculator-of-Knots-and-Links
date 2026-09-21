# Task Queue

Tasks are ordered by priority. Agents should not skip ahead unless a dependency makes the next task impossible.

## M0 — Repository recovery

- [x] Extract `report_bundle.zip` into a temporary working area and inventory every source, notebook, report, asset, generated file, and dependency.
- [x] Identify all current executable entry points and document how to run them (the benchmark CLIs became runnable after issue #5 recovery).
- [x] Move actual source files into a normal repository structure without changing behaviour.
- [x] Add an appropriate `.gitignore` and exclude caches/build output.
- [x] Preserve the original bundle temporarily under `archive/report_bundle.zip` until the recovered source tree is verified.
- [x] Create `docs/SOURCE_INVENTORY.md` describing the recovered project.
- [x] Create `docs/MATH_CONVENTIONS.md` from evidence in the existing implementation.
- [x] Recover the missing `src.braid` and `src.invariants` implementations from the authoritative historical source supplied for issue #5.
- [x] Recover `BraidWord`, all three branch evaluators, the Tkinter GUI/workbench, historical tests, examples, data, and the report-bundle tool without refactoring them.
- [x] Re-run the documented numeric benchmark CLIs at q=2, q=3, and q=5 and compare their JSON results exactly with the archived output fixture.
- [x] Run and record the symbolic benchmark reproduction; preserve any observed runtime/result evidence in `docs/AUTHORITATIVE_RECOVERY.md`.
- [x] Document recovered entry points, dependencies, established mathematical conventions, documentation discrepancies, and GUI/workbench architecture.

## M1 — Baseline and tests

- [x] Create a minimal `pyproject.toml` with runtime and test dependencies.
- [x] Confirm the recovered `src` import package and retain it without a style-only move.
- [x] Add explicit pytest configuration and test tiers.
- [x] Convert additional known-good calculations into executable regression tests. Stored q=2/3/5 and symbolic outputs remain frozen as archive-backed fixtures.
- [x] Record expected outputs for representative knots/links and braid words in the fixture-backed compatibility manifest.
- [x] Add non-interactive smoke tests for the principal current executable entry points.
- [x] Keep fast/core, GUI smoke, and slow/extended mathematical test coverage separately runnable and documented.

## M2 — Core refactor

- [x] Extract a UI-independent application/service boundary for braid parsing and evaluation; workbench and Tkinter compatibility adapters now share it.
- [x] Define the provisional application API, frontend-neutral branch catalog, and structured service errors for current frontends.
- [x] Add frontend-neutral application result DTOs and deterministic reporting/serialization for maintained frontends.
- [x] Route maintained workbench pair comparison through the application service evaluation results.
- [ ] Separate remaining mathematical logic from scripts, notebooks, and GUI code.
- [ ] Define a small stable public API.
- [ ] Remove demo-specific hard-coding where safe.
- [ ] Centralize configuration and mathematical conventions.
- [ ] Add structured error types for invalid inputs.

## M3 — Desktop application

- [ ] Create a PySide6 application shell.
- [ ] Add knot/link or braid input workflow.
- [ ] Add invariant/calculation selection.
- [ ] Add result display and copy/export support.
- [ ] Run expensive symbolic work outside the UI thread.
- [ ] Add clear validation and error messages.

## M4 — Distribution

- [ ] Add PyInstaller build configuration.
- [ ] Add Windows build workflow in GitHub Actions.
- [ ] Produce a standalone downloadable build.
- [ ] Add version metadata.
- [ ] Add release workflow and installer strategy.

## M5 — Productization

- [ ] Curated example library.
- [ ] Save/load calculations.
- [ ] Export results.
- [ ] Mathematical explanation panel.
- [ ] User documentation.
- [ ] Screenshots and installation instructions in README.
