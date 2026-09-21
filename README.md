# Calculator of Knots and Links

Calculator of Knots and Links is a project for computing knot and link invariants, with a long-term goal of becoming a research-quality mathematical calculator that is also usable as a normal installable desktop application.

## Project status

The first recovery pass over the bundled research snapshot is complete. The recoverable benchmark source, scripts, and data now live in normal repository paths.

The snapshot was incomplete: it references braid and invariant evaluators, a GUI, and a workbench that were not included in the ZIP or repository history. The restored benchmark CLIs therefore cannot run until those internal modules are recovered. No mathematical implementation has been guessed or replaced.

See:

- `AGENTS.md` — development and agent rules
- `docs/PROJECT_STATE.md` — current project state
- `docs/TASKS.md` — prioritized task queue
- `docs/SOURCE_INVENTORY.md` — complete snapshot inventory, entry points, dependencies, and recovery gaps
- `docs/MATH_CONVENTIONS.md` — conventions evidenced by the recovered files and unresolved normalization questions

## Repository contents

- `src/benchmark_lab/` — byte-for-byte recovered benchmark/profile/audit layer
- `examples/benchmark_lab/` — recovered command-line entry scripts
- `data/benchmark_lab/` — recovered benchmark registries
- `tests/` — archive-integrity and stored-output regression tests
- `archive/report_bundle.zip` — original snapshot retained as recovery evidence
- `CITATION.cff` — citation metadata

Run the currently available recovery tests with:

```bash
python -m pytest
```

The intended benchmark commands and their current blocker are documented in `docs/SOURCE_INVENTORY.md`.

## Development principle

Mathematical correctness comes first. Refactors must preserve validated braid, R-matrix, trace, normalization, and polynomial conventions unless a change is explicitly documented and tested.

## Citation

If you use this repository in academic work, please cite the software repository using the metadata in `CITATION.cff`.

GitHub can export citation formats through the repository's **Cite this repository** feature.

## Author

Qiyu Dong
