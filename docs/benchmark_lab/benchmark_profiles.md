# Benchmark Profiles

## 1. 这套 profile 实验做什么

benchmark lab 会把三条现有 branch 固定成一个 profile 向量：

- `sl2_fundamental`
- `sl2_3d_9x9`
- `sl3_fundamental`

对每个 pair，lab 只负责：

- 读取 A/B 两侧 braid 数据
- 调用旧程序里的 branch evaluator
- 比较 same / different
- 生成 observed profile
- 对照 expected profile
- 输出 mismatch 或 skipped

## 2. profile 规则

固定顺序：

`(sl2_fundamental, sl2_3d_9x9, sl3_fundamental)`

固定编码：

- `same -> 0`
- `different -> 1`

因此：

- `(0,0,0)` 表示三条 branch 都没有把 pair 分开
- `(1,1,1)` 表示三条 branch 都把 pair 分开
- `(0,1,1)` 表示 `sl2_fundamental` 没分开，但两条 9x9 线分开了

placeholder / needs_audit pair 不会伪造 profile，而是标成 `skipped`。

## 3. 模板字段

模板字段与旧 benchmark 语义相同，但都放在新 lab 的数据目录里：

- `pair_id`
- `group`
- `label_A`, `label_B`
- `source_A`, `source_B`
- `num_strands_A`, `generators_A`
- `num_strands_B`, `generators_B`
- `same_jones`
- `same_alexander_or_conway`
- `mutant`
- `status_of_braid_source`
- `expected_sl2_fundamental`
- `expected_sl2_3d_9x9`
- `expected_sl3_fundamental`
- `expected_profile`
- `priority`
- `notes`

## 4. 当前核心 5 对

- `P01`: `5_1` vs `5_1_stabilized`
- `P02`: `5_1` vs `10_22`
- `P03`: `10_22` vs `10_35`
- `P04`: `5_1` vs `10_132`
- `P05`: `K11n34` vs `K11n42` placeholder

其中 `P01` 和 `P04` 是当前最重要的 audit cases。

## 5. 运行方式

```bash
python examples/benchmark_lab/run_benchmark_profiles.py --input data/benchmark_lab/benchmark_pairs_template.csv --q 2
python examples/benchmark_lab/run_benchmark_profiles.py --input data/benchmark_lab/benchmark_pairs_template.csv --q 3
python examples/benchmark_lab/run_benchmark_profiles.py --input data/benchmark_lab/benchmark_pairs_template.csv --q 5
python examples/benchmark_lab/run_benchmark_profiles.py --input data/benchmark_lab/benchmark_pairs_template.csv --q q
```

也可以把输入换成 JSON：

```bash
python examples/benchmark_lab/run_benchmark_profiles.py --input data/benchmark_lab/benchmark_pairs_template.json --q 2
```

## 6. 输出目录

所有 profile 结果都写到：

- `artifacts/benchmark_lab/benchmark_pairs_template_q_2/`
- `artifacts/benchmark_lab/benchmark_pairs_template_q_3/`
- `artifacts/benchmark_lab/benchmark_pairs_template_q_5/`
- `artifacts/benchmark_lab/benchmark_pairs_template_q_q/`

每次运行至少导出：

- `pair_level_results.csv`
- `pair_level_results.json`
- `summary.csv`
- `summary.json`
- `summary.md`

## 7. mismatch 的处理原则

如果 expected profile 与程序观测不一致：

- 不改 branch
- 不改旧程序
- 不偷偷调 expected profile 掩盖问题
- 直接输出：
  - observed profile
  - expected profile
  - `match_expected = no`
