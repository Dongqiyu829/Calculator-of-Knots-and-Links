# Recovered Source Inventory

Last updated: 2026-09-21

## Recovery provenance

The original snapshot is retained at `archive/report_bundle.zip`.

- ZIP root: `report_bundle/`
- SHA-256: `df0d35c0867b85b89d78e3427554cf3b4ebfb796b4db185877567cb5782d97a0`
- Snapshot note: created for a UROP report; `VERSION.txt` says the source was not in a Git repository.
- Archive contents: 55 files: 9 Python source/script files, 2 benchmark input files, 27 generated artifact files, 7 compiled bytecode files, 7 Markdown documents, and 3 root metadata files.

The recoverable Python source, entry scripts, and benchmark inputs were copied byte-for-byte into normal repository paths. `tests/test_recovered_baseline.py` verifies them against the archive. Generated results and bytecode were not expanded into the working tree; they remain available in the archived snapshot, while a small curated fixture records the known-good outputs used by regression tests.

## Recovered Python source

All seven source files below now live at their original paths under `src/benchmark_lab/`:

| File | Responsibility | Important internal dependency |
| --- | --- | --- |
| `src/benchmark_lab/__init__.py` | Public imports for the benchmark package | `branch_adapter`, `registry` |
| `src/benchmark_lab/audit.py` | Per-pair detailed audit records and comparisons | recovered benchmark modules; missing evaluators |
| `src/benchmark_lab/branch_adapter.py` | Fixed three-branch adapter and `q` parsing | missing `src.braid` and `src.invariants` modules |
| `src/benchmark_lab/io_utils.py` | CSV, JSON, Markdown, and artifact-path helpers | standard library only |
| `src/benchmark_lab/profile_runner.py` | Pair evaluation and separation-profile construction | recovered benchmark modules; missing evaluators |
| `src/benchmark_lab/profile_summary.py` | Profile and expectation summary counts | `profile_runner` |
| `src/benchmark_lab/registry.py` | CSV/JSON registry parsing and validation | missing `src.braid.braid_word.BraidWord` |

No other mathematical, GUI, workbench, algebra, braid, R-matrix, or invariant source modules are present in the ZIP or any Git commit/branch inspected during recovery.

## Scripts and entry points

The archive contains no notebooks. It contains two command-line scripts, now restored byte-for-byte:

| File | Intended invocation from repository root | Current status |
| --- | --- | --- |
| `examples/benchmark_lab/run_benchmark_profiles.py` | `python examples/benchmark_lab/run_benchmark_profiles.py --input data/benchmark_lab/benchmark_pairs_template.csv --q 2` (also documented with `3`, `5`, or symbolic `q`) | Blocked at import time because `src.braid` and `src.invariants` were not included in the snapshot. |
| `examples/benchmark_lab/run_benchmark_audit.py` | `python examples/benchmark_lab/run_benchmark_audit.py --input data/benchmark_lab/benchmark_pairs_template.csv --pair P03 --q q` (the snapshot also documents P01/P04 with numeric `q`) | Blocked by the same missing internal modules. |

There is no recoverable desktop GUI entry point. The snapshot README claims that a GUI/workbench and main branch evaluators existed, but their files are absent. The commands above are therefore documented entry points, not currently runnable application paths.

## Input data

Both inputs were restored byte-for-byte under `data/benchmark_lab/`:

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

### Missing internal dependencies

These imports are referenced but not included in the archive or repository history:

- `src.braid.braid_word.BraidWord`
- `src.invariants.branch_registry.evaluate_sl2_fundamental_branch`
- `src.invariants.branch_registry.evaluate_sl2_spin1_branch`
- `src.invariants.branch_registry.evaluate_sl3_fundamental_branch`
- `src.invariants.branch_results.InvariantBranchResult`

The snapshot docs also mention `pytest` for tests, `tkinter` for a GUI, and `tools/create_report_bundle.py`; none is imported or supplied by the recovered source. No dependency manifest (`pyproject.toml`, `requirements.txt`, lock file, or equivalent) exists in the snapshot.

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

## Recovery limitations and next evidence needed

- The original mathematical evaluator code is missing, so stored calculations cannot yet be recomputed.
- The claimed GUI/workbench cannot be recovered from this ZIP.
- P01 is labelled a “positive stabilization candidate” while its last generator is `-2`; the absent braid convention code is required to resolve that naming/sign ambiguity.
- R-matrix normalization, tensor-factor ordering, trace/framing normalization, and polynomial normalization are not implemented or defined in the recovered files.
- The original ZIP should remain under `archive/` until missing source is obtained and the stored results can be reproduced independently. It is safe to treat it as an archive, but not yet safe to delete it.
