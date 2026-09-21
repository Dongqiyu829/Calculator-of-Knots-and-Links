# Benchmark Audit

## 1. audit 做什么

benchmark audit 是对单个 pair 的细粒度检查，不是 profile summary 的替代品。

它会输出：

- braid A / B 的基本信息
- strand count
- generators
- writhe
- 三条 branch 的输出
- same / different 判断过程
- 符号模式下的 simplified difference
- 数值模式下的 numeric witness

## 2. 重点 pair

当前应优先 audit：

- `P01 = 5_1 vs 5_1_stabilized`
- `P04 = 5_1 vs 10_132`

因为这两对最适合检查“同 knot 的稳定性问题”和“当前负例 blind-spot 是否真实存在”。

## 3. 运行方式

```bash
python examples/benchmark_lab/run_benchmark_audit.py --input data/benchmark_lab/benchmark_pairs_template.csv --pair P01 --q 2
python examples/benchmark_lab/run_benchmark_audit.py --input data/benchmark_lab/benchmark_pairs_template.csv --pair P04 --q 2
python examples/benchmark_lab/run_benchmark_audit.py --input data/benchmark_lab/benchmark_pairs_template.csv --pair P01 --q q
```

## 4. 输出文件

audit 结果写到 profile 运行同一层级目录下，例如：

- `artifacts/benchmark_lab/benchmark_pairs_template_q_2/audit_P01_q_2.md`
- `artifacts/benchmark_lab/benchmark_pairs_template_q_2/audit_P01_q_2.json`

## 5. `needs_audit` pair 的语义

如果 pair 本身已经是 `status_of_braid_source=needs_audit`：

- audit 不会假装继续算
- 会明确标成 skipped
- 会保留 warnings

这也是 benchmark lab 的目标之一：把未审计输入和真正的程序行为清楚分开。
