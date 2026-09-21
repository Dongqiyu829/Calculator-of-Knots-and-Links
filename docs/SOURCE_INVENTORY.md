# Recovered Source Inventory

Last updated: 2026-09-21

## Recovery status

This inventory began with the incomplete report ZIP described below. Issue #5
subsequently recovered the authoritative historical project from
`C:\cpp\comp2012\Quantum Group Knot`. The full exact manifest, entry points,
dependencies, exclusions, GUI architecture, and verification record are in
`docs/AUTHORITATIVE_RECOVERY.md`.

The authoritative recovery restores `src.braid`, `src.invariants`, algebra and
R-matrix builders, all three benchmark branch evaluators, the Tkinter
GUI/workbench, examples, tests, data, documentation, and
`tools/create_report_bundle.py`. The local authoritative copy of
`report_bundle.zip` has the same SHA-256 as the repository archive, which ties
the complete source tree to the previously recovered benchmark snapshot.

## Phase 1 archive provenance

The original snapshot is retained at `archive/report_bundle.zip`.

- ZIP root: `report_bundle/`
- SHA-256: `df0d35c0867b85b89d78e3427554cf3b4ebfb796b4db185877567cb5782d97a0`
- Snapshot note: created for a UROP report; `VERSION.txt` says the source was not in a Git repository.
- Archive contents: 55 files: 9 Python source/script files, 2 benchmark input files, 27 generated artifact files, 7 compiled bytecode files, 7 Markdown documents, and 3 root metadata files.

The recoverable Python source, entry scripts, and benchmark inputs were copied
content-identically into normal repository paths. The archive has CRLF endings
and Git checkouts use LF, so `tests/test_recovered_baseline.py` normalizes line
endings for source comparison while verifying the ZIP itself by exact SHA-256.
Generated results and bytecode were not expanded into the working tree; they
remain available in the archive, while a curated fixture records known-good
outputs.

## Recovered Python source

All seven source files below now live at their original paths under `src/benchmark_lab/`:

| File | Responsibility | Important internal dependency |
| --- | --- | --- |
| `src/benchmark_lab/__init__.py` | Public imports for the benchmark package | `branch_adapter`, `registry` |
| `src/benchmark_lab/audit.py` | Per-pair detailed audit records and comparisons | recovered benchmark modules and restored evaluators |
| `src/benchmark_lab/branch_adapter.py` | Fixed three-branch adapter and `q` parsing | restored `src.braid` and `src.invariants` modules |
| `src/benchmark_lab/io_utils.py` | CSV, JSON, Markdown, and artifact-path helpers | standard library only |
| `src/benchmark_lab/profile_runner.py` | Pair evaluation and separation-profile construction | recovered benchmark modules and restored evaluators |
| `src/benchmark_lab/profile_summary.py` | Profile and expectation summary counts | `profile_runner` |
| `src/benchmark_lab/registry.py` | CSV/JSON registry parsing and validation | restored `src.braid.braid_word.BraidWord` |

No other mathematical, GUI, workbench, algebra, braid, R-matrix, or invariant
source modules are present in the ZIP. They were later recovered from the
authoritative local folder; see `docs/AUTHORITATIVE_RECOVERY.md`.

## Scripts and entry points

The archive contains no notebooks. It contains two command-line scripts, now
restored content-identically (with Git-normalized line endings):

| File | Intended invocation from repository root | Current status |
| --- | --- | --- |
| `examples/benchmark_lab/run_benchmark_profiles.py` | `python examples/benchmark_lab/run_benchmark_profiles.py --input data/benchmark_lab/benchmark_pairs_template.csv --q 2` (also documented with `3`, `5`, or symbolic `q`) | Runnable after the authoritative issue #5 recovery. |
| `examples/benchmark_lab/run_benchmark_audit.py` | `python examples/benchmark_lab/run_benchmark_audit.py --input data/benchmark_lab/benchmark_pairs_template.csv --pair P03 --q q` (the snapshot also documents P01/P04 with numeric `q`) | Runnable after the authoritative issue #5 recovery. |

The ZIP itself has no GUI entry point. The authoritative recovery supplied the
Tkinter launchers `examples/demo_launcher_gui.py`,
`examples/braid_workbench_gui.py`, and
`examples/demo_launcher_gui_legacy.py`.

## Input data

Both inputs were restored content-identically under `data/benchmark_lab/`:

- `data/benchmark_lab/benchmark_pairs_template.csv`
- `data/benchmark_lab/benchmark_pairs_template.json`

They describe the same five pair IDs, P01 through P05. P05 has placeholder braid data and is explicitly marked `needs_audit`.

## Dependencies and imports

### External dependency

- `sympy`: imported by `branch_adapter.py`, `profile_runner.py`, and `audit.py`. The snapshot documentation records SymPy as the sole external runtime dependency.

### Standard-library imports

- `argparse`
- `collections.Counter`
- `csv`
- `dataclasses`
- `io`
- `json`
- `pathlib`
- `sys`
- `typing`

### Formerly missing internal dependencies

These imports are absent from the ZIP but restored from the authoritative source:

- `src.braid.braid_word.BraidWord`
- `src.invariants.branch_registry.evaluate_sl2_fundamental_branch`
- `src.invariants.branch_registry.evaluate_sl2_spin1_branch`
- `src.invariants.branch_registry.evaluate_sl3_fundamental_branch`
- `src.invariants.branch_results.InvariantBranchResult`

The authoritative source also restores the `unittest`-style test suite, Tkinter
GUI, and `tools/create_report_bundle.py`. It still contains no dependency
manifest (`pyproject.toml`, requirements file, lock file, or equivalent).

## Documentation and metadata in the archive

These files were inventoried as historical/report material. They remain in `archive/report_bundle.zip` because several contain duplicated sections, refer to missing code, or describe a fuller repository than the snapshot actually contains:

- `README.md`
- `LICENSE` — the MIT license text appears twice consecutively; a single canonical copy is now at repository root.
- `VERSION.txt`
- `docs/benchmark_lab/README.md`
- `docs/benchmark_lab/benchmark_audit.md`
- `docs/benchmark_lab/benchmark_profiles.md`
- `docs/benchmark_summary.md`
- `docs/github_release_checklist.md`
- `docs/report_appendix.md`
- `docs/reproducibility.md`

There are no image, audio, video, font, or other binary assets in the snapshot.

## Generated artifact inventory

The following 27 files are generated benchmark outputs. They were inspected but not copied into the normal source tree because `artifacts/` is generated output and is now ignored. They remain inside the archived ZIP.

### `artifacts/benchmark_lab/benchmark_pairs_template_q_2/`

- `audit_P01_q_2.json`
- `audit_P01_q_2.md`
- `audit_P04_q_2.json`
- `audit_P04_q_2.md`
- `pair_level_results.csv`
- `pair_level_results.json`
- `summary.csv`
- `summary.json`
- `summary.md`

### `artifacts/benchmark_lab/benchmark_pairs_template_q_3/`

- `audit_P03_q_3.json`
- `audit_P03_q_3.md`
- `pair_level_results.csv`
- `pair_level_results.json`
- `summary.csv`
- `summary.json`
- `summary.md`

### `artifacts/benchmark_lab/benchmark_pairs_template_q_5/`

- `audit_P03_q_5.json`
- `audit_P03_q_5.md`
- `pair_level_results.csv`
- `pair_level_results.json`
- `summary.csv`
- `summary.json`
- `summary.md`

### `artifacts/benchmark_lab/benchmark_pairs_template_q_q/`

- `audit_P01_q_q.json`
- `audit_P01_q_q.md`
- `audit_P03_q_q.json`
- `audit_P03_q_q.md`

## Cache and build inventory

Seven CPython 3.12 bytecode cache files were present and intentionally excluded from the recovered tree:

- `src/benchmark_lab/__pycache__/__init__.cpython-312.pyc`
- `src/benchmark_lab/__pycache__/audit.cpython-312.pyc`
- `src/benchmark_lab/__pycache__/branch_adapter.cpython-312.pyc`
- `src/benchmark_lab/__pycache__/io_utils.cpython-312.pyc`
- `src/benchmark_lab/__pycache__/profile_runner.cpython-312.pyc`
- `src/benchmark_lab/__pycache__/profile_summary.cpython-312.pyc`
- `src/benchmark_lab/__pycache__/registry.cpython-312.pyc`

No build directories, distributions, wheels, installers, coverage output, or virtual environments are present in the ZIP.

## Baseline evidence retained

The curated fixture `tests/fixtures/recovered_benchmark_baselines.json` records:

- the archive hash;
- every stored numeric separation profile at `q=2`, `q=3`, and `q=5`;
- exact stored P03 branch outputs in those numeric modes; and
- exact stored symbolic P03 branch differences.

The primary stored result is P03 with profile `(0,1,1)` in all three numeric modes and in the symbolic audit: `sl2_fundamental` is equal, while `sl2_3d_9x9` and `sl3_fundamental` differ. P01 and P04 disagree with their expected metadata in at least one branch and remain audit cases, not validated conclusions.

## Phase 1 limitations resolved by issue #5

- The evaluator code and GUI/workbench are now present.
- Numeric q=2, q=3, and q=5 benchmark JSON outputs reproduce the archive.
- P01 is demonstrably a negative stabilization under the recovered sign
  convention, despite its historical “positive” label.
- R-matrix, tensor ordering, trace/framing, eigenvalue, and polynomial
  conventions are now documented from primary source evidence in
  `docs/MATH_CONVENTIONS.md`.
- The original ZIP remains under `archive/` as immutable provenance.
