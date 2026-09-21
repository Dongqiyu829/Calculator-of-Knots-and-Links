# Task Queue

Tasks are ordered by priority. Agents should not skip ahead unless a dependency makes the next task impossible.

## M0 — Repository recovery

- [ ] Extract `report_bundle.zip` into a temporary working area and inventory every source, notebook, report, asset, generated file, and dependency.
- [ ] Identify all current executable entry points and document how to run them.
- [ ] Move actual source files into a normal repository structure without changing behaviour.
- [ ] Add an appropriate `.gitignore` and exclude caches/build output.
- [ ] Preserve the original bundle temporarily under an archival path until the recovered source tree is verified.
- [ ] Create `docs/SOURCE_INVENTORY.md` describing the recovered project.
- [ ] Create `docs/MATH_CONVENTIONS.md` from evidence in the existing implementation.

## M1 — Baseline and tests

- [ ] Create a minimal `pyproject.toml`.
- [ ] Introduce a `src/` layout only after existing imports and entry points are understood.
- [ ] Add pytest.
- [ ] Convert known-good calculations into regression tests.
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
