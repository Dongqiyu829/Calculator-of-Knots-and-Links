# Benchmark Lab

## 目的

这个目录树是一套完全平行的新实验程序。它的目标不是改动现有主线，也不是接管旧 GUI / workbench，而是在不修改旧程序的前提下，把现有三条 branch 组织成一个独立的 benchmark/profile/audit 实验平台。

这套 lab 只做一件事：

- import 现有 branch evaluator
- 读取 benchmark 模板
- 运行 pairwise profile 实验
- 生成 summary
- 对关键 pair 做详细 audit

## 平行目录树

- `src/benchmark_lab/`
- `examples/benchmark_lab/`
- `data/benchmark_lab/`
- `docs/benchmark_lab/`
- `tests/benchmark_lab/`
- `artifacts/benchmark_lab/`

## 不变原则

- 不修改 legacy_fast
- 不修改原 GUI
- 不修改原 workbench
- 不修改 branch 数学逻辑
- benchmark metadata 只是理论预期，不是程序真理
- mismatch 必须显式暴露，不允许偷偷调 expected profile 掩盖

## 入口

- profile 实验：`examples/benchmark_lab/run_benchmark_profiles.py`
- 单 pair audit：`examples/benchmark_lab/run_benchmark_audit.py`
