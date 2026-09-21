# Task Queue

Tasks are ordered by priority. Agents should not skip ahead unless a dependency makes the next task impossible.

## M0 — Repository recovery

- [x] Extract `report_bundle.zip` into a temporary working area and inventory every source, notebook, report, asset, generated file, and dependency.
- [x] Identify all current executable entry points and document how to run them (both recovered CLIs are currently blocked by missing internal modules).
- [x] Move actual source files into a normal repository structure without changing behaviour.
- [x] Add an appropriate `.gitignore` and exclude caches/build output.
- [x] Preserve the original bundle temporarily under `archive/report_bundle.zip` until the recovered source tree is verified.
- [x] Create `docs/SOURCE_INVENTORY.md` describing the recovered project.
- [x] Create `docs/MATH_CONVENTIONS.md` from evidence in the existing implementation.
- [ ] Recover the missing `src.braid` and `src.invariants` implementations from an authoritative source; do not reconstruct their conventions from guesses.
- [ ] Re-run the documented benchmark CLIs and compare their results with the archived output fixture.

## M1 — Baseline and tests

- [ ] Create a minimal `pyproject.toml`.
- [ ] Introduce a `src/` layout only after existing imports and entry points are understood.
- [ ] Add pytest.
- [ ] Convert known-good calculations into executable regression tests once the missing evaluators are recovered. Stored q=2/3/5 and symbolic outputs are already frozen as archive-backed fixtures.
- [ ] Record expected outputs for representative knots/links and braid words.
- [ ] Add smoke tests for all current entry points.

## M2 — Core refactor

- [ ] Separate mathematical logic from scripts, notebooks, and GUI code.
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
