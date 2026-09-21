# Report Appendix

## Project information

- Title: Quantum Groups, Yang-Baxter Equations, and Braid-Based Knot Invariants
- Author: Dong Qiyu
- Student ID: 21048043
- Department: Mathematics
- Supervisor: Ivan Ip

## Purpose of this appendix

This appendix records the repository snapshot used for the UROP report, the main benchmark_lab entry points, the current benchmark template, and the benchmark results that are most relevant to the report discussion.

## Repository folders used in the report

- `src/benchmark_lab/`: isolated benchmark/profile/audit implementation.
- `examples/benchmark_lab/`: command-line entry scripts for profile and audit runs.
- `data/benchmark_lab/benchmark_pairs_template.csv`: main benchmark template used in the report.
- `docs/benchmark_summary.md`: plain-language summary of the current benchmark interpretation.
- `docs/reproducibility.md`: environment and command guide.
- `artifacts/benchmark_lab/`: exported benchmark results, when present in the snapshot.

## Main scripts used in the report

- `python examples/benchmark_lab/run_benchmark_profiles.py --input data/benchmark_lab/benchmark_pairs_template.csv --q 2`
- `python examples/benchmark_lab/run_benchmark_profiles.py --input data/benchmark_lab/benchmark_pairs_template.csv --q 3`
- `python examples/benchmark_lab/run_benchmark_profiles.py --input data/benchmark_lab/benchmark_pairs_template.csv --q 5`
- `python examples/benchmark_lab/run_benchmark_profiles.py --input data/benchmark_lab/benchmark_pairs_template.csv --q q`
- `python examples/benchmark_lab/run_benchmark_audit.py --input data/benchmark_lab/benchmark_pairs_template.csv --pair P01 --q 2`
- `python examples/benchmark_lab/run_benchmark_audit.py --input data/benchmark_lab/benchmark_pairs_template.csv --pair P04 --q 2`
- `python examples/benchmark_lab/run_benchmark_audit.py --input data/benchmark_lab/benchmark_pairs_template.csv --pair P03 --q q`
- `python tools/create_report_bundle.py`

## Current benchmark focus

The main benchmark pair used in the report is `P03 = 10_22 vs 10_35`. The current stored runs show the observed profile `(0,1,1)` in the numeric cases `q=2`, `q=3`, and `q=5`. The symbolic `q=q` audit for `P03` also shows the same branch-wise pattern: `sl2_fundamental` stays equal, while `sl2_3d_9x9` and `sl3_fundamental` differ.

## Current audit cases

- `P01 = 5_1 vs 5_1_stabilized`: stabilization audit case.
- `P04 = 5_1 vs 10_132`: literature/convention reconciliation audit case.

These cases are included because they expose interpretation and normalization questions that should remain visible in the report.

## Reproducibility commands

See `docs/reproducibility.md` for the full environment notes. The short command list is:

```bash
python examples/benchmark_lab/run_benchmark_profiles.py --input data/benchmark_lab/benchmark_pairs_template.csv --q 2
python examples/benchmark_lab/run_benchmark_profiles.py --input data/benchmark_lab/benchmark_pairs_template.csv --q 3
python examples/benchmark_lab/run_benchmark_profiles.py --input data/benchmark_lab/benchmark_pairs_template.csv --q 5
python examples/benchmark_lab/run_benchmark_profiles.py --input data/benchmark_lab/benchmark_pairs_template.csv --q q
python examples/benchmark_lab/run_benchmark_audit.py --input data/benchmark_lab/benchmark_pairs_template.csv --pair P01 --q 2
python examples/benchmark_lab/run_benchmark_audit.py --input data/benchmark_lab/benchmark_pairs_template.csv --pair P04 --q 2
```

python examples/benchmark_lab/run_benchmark_audit.py --input data/benchmark_lab/benchmark_pairs_template.csv --pair P03 --q q
python tools/create_report_bundle.py
```

## Release placeholders

- GitHub repository URL: [fill before release]
- Commit hash: [fill before release if the snapshot is stored in git]
- Release tag: [fill before release]