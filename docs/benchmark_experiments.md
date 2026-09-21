# Benchmark Experiments

## 1. 为什么要有 benchmark layer

当前主线已经有三条可运行 branch：

- `sl2_fundamental`
- `sl2_3d_9x9`
- `sl3_fundamental`

但如果要系统研究 separation profiles，仅靠零散 demo 不够。benchmark experiment layer 的目标是把“固定 pair 元数据、固定 braid 输入、固定 q 模式、固定 profile 规则、固定导出格式”放到一个可复现外层里，而不去改 branch 的数学逻辑本身。

这层是 benchmark metadata + runner + summary/export，不是新的不变量定义层。

## 2. separation profile 是什么

这里固定三条 branch 的顺序为：

`(sl2_fundamental, sl2_3d_9x9, sl3_fundamental)`

并固定编码规则：

- `same -> 0`
- `different -> 1`

因此：

- `same, same, same -> (0,0,0)`
- `different, different, different -> (1,1,1)`
- `same, different, different -> (0,1,1)`

如果 pair 没法安全计算，例如 braid source 还没 audit，runner 会把该 pair 标成 `skipped`，而不是伪造 profile。

## 3. 模板字段说明

CSV 模板和 JSON 模板表达的是同一组字段：

- `pair_id`: benchmark 对的稳定编号
- `group`: benchmark 分组，例如 control / main_positive_benchmark
- `label_A`, `label_B`: pair 两侧标签
- `source_A`, `source_B`: braid 来源说明
- `num_strands_A`, `num_strands_B`: strands 数
- `generators_A`, `generators_B`: Artin generator 列表
- `same_jones`: 理论元数据，表示 pair 是否已知 Jones 相同
- `same_alexander_or_conway`: 理论元数据，表示 pair 是否已知 Alexander/Conway 相同
- `mutant`: 理论元数据，表示 pair 是否作为 mutant 相关案例
- `status_of_braid_source`: `safe` 或 `needs_audit`
- `expected_sl2_fundamental`, `expected_sl2_3d_9x9`, `expected_sl3_fundamental`: 理论预期，不是程序真理
- `expected_profile`: 理论预期 profile
- `priority`: 当前实验优先级
- `notes`: 说明文字

## 4. 当前核心 5 对的用途

- `P01`: control。用 `5_1` 和一个稳定化 presentation 检查“同 knot 不应被错误分开”。
- `P02`: easy different control。用 `5_1` vs `10_22` 检查“明显不同的 pair 应该被全部分开”。
- `P03`: main positive benchmark。目标 profile 是 `(0,1,1)`，用于观察 `sl2_fundamental` 与两个 9x9 branch 的 separation gap。
- `P04`: main negative benchmark。理论元数据预期它可能是当前三 branch 的共同 blind spot。
- `P05`: mutation blind-spot placeholder。先把 pair 留在 benchmark registry 中，但 braid source 还没 audit，所以当前必须 warning + skipped。

## 5. 为什么 `K11n34 / K11n42` 先只做 placeholder

这对是 mutation blind-spot placeholder。当前项目里还没有最后固定、可直接用于主线 Artin-generator 约定的 braid source，因此不能装作已经可以安全计算。

benchmark layer 的处理规则是：

- 保留在模板里
- 保留在 summary 里
- 明确标成 `needs_audit`
- runner 必须 warning
- runner 必须跳过实际计算

这比悄悄吞掉、更改 pair，或者用未审计 braid 硬跑，要诚实得多。

## 6. same / different 的比较规则

### 数值模式

如果 `q_parameter` 是 `2`、`3`、`5` 等数值：

- 对输出做 `sympy.simplify`
- 再做严格相等比较

### 符号模式

如果 `q_parameter == "q"`：

- 对两个输出做 `sympy.simplify`
- 比较差是否为 `0`

这里不做字符串级比较。

## 7. 运行方法

当前 CLI 入口是：

```bash
python examples/run_benchmark_experiments.py --input data/benchmark_pairs_template.csv --q 2
python examples/run_benchmark_experiments.py --input data/benchmark_pairs_template.csv --q 3
python examples/run_benchmark_experiments.py --input data/benchmark_pairs_template.csv --q 5
python examples/run_benchmark_experiments.py --input data/benchmark_pairs_template.csv --q q
```

也可以把 `--input` 换成 JSON 模板：

```bash
python examples/run_benchmark_experiments.py --input data/benchmark_pairs_template.json --q 2
```

CLI 会输出：

- pair-level result table
- summary table
- 导出文件路径

默认导出目录是：

`artifacts/benchmark_experiments/<input_name>_q_<mode>/`

## 8. 导出格式

pair-level CSV 会固定输出：

- `pair_id`
- `q_mode`
- `sl2_fundamental_A`
- `sl2_fundamental_B`
- `sl2_fundamental_relation`
- `sl2_3d_A`
- `sl2_3d_B`
- `sl2_3d_relation`
- `sl3_fundamental_A`
- `sl3_fundamental_B`
- `sl3_fundamental_relation`
- `observed_profile`
- `match_expected`
- `notes`

summary 会导出 CSV / JSON / markdown，至少统计：

- `(0,0,0)`
- `(1,1,1)`
- `(0,1,1)`
- `(0,0,1)`
- `(0,1,0)`
- `skipped`
- `match_expected = yes/no/partial`

## 9. `needs_audit` 的含义

`needs_audit` 表示：

- 当前 pair 的 braid source 还没有被当前项目主线约定最终审计通过
- benchmark 元数据可以先存在
- 但 runner 不能把它当成 safe pair 去跑

因此，`needs_audit` 不会静默失败，也不会被自动补成猜测 braid；它会被明确 warning，并保留在 summary 中作为 skipped pair。
