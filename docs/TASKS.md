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
- [x] Separate maintained frontend/workbench evaluation and catalog access from mathematical implementation; historical scripts and legacy paths remain compatibility evidence.
- [x] Define and freeze the small M3 frontend application API in `docs/APPLICATION_API.md`.
- [x] Defer removal of recovered demo-specific defaults and presentation hard-coding to M3 UX design; it is not needed for the M2 boundary.
- [x] Centralize frontend branch/model configuration in the service catalog and preserve mathematical conventions in `docs/MATH_CONVENTIONS.md`; broader configuration is deferred to M3/M4.
- [x] Add structured service error types for invalid frontend input and unknown application selections.

## M3 — Desktop application

- [x] Create a PySide6 application shell.
- [x] Add a convention-explicit custom R/check-R braid-operator engine through the application service boundary.
- [x] Add an offline independent Knot Atlas oracle suite with multi-knot braid-sign calibration, exact Jones/A2 checks, custom check-R parity, and negative controls.
- [x] Add knot/link or braid input workflow (custom signed braid input is available through the Custom R/check-R operator workflow).
- [x] Add invariant/calculation selection, including catalog examples and project-native custom braids.
- [x] Add result display and copy/export support for invariant calculations and custom braid-operator results.
- [x] Run expensive symbolic invariant evaluation and custom-matrix validation/operator work outside the UI thread.
- [x] Add clear validation and error messages for the custom R/check-R workflow, including structural validity versus relation-verification status.

## M4 — Distribution

- [x] Add PyInstaller build configuration.
- [x] Add Windows build workflow in GitHub Actions.
- [x] Produce a standalone downloadable build artifact with packaged executable smoke validation.
- [x] Add single-source application version metadata and lightweight version checks.
- [x] Add tag-driven release workflow and document the portable ZIP installer strategy.
- [x] Add the per-user Inno Setup installer, shared Windows artifact build script, stable release assets, checksum manifest, and installer/portable smoke checks.
- [x] Add the bilingual README download landing section and clean-machine Windows acceptance checklist.
- [x] Prepare the `0.1.1` release candidate: version metadata, bilingual notes, pre-tag state documentation, and a non-publishing dry-run contract.
- [x] Prepare the `0.1.2` desktop-hotfix release candidate: single-source version bump, bilingual hotfix notes, pre-tag state docs, and non-publishing dry-run validation contract.

## M5 — Productization

- [x] Add a maintained Qt-native braid visualization with project-native crossing semantics, zoom/pan/fit, and SVG/PNG export.
- [x] Curated example library with provenance/status metadata and service-driven searchable browser.
- [x] Deterministic versioned `.knotcalc.json` save/load for invariant and custom R/check-R setups without automatic evaluation.
- [x] Export results through a coherent File → Export route while preserving service serializers and preview SVG/PNG exports.
- [x] Mathematical explanation panel backed by frontend-neutral service descriptors with formal/candidate/operator-only boundaries.
- [x] Bilingual offline user documentation and Help access in the maintained PySide6 application.
- [x] README screenshots/demo refresh path and bilingual installation/download guidance.

## Post-v0.1.1 desktop hotfix

- [x] Give invariant braid setup/preview and calculation/results separate resizable pages, with explicit manual input, readable scrollable branches, and optional shared side docks.

## M6 — Measured mathematical performance

- [x] Add a reproducible, non-CI benchmark/profiling harness and record symbolic/numeric baseline and after measurements.
- [x] Separate built-in runtime R construction from validated research diagnostics for formal branches; retain candidate projector metadata.
- [x] Reuse bounded, defensively copied local data and exact one-strand normalization scalars; verify matrix/output equivalence.
- [x] Document matrix-free contraction and sl2 Hecke/Temperley–Lieb follow-up designs without implementing those backends in this pass.


## M6 — Result presentation and preview continuity

- [x] Remove false non-crossing strand breaks from the maintained braid preview by localizing every visible gap to a registered crossing shared by the Qt and SVG renderers.
- [x] Add Compact and Detailed maintained result views, defaulting to Compact without changing deterministic JSON export content.
- [x] Add exact symbolic relabeling for sl2 standard Jones-variable `t` form and maintained Atlas-comparable variable forms only when the conversion is an unambiguous Laurent rewrite.
- [x] Keep numeric `q` results scalar-only in Compact mode and keep the sl2 spin-1 branch explicitly candidate-only without claiming a final standard colored-Jones identification.
