# Calculator of Knots and Links

Calculator of Knots and Links is a project for computing knot and link invariants, with a long-term goal of becoming a research-quality mathematical calculator that is also usable as a normal installable desktop application.

## Project status

The authoritative historical source recovery is complete. The braid, R-matrix,
invariant, benchmark, GUI/workbench, example, and test code now lives in normal
repository paths.

The first archived ZIP was incomplete, but issue #5 recovered its missing modules
from the authoritative local source. No mathematical implementation was guessed,
refactored, or normalized during that pass. The historical Tkinter frontends
remain available as compatibility/reference applications. The maintained desktop
shell uses PySide6 and is intentionally limited to service-driven startup,
example/branch discovery, and layout in this first M3 step.

See:

- `AGENTS.md` — development and agent rules
- `docs/PROJECT_STATE.md` — current project state
- `docs/TASKS.md` — prioritized task queue
- `docs/SOURCE_INVENTORY.md` — complete snapshot inventory, entry points, dependencies, and recovery gaps
- `docs/AUTHORITATIVE_RECOVERY.md` — exact issue #5 recovery manifest and verification record
- `docs/MATH_CONVENTIONS.md` — conventions evidenced by the recovered files and unresolved normalization questions

## Repository contents

- `src/` — recovered mathematical engine, benchmark layers, and Tkinter workbench
- `examples/` — historical CLI/demo/GUI entry scripts
- `data/` — historical benchmark registries
- `tests/` — historical tests, archive-integrity regression tests, and non-interactive entrypoint smoke tests
- `archive/report_bundle.zip` — original snapshot retained as recovery evidence
- `CITATION.cff` — citation metadata

Install the recovered package and its test dependencies with:

```bash
python -m pip install -e ".[test]"
```

Install and launch the maintained PySide6 shell with:

```bash
python -m pip install -e ".[desktop]"
python -m src.desktop
```

It performs no invariant evaluation on startup. Full braid editing, evaluation,
and export are subsequent M3 work; no PyInstaller configuration is included yet.

Test tiers, CI behavior, and headless GUI instructions are documented in
`docs/TESTING.md`. Historical entry points and benchmark reproduction commands
are documented in `docs/AUTHORITATIVE_RECOVERY.md`.

## Development principle

Mathematical correctness comes first. Refactors must preserve validated braid, R-matrix, trace, normalization, and polynomial conventions unless a change is explicitly documented and tested.

## Citation

If you use this repository in academic work, please cite the software repository using the metadata in `CITATION.cff`.

GitHub can export citation formats through the repository's **Cite this repository** feature.

## Author

Qiyu Dong
