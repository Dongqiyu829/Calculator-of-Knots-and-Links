# Calculator of Knots and Links

Calculator of Knots and Links is a research-oriented knot/link invariant calculator with a maintained PySide6 desktop frontend, a reusable Python/SymPy service boundary, and preserved historical benchmark/reference code.

The project prioritizes mathematical correctness, reproducibility, and explicit convention handling over UI polish.

## Current status

The historical source recovery, package/test baseline, service-layer refactor, and the core M3 desktop workflow are complete.

The repository now contains:

- the recovered braid, algebra, R-matrix, invariant, benchmark, Tkinter/workbench, and catalog code;
- a maintained PySide6 desktop application;
- frontend-neutral application services and result DTOs;
- a convention-explicit custom R/check-R braid-operator engine;
- representative regression fixtures from the authoritative recovered implementation;
- an offline external Knot Atlas oracle suite for independent mathematical validation.

M4 distribution is now in progress. The first supported target is a reproducible PyInstaller `onedir` Windows build produced and smoke-tested by GitHub Actions; stable version metadata, tagged releases, and installer strategy remain follow-up work.

## Desktop application

Install the desktop dependencies and launch the maintained application with:

```bash
python -m pip install -e ".[desktop]"
python -m src.desktop
```

The desktop application does not evaluate invariants on startup. Expensive invariant and custom-matrix operations run only on request and are dispatched outside the Qt UI thread.

### Built-in invariant workflow

The primary desktop tab supports both catalog examples and project-native custom braids.

Users can:

- choose a built-in knot/link/braid example;
- enter a custom braid by strand count and signed Artin generators;
- select one or more available invariant branches;
- enter exact or symbolic q values such as `2`, `3/2`, or `q`;
- run calculations in a background Qt worker;
- inspect formal/candidate status, normalization, variable convention, representation metadata, notes, and warnings;
- copy selected or complete text results;
- copy deterministic JSON;
- export results to JSON or text.

Current built-in branches are:

- `sl2_fundamental` — Jones-compatible, **formal**;
- `sl3_fundamental` — A2/sl3 fundamental, **formal**;
- `sl2_spin1` / workbench model `sl2_3d_9x9` — 3-dimensional spin-1 branch, **candidate**.

The candidate branch remains explicitly labelled as such and is not presented as having a fully resolved external normalization.

### Custom R / check-R workflow

The advanced desktop tab accepts user-supplied local matrices and constructs braid-group operators.

Supported features include:

- paste matrix text or load simple text/JSON contents;
- explicitly choose whether the input is raw `R` or `check-R`;
- convert raw `R` using the documented convention `check-R = P R`;
- infer or validate the local dimension `d`;
- check matrix shape and tensor-square compatibility;
- inspect invertibility;
- optionally test the check-R braid relation;
- optionally test the standard raw-R Yang-Baxter equation;
- distinguish relation status as verified, failed, not checked, or undecidable;
- enter arbitrary signed braid words;
- use the inverse local operator for negative generators;
- construct the full `d^n x d^n` braid operator;
- inspect ordered generator diagnostics and tensor-growth warnings;
- copy/export deterministic JSON.

This workflow constructs braid operators only. An arbitrary R-matrix is **not** automatically treated as a knot/link invariant recipe: quantum trace/enhancement, Markov normalization, framing, and related data are separate mathematical structure.

## Mathematical implementation

For the full mathematical derivation and code map—from braid words and representation bases through raw \(R\), \(\check R = PR\), Yang-Baxter validation, tensor embedding, enhanced traces, branch normalization, worked trefoil/figure-eight examples, and the custom R-matrix extension—see:

- [Mathematical Implementation Guide](docs/MATHEMATICAL_IMPLEMENTATION.md)

The guide is intended for both human readers and AI coding agents. Exact convention records remain in `docs/MATH_CONVENTIONS.md`, while independent external checks remain in `docs/EXTERNAL_VALIDATION.md`.

## Mathematical validation

The project keeps internal compatibility regression data separate from independent external validation.

Representative recovered outputs are frozen in:

- `tests/fixtures/representative_invariant_regressions.json`

External validation is documented in:

- `docs/EXTERNAL_VALIDATION.md`
- `tests/fixtures/knot_atlas_oracles.json`

The Knot Atlas suite currently includes `3_1`, `4_1`, `5_1`, `5_2`, and `6_1`.

Current calibrated external correspondences include:

- Knot Atlas braid generators map to project generators by a global sign reversal across the calibration set;
- Jones/sl2 fundamental uses the documented variable correspondence `q_atlas = q_project^2`;
- sl3/A2 fundamental uses `q_atlas = q_project^-1`;
- the spin-1/A1 weight-2 comparison remains diagnostic/candidate rather than being forced to match.

The custom check-R engine is also parity-tested against the built-in sl2 fundamental braid operator on representative braids, including symbolic coverage.

## Repository contents

- `src/` — mathematical engine, services, maintained PySide6 desktop application, recovered Tkinter/workbench code
- `examples/` — historical CLI/demo/GUI entry scripts
- `data/` — historical benchmark registries
- `tests/` — unit, regression, architecture, GUI-smoke, external-oracle, and compatibility tests
- `docs/` — project state, API contract, mathematical conventions, validation and recovery documentation
- `archive/report_bundle.zip` — original snapshot retained as provenance
- `CITATION.cff` — citation metadata

## Development setup

Install the package and test dependencies with:

```bash
python -m pip install -e ".[test]"
```

Install both test and desktop dependencies as needed for development.

Test tiers, CI behavior, and headless GUI instructions are documented in `docs/TESTING.md`.

Important project documents:

- `AGENTS.md` — development and agent rules
- `docs/PROJECT_STATE.md` — current project state
- `docs/TASKS.md` — prioritized task queue
- `docs/APPLICATION_API.md` — supported frontend-neutral application API
- `docs/MATHEMATICAL_IMPLEMENTATION.md` — complete end-to-end mathematical implementation guide
- `docs/MATH_CONVENTIONS.md` — established braid/R-matrix/q/trace conventions
- `docs/CUSTOM_RMATRIX_ENGINE.md` — custom R/check-R operator contract
- `docs/EXTERNAL_VALIDATION.md` — independent Knot Atlas validation
- `docs/REPRESENTATIVE_REGRESSIONS.md` — recovered compatibility baselines
- `docs/AUTHORITATIVE_RECOVERY.md` — source-recovery provenance
- `docs/DISTRIBUTION.md` — Windows standalone build and artifact instructions

## Distribution status

The first Windows standalone distribution path uses a PyInstaller `onedir` bundle. On Windows:

```powershell
python -m pip install -e ".[desktop,build]"
python -m PyInstaller --clean --noconfirm packaging/Calculator-of-Knots-and-Links.spec
```

The executable is produced under `dist\\Calculator-of-Knots-and-Links\\`. A packaging-only `--smoke-test` mode constructs the maintained PySide6 window, verifies bundled runtime imports, and exits without entering the normal event loop or evaluating an invariant.

The Windows GitHub Actions workflow builds the bundle, smoke-tests the packaged executable, creates `Calculator-of-Knots-and-Links-windows-x64.zip`, extracts that ZIP, smoke-tests the extracted executable again, and only then uploads it as an Actions artifact.

See `docs/DISTRIBUTION.md` for exact local-build and artifact-download instructions. This is not yet a tagged GitHub Release or installer.

## Development principle

Mathematical correctness comes first. Refactors must preserve validated braid, R-matrix, tensor-ordering, q, trace, framing, eigenvalue, and polynomial conventions unless a change is explicitly documented, independently justified, and regression-tested.

## Citation

If you use this repository in academic work, please cite the software repository using the metadata in `CITATION.cff`.

GitHub can export citation formats through the repository's **Cite this repository** feature.

## Author

Qiyu Dong
