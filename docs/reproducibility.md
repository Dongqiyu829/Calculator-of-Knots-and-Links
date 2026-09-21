# Reproducibility

## Environment

- Operating system used during development: Windows.
- Python used in the current workspace: Python 3.12.4.
- Core external package used by the benchmark layer: `sympy`.
- Standard-library modules used by the benchmark_lab CLIs include `argparse`, `csv`, `json`, `pathlib`, and `tkinter` is only needed for GUI entry points, not for benchmark_lab.

## Setup

Create or activate a Python environment, then install the main symbolic dependency:

```bash
pip install sympy
```

If you want to run the smoke tests for the isolated benchmark_lab layer, also install:

```bash
pip install pytest
```

## Main benchmark commands

Run the main profile template in numeric modes:

```bash
python examples/benchmark_lab/run_benchmark_profiles.py --input data/benchmark_lab/benchmark_pairs_template.csv --q 2
python examples/benchmark_lab/run_benchmark_profiles.py --input data/benchmark_lab/benchmark_pairs_template.csv --q 3
python examples/benchmark_lab/run_benchmark_profiles.py --input data/benchmark_lab/benchmark_pairs_template.csv --q 5
```

Run the symbolic profile mode:

```bash
python examples/benchmark_lab/run_benchmark_profiles.py --input data/benchmark_lab/benchmark_pairs_template.csv --q q
```

Run the two main audit cases:

```bash
python examples/benchmark_lab/run_benchmark_audit.py --input data/benchmark_lab/benchmark_pairs_template.csv --pair P01 --q 2
python examples/benchmark_lab/run_benchmark_audit.py --input data/benchmark_lab/benchmark_pairs_template.csv --pair P04 --q 2
```

## Output locations

Profile outputs are written under:

- `artifacts/benchmark_lab/benchmark_pairs_template_q_2/`
- `artifacts/benchmark_lab/benchmark_pairs_template_q_3/`
- `artifacts/benchmark_lab/benchmark_pairs_template_q_5/`
- `artifacts/benchmark_lab/benchmark_pairs_template_q_q/`

Each profile run writes:

- `pair_level_results.csv`
- `pair_level_results.json`
- `summary.csv`
- `summary.json`
- `summary.md`

Audit outputs are written into the same `artifacts/benchmark_lab/...` directories as `audit_<pair>_q_<mode>.md` and `audit_<pair>_q_<mode>.json`.

## How to verify the main benchmark claim

The main report claim is about `P03 = 10_22 vs 10_35`.

To verify it:

1. Run the profile command for `q=2`, `q=3`, and `q=5`.
2. Open `pair_level_results.csv` in each output directory.
3. Find the row with `pair_id = P03`.
4. Check that `observed_profile` is `(0,1,1)`.
5. For symbolic confirmation, run the `q=q` profile or inspect the symbolic audit for `P03` in `artifacts/benchmark_lab/benchmark_pairs_template_q_q/`.

The intended interpretation is: `sl2_fundamental` does not separate the pair, while both `sl2_3d_9x9` and `sl3_fundamental` do separate it.

## Optional test command

```bash
python -m pytest tests/benchmark_lab
```

## Notes

- `P01` and `P04` should be treated as audit cases, not as final benchmark conclusions.
- `P05` is intentionally skipped until its braid source is audited.
- benchmark metadata is preserved as metadata; the runner does not rewrite observed outputs to match expectations.# Reproducibility

## Environment

- Operating system used during development: Windows
- Python version used in the current local environment: 3.12.4
- Main external package required for benchmark_lab: `sympy`

The benchmark_lab commands do not require the GUI. They run from the command line and import the current branch evaluators from the main codebase.

## Setup

From the repository root, install the main dependency with:

```bash
pip install sympy
```

If you use a virtual environment or Conda environment, activate it first.

## Benchmark Commands

Run the profile experiments:

```bash
python examples/benchmark_lab/run_benchmark_profiles.py --input data/benchmark_lab/benchmark_pairs_template.csv --q 2
python examples/benchmark_lab/run_benchmark_profiles.py --input data/benchmark_lab/benchmark_pairs_template.csv --q 3
python examples/benchmark_lab/run_benchmark_profiles.py --input data/benchmark_lab/benchmark_pairs_template.csv --q 5
python examples/benchmark_lab/run_benchmark_profiles.py --input data/benchmark_lab/benchmark_pairs_template.csv --q q
```

Run focused audits:

```bash
python examples/benchmark_lab/run_benchmark_audit.py --input data/benchmark_lab/benchmark_pairs_template.csv --pair P01 --q 2
python examples/benchmark_lab/run_benchmark_audit.py --input data/benchmark_lab/benchmark_pairs_template.csv --pair P04 --q 2
python examples/benchmark_lab/run_benchmark_audit.py --input data/benchmark_lab/benchmark_pairs_template.csv --pair P03 --q q
```

## Output Locations

Profile outputs appear in folders such as:

- `artifacts/benchmark_lab/benchmark_pairs_template_q_2/`
- `artifacts/benchmark_lab/benchmark_pairs_template_q_3/`
- `artifacts/benchmark_lab/benchmark_pairs_template_q_5/`
- `artifacts/benchmark_lab/benchmark_pairs_template_q_q/`

Each completed profile run writes:

- `pair_level_results.csv`
- `pair_level_results.json`
- `summary.csv`
- `summary.json`
- `summary.md`

Each audit run writes files such as:

- `audit_P01_q_2.md`
- `audit_P04_q_2.md`
- `audit_P03_q_q.md`

## How To Verify P03

After running the profile command, open `pair_level_results.csv` in the corresponding artifact folder and check the row with `pair_id = P03`.

The current report-ready claim is:

- `sl2_fundamental_relation = same`
- `sl2_3d_relation = different`
- `sl3_fundamental_relation = different`
- `observed_profile = (0,1,1)`

For symbolic inspection, run the `P03` audit at `q = q` and review the symbolic differences recorded in `audit_P03_q_q.md`.

## Packaging A Snapshot

To prepare a report submission bundle, run:

```bash
python tools/create_report_bundle.py
```

This creates `report_bundle/`, writes `VERSION.txt`, and packs the same snapshot into `report_bundle.zip`.