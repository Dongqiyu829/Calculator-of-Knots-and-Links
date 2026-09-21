# Authoritative Source Recovery

Last updated: 2026-09-21

## Provenance and scope

Issue #5 used `C:\cpp\comp2012\Quantum Group Knot` as the authoritative
historical source. The folder has no `.git` directory, so there is no upstream
commit identifier to retain. Its `report_bundle.zip` has SHA-256
`df0d35c0867b85b89d78e3427554cf3b4ebfb796b4db185877567cb5782d97a0`,
exactly matching `archive/report_bundle.zip` in this repository. The existing
`src/benchmark_lab`, `examples/benchmark_lab`, and `data/benchmark_lab` files
were content-identical to the authoritative copies after normalizing CRLF/LF.

The recovery copied source, examples, tests, data, Markdown/CSV documentation,
and the report-bundle utility. It deliberately excluded `.git`, `.vscode`,
`__pycache__`, `.pyc`, `artifacts`, `report_bundle`, `report_bundle.zip`, build
or distribution output, and virtual environments. Three historical rendered
documents (`docs/document.html`, `docs/MATH descrip.html`, and
`docs/mutant knots.docx`), three root PDFs, and the root `Instruction` file were
inspected as non-runtime research/report material but were not copied. The
authoritative root README, LICENSE, and `.gitignore` were not allowed to replace
the repository's maintained versions.

No mathematical source was refactored or redesigned in this pass.

## Exact recovered runtime files

The authoritative tree contains these Python modules under `src/`:

- `src/__init__.py`
- `src/algebra/{__init__.py,lie_algebra.py,representations.py}`
- `src/benchmark_lab/{__init__.py,audit.py,branch_adapter.py,io_utils.py,profile_runner.py,profile_summary.py,registry.py}`
- `src/braid/{__init__.py,braid_operator.py,braid_word.py}`
- `src/catalog/{__init__.py,braid_examples.py}`
- `src/experiments/{__init__.py,benchmark_registry.py,profile_runner.py,profile_summary.py}`
- `src/gui/{__init__.py,braid_preview_renderer.py,braid_workbench_app.py,braid_workbench.py,demo_launcher.py,demo_launcher_legacy.py}`
- `src/invariants/{__init__.py,benchmark.py,branch_formatter.py,branch_registry.py,branch_results.py,compare_9x9_benchmark.py,convention_audit.py,eyb_diagnostics.py,eyb_invariant.py,jones_debug.py,jones_invariant.py,jones_reference_cases.py,legacy_branch_registry.py,legacy_multibranch_benchmark.py,markov_checks.py,multibranch_benchmark.py,polynomial_result.py,quantum_trace.py,sl2_3d_candidate_benchmark.py,sl2_3d_colored_jones_candidate.py}`
- `src/rmatrix/{__init__.py,projectors.py,rmatrix_base.py,sl2_rmatrix.py,sl3_rmatrix.py}`
- `src/workbench/{__init__.py,comparison.py,experiment_log.py,runner.py,specs.py}`

This restores every missing module named by the benchmark adapter, including
`BraidWord`, `InvariantBranchResult`, and the sl2 fundamental, sl2 spin-1/3D,
and sl3 fundamental branch evaluators.

## Exact recovered entry scripts and examples

The authoritative example set is:

- `examples/benchmark_lab/run_benchmark_audit.py`
- `examples/benchmark_lab/run_benchmark_profiles.py`
- `examples/benchmark_P2_demo.py`
- `examples/benchmark_P3_demo.py`
- `examples/braid_operator_demo.py`
- `examples/braid_workbench_gui.py`
- `examples/check_sl2_3d_knot_atlas_correspondence.py`
- `examples/compare_9x9_discriminating_power_demo.py`
- `examples/compare_9x9_local_data_demo.py`
- `examples/compare_9x9_raw_trace_demo.py`
- `examples/compare_A_type_invariants_demo.py`
- `examples/convention_audit_demo.py`
- `examples/debug_braid_preview.py`
- `examples/debug_compare_10_22_10_35.py`
- `examples/debug_single_trefoil_against_jones.py`
- `examples/demo_launcher_gui.py`
- `examples/demo_launcher_gui_legacy.py`
- `examples/eyb_partial_trace_demo.py`
- `examples/eyb_stabilization_ratio_demo.py`
- `examples/jones_benchmark_demo.py`
- `examples/jones_debug_demo.py`
- `examples/markov_move_demo.py`
- `examples/multibranch_invariant_demo.py`
- `examples/raw_trace_demo.py`
- `examples/representation_summary_demo.py`
- `examples/run_benchmark_experiments.py`
- `examples/sl2_fundamental_eyb_demo.py`
- `examples/sl2_fundamental_rmatrix_demo.py`
- `examples/sl2_spin1_projector_demo.py`
- `examples/sl2_spin1_rmatrix_demo.py`
- `examples/sl3_fundamental_eyb_demo.py`
- `examples/sl3_fundamental_rmatrix_demo.py`
- `examples/sl3_projector_demo.py`

The principal historical entry points are:

```text
python examples/demo_launcher_gui.py
python examples/braid_workbench_gui.py
python examples/demo_launcher_gui_legacy.py
python examples/run_benchmark_experiments.py --input data/benchmark_pairs_template.csv --q 2
python examples/benchmark_lab/run_benchmark_profiles.py --input data/benchmark_lab/benchmark_pairs_template.csv --q 2
python examples/benchmark_lab/run_benchmark_audit.py --input data/benchmark_lab/benchmark_pairs_template.csv --pair P03 --q q
```

The remaining example files are directly executable demonstrations and
diagnostics for the algebra, R-matrix, trace, invariant, and benchmark layers.

## Exact recovered tests

- `tests/benchmark_lab/{__init__.py,test_audit_smoke.py,test_profile_runner_smoke.py,test_registry_smoke.py}`
- `tests/test_benchmark_registry_smoke.py`
- `tests/test_braid_preview_renderer_smoke.py`
- `tests/test_braid_workbench_comparison_smoke.py`
- `tests/test_braid_workbench_gui_smoke.py`
- `tests/test_branch_formatter_smoke.py`
- `tests/test_compare_9x9_benchmark_smoke.py`
- `tests/test_experiment_log_smoke.py`
- `tests/test_eyb_stabilization_regression.py`
- `tests/test_gui_builtin_preview_sync.py`
- `tests/test_gui_custom_vs_branch_evaluator.py`
- `tests/test_gui_dataflow_smoke.py`
- `tests/test_jones_debug_smoke.py`
- `tests/test_legacy_fast_program_smoke.py`
- `tests/test_multibranch_benchmark_smoke.py`
- `tests/test_profile_runner_smoke.py`
- `tests/test_sl2_3d_candidate_catalog_regression.py`
- `tests/test_sl2_3d_candidate_smoke.py`
- `tests/test_sl2_3d_knot_atlas_correspondence.py`
- `tests/test_sl2_jones_compatible_regression.py`
- `tests/test_workbench_input_parity.py`
- `tests/test_workbench_input_schema_smoke.py`

`tests/test_recovered_baseline.py` and its JSON fixture came from the earlier
archive recovery. They are retained alongside the historical tests.

## Exact recovered data, documentation, and tooling

Data:

- `data/benchmark_lab/{benchmark_pairs_template.csv,benchmark_pairs_template.json}` (already present and verified)
- `data/{benchmark_pairs_template.csv,benchmark_pairs_template.json}`

Documentation copied from the authoritative source:

- `docs/benchmark_experiments.md`
- `docs/benchmark_lab/{README.md,benchmark_audit.md,benchmark_profiles.md}`
- `docs/benchmark_pairs.csv`
- `docs/benchmark_summary.md`
- `docs/braid_preview_status.md`
- `docs/braid_workbench_guide.md`
- `docs/current_summary.md`
- `docs/github_release_checklist.md`
- `docs/json_braid_input_schema.md`
- `docs/mathematical_status_note.md`
- `docs/report_appendix.md`
- `docs/reproducibility.md`
- `docs/simple_examples.md`
- `docs/sl2_3d_knot_atlas_correspondence.md`

Tooling:

- `tools/create_report_bundle.py`

## Dependencies and configuration

The only non-standard runtime import is `sympy`. Historical tests are written
with `unittest` conventions and are runnable through `pytest`; the archive
baseline test directly imports `pytest`. GUI entry points use the standard
library `tkinter`. Other standard-library dependencies include `argparse`,
`collections`, `csv`, `dataclasses`, `io`, `itertools`, `json`, `pathlib`,
`sys`, `time`, and `typing`.

The source documents Python 3.12.4 as its development/verification environment.
No `pyproject.toml`, `setup.py`, `setup.cfg`, requirements file, lock file,
tox/nox configuration, CI workflow, or packaging/build configuration exists in
the authoritative folder. None was invented during recovery.

## Established mathematical conventions

The recovered implementation establishes the following, replacing the earlier
unknowns recorded from the incomplete ZIP:

- Positive integer `i` means Artin generator `sigma_i`; negative `-i` means its
  inverse. Writhe is the signed generator count.
- Braid generators use `RMatrixData.braid_matrix`; negative generators use its
  inverse. Embedded operators are multiplied left-to-right in input order.
- Representation bases run from highest to lowest weight and tensor bases use
  the induced lexicographic order.
- `matrix` is the raw literature-facing R matrix and `braid_matrix` is the local
  braid generator `P R`, with `P` the tensor-factor swap.
- The sl2 fundamental braid channels are `q` on J=1 and `-q^-1` on J=0.
- The sl2 spin-1/3D channels J=2, J=1, and J=0 have braid eigenvalues
  `q^4`, `-1`, and `q^-2`, respectively, on basis
  `(w_1,w_0,w_-1)` in lexicographic tensor order.
- The sl3 fundamental Hecke channels have eigenvalues `q` on the symmetric 6
  and `-q^-1` on the antisymmetric 3-bar.
- EYB output is `alpha^-w beta^-n Tr(b mu^tensor-n)`. For sl2 fundamental,
  `mu=diag(q^-1,q)`, `alpha=q^2`, `beta=1`; for sl3 fundamental,
  `mu=diag(q^-2,1,q^2)`, `alpha=q^3`, `beta=1`.
- The sl2 fundamental Jones-compatible output reduces the current P2 output by
  the one-strand unknot and declares `t=q^-2`.
- The sl2 3D branch uses `mu=diag(q^-2,1,q^2)`, `alpha=q^4`, `beta=1`, then
  reduces by its one-strand unknot. The source explicitly labels this a
  candidate normalization; Knot Atlas comparison substitutes `q -> q^2`.

The archive's P01 description says “positive stabilization,” but its added
generator is `-2`. Under the recovered implementation this is a negative
stabilization. The data is preserved; only the documentation discrepancy is
recorded. P01/P04 expectation mismatches are likewise not “fixed.”

## GUI and workbench architecture

The recovered desktop code is Tkinter, not PySide6:

- `src/gui/demo_launcher.py` contains the main demo window and evaluator helper
  functions used by other code.
- `src/gui/braid_workbench_app.py` provides manual/JSON input, result tables,
  exports, and experiment logging.
- `src/workbench/specs.py`, `comparison.py`, `runner.py`, and
  `experiment_log.py` hold input models, comparisons, batch execution, and logs.
- `src/gui/braid_preview_renderer.py` separates braid geometry/SVG generation
  from its Tk canvas renderer.
- `src/gui/demo_launcher_legacy.py` and its example retain the legacy branch
  behavior.

The historical dependency direction is not clean: `src/workbench/runner.py`
imports evaluator helpers from `src.gui.demo_launcher`. That is recorded as
architecture debt and intentionally left unchanged. No PySide6 work belongs to
this recovery PR.

## Verification record

The original authoritative suite was run in the source folder with:

```text
python -m pytest -q -p no:cacheprovider
```

Result: **108 passed, 5 failed** in 1100.13 seconds. Two failures were Tk root
creation failures caused by the current Anaconda Tcl/Tk installation
(`tcl_findLibrary`/missing `menu.tcl`). Two formatter failures expect the
internal ID `sl2_spin1`, while the implementation emits its user-facing Chinese
name. One Jones debug test expects no reference expression although the current
reference catalog supplies `t + t**3 - t**4`. The recovered implementation was
not changed. Its smoke tests were subsequently aligned with the observed
display-name/reference behavior, and Tk-dependent assertions now skip only when
a Tk root cannot be created in the execution environment.

The merged repository collects 139 tests. The pre-existing archive baseline was
run separately and passes: **26 passed**. A broader recovery-focused selection
covering that baseline, `tests/benchmark_lab`, registry, and profile-runner
smokes passes: **45 passed**.

All 135 in-scope authoritative files were compared with the repository after
normalizing only CRLF/LF; no file was missing or content-different.

The recovered benchmark profile command completed for q=2, q=3, and q=5.
Each regenerated `pair_level_results.json` is equal as a parsed JSON object to
the corresponding archived JSON. In all three modes P03
reproduces `(0,1,1)`, P01 reproduces `(0,1,0)`, P02 and P04 reproduce
`(1,1,1)`, and P05 is skipped. The symbolic P01 and P03 audits also completed;
each regenerated audit JSON is equal as a parsed JSON object to its archived
counterpart. P03 reproduces `same/different/different`, including the exact
stored symbolic differences.
