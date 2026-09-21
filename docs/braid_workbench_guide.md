# Braid Workbench Guide

## 1. 这是什么

examples/braid_workbench_gui.py 是当前 ordinary/mainline 上的独立 braid workbench。它不是 legacy_fast 的替代品，也不是新的数学主线；它的目标是把当前普通版本上的三条分支、比较层、结果表、experiment log 和结构化导出整合成一个更适合研究工作流的入口。

这次 workbench 的关键升级是：

- 输入接口分成 Manual input 和 JSON input 两套前端
- 但两边都进入同一个 unified spec / runner / comparison / export 流程
- 所以是输入分立，功能不分裂

## 2. 如何启动

在项目根目录运行：

```bash
C:/Users/dongqiyu/anaconda3/python.exe examples/braid_workbench_gui.py
```

如果只想在命令行里快速做一次内置 pair comparison，也可以运行：

```bash
C:/Users/dongqiyu/anaconda3/python.exe examples/braid_workbench_gui.py --compare trefoil figure_eight --q 2
```

## 3. 界面结构

当前 ordinary braid workbench 分成四个页签：

- Manual input
- JSON input
- Results
- Experiment log

### Manual input

适合人手工构造 braid 集合。你可以：

- 新建 braid 条目
- 复制 braid 条目
- 删除 braid 条目
- 修改 label
- 修改 num_strands
- 手写 generators
- 用 +σ_i / -σ_i 按钮追加 generators
- Undo / Clear
- 写 notes
- 看每个 braid 的 preview
- 设置 q parameter
- 选择 models
- 选择 comparison_mode
- 运行整个 batch

### JSON input

适合把 AI 或程序输出的 braid 批量导入。你可以：

- 粘贴 JSON
- Validate JSON
- Load braids
- Run JSON batch
- Clear JSON
- Copy AI JSON template
- 查看 schema 说明和当前载入 batch 的结构化摘要

### Results

无论输入来自 Manual 还是 JSON，结果都统一显示为三张表：

- single braid result table
- pairwise comparison table
- summary table

你也可以从这里：

- 导出当前表为 CSV
- 导出当前表为 JSON
- 复制当前表为 markdown table
- 导出完整 result bundle JSON
- 把当前 pairwise rows 加入 experiment log

### Experiment log

无论 pairwise rows 来自 Manual run 还是 JSON run，都统一加入同一个 log，并保留 input_source 字段。你可以：

- 查看记录
- 按 label 筛选
- 按 classification 筛选
- 按 input_source = manual/json 筛选
- 按 Jones / sl2 3D / sl3 的 same or different 状态筛选
- 导出 CSV / JSON / markdown table

## 4. Manual input 怎么用

### 4.1 新建一组 braids

进入 Manual input 页签后：

1. 在顶部设置 q parameter。
2. 选择 comparison_mode。
3. 勾选要参与当前 run 的 models。
4. 用 Add braid 增加一个 braid 卡片。
5. 每张卡片里填写 label、num_strands、generators、notes。
6. 需要时可点 Duplicate 复制一张已有卡片。
7. 点 Run manual batch 运行整组 braids。

### 4.2 图形化构造 generators

每张 manual braid 卡片都支持：

- 手写 generator 序列，例如 1 2 1 或 1 -2 1 -2
- 点击 +σ_i / -σ_i 追加 generator
- Undo 撤回最后一个 generator
- Clear 清空 generators
- 实时刷新 braid preview

输入约定：

- 1 表示 σ1
- -1 表示 σ1^-1
- 2 表示 σ2
- -2 表示 σ2^-1

### 4.3 q parameter 怎么选

Manual input 顶部直接写清楚了当前口径：

- q = q：符号模式，输出多项式，较慢，适合正式确认
- q = 2 或其他数字：数值模式，输出代值后的数，较快，适合快速筛查

## 5. JSON input 怎么用

### 5.1 固定 schema

当前 JSON input 使用固定 schema：

```json
{
  "q_parameter": "q",
  "models": [
    "sl2_fundamental",
    "sl2_3d_9x9",
    "sl3_fundamental"
  ],
  "comparison_mode": "pairwise",
  "braids": [
    {
      "label": "A",
      "num_strands": 3,
      "generators": [1, 2, 1],
      "notes": "optional"
    },
    {
      "label": "B",
      "num_strands": 3,
      "generators": [2, 1, 2],
      "notes": "optional"
    }
  ]
}
```

### 5.2 校验规则

当前 JSON 校验是严格的，不会静默失败：

- q_parameter 只能是 q、可解析数字的字符串、或数值型 2/3/...
- models 只能是 sl2_fundamental、sl2_3d_9x9、sl3_fundamental
- comparison_mode 只能是 single、pairwise、all
- 每个 braid 必须有 label、num_strands、generators
- num_strands 必须是整数且 >= 2
- generators 必须是整数数组，且只能落在 ±1 到 ±(n-1)

### 5.3 推荐使用流程

1. 把 JSON 粘到文本框。
2. 先点 Validate JSON。
3. 再点 Load braids，确认当前 batch 摘要是否正确。
4. 最后点 Run JSON batch。
5. 到 Results 页签查看三张统一结果表。

## 6. comparison_mode 怎么理解

当前 workbench 两种输入方式都支持同样的 comparison_mode：

- single：对每个 braid 单独计算，不做 braid 间比较
- pairwise：对所有 braid 做两两比较
- all：先给 single braid result table，再给 pairwise comparison table，再给 summary table

例子：如果 braids 是 A、B、C，那么 pairwise 会比较：

- A vs B
- A vs C
- B vs C

## 7. models 怎么理解

当前 workbench 两种输入方式都支持同样的三种 model id：

- sl2_fundamental -> Jones / sl2 fundamental -> formal Jones-compatible branch
- sl2_3d_9x9 -> sl2 的3维表示下的9x9矩阵 -> colored Jones candidate branch；当前对照 Knot Atlas n=2，已确认 `3_1` 的 `q^6 J_2(3_1; q^2)` calibration，`5_2` 仍在 verification，不是 theorem-level 最终结论
- sl3_fundamental -> sl3 fundamental -> formal sl3 branch

Manual input 用勾选框设置 models，JSON input 用 models 数组设置 models。两边最终都进入同一个 ComparisonRunSpec。

如果你在 workbench 里查看 `sl2_3d_9x9` 这条线，请始终按同一个口径理解：Knot Atlas 把 `J_n` 用在 `(n+1)` 维 `sl2` 表示上，所以当前 3 维分支对照的是 Knot Atlas `n=2`；当前 `3_1` 与 `5_1` 已有直接 q-shift correspondence，`5_2` 仍只写作 under verification。

## 8. 输出结果怎么读

Results 页签统一显示三张表。

### 表 1：single braid result table

字段至少包括：

- label
- num_strands
- generators
- sl2_fundamental_output
- sl2_3d_9x9_output
- sl3_fundamental_output

这张表回答的是：每个 braid 自己在三条主分支上的输出分别是什么。

### 表 2：pairwise comparison table

字段至少包括：

- pair_label
- braid_a
- braid_b
- sl2_fundamental_same
- sl2_3d_9x9_same
- sl3_fundamental_same
- classification

这张表回答的是：任意两条 braid 在当前分支上是否给出相同结果，以及当前 classification 是什么。

### 表 3：summary table

字段至少包括：

- classification
- count

这张表回答的是：本次 pairwise run 里每一种 classification 出现了多少次。

## 9. classification 怎么读

当前 workbench 继续沿用已有 classification 体系，在默认三模型口径下兼容这些标签：

- both_distinguish
- neither_distinguishes
- only_sl2_3d_distinguishes
- only_sl3_distinguishes
- jones_same_sl3_diff
- jones_same_sl2_3d_diff
- all_same
- all_different

如果本次 run 只勾选了模型子集，workbench 会保留统一 pairwise table 结构，并使用向后兼容的补充标签表示“当前选中模型全同 / 全异 / 混合”。

## 10. experiment log 怎么用

当前 experiment log 记录的是 pairwise rows，不区分输入前端。也就是说：

- Manual input 产生的 pairwise rows 可以加入 log
- JSON input 产生的 pairwise rows 也可以加入 log

并且每条记录都明确包含：

- input_source = manual 或 json
- braid A / braid B 的 strands 与 generators
- 三个输出列
- 三个 same/different 列
- classification
- notes
- timestamp
- record_id

所以你后面筛数据时，可以直接按 input_source 区分“这是我手工构造的 batch”还是“这是 AI / 程序导入的 batch”。

## 11. 导出怎么用

当前 ordinary workbench 的导出分两层：

### Results 页签导出

针对当前 run 的统一结果表：

- Export current table CSV
- Export current table JSON
- Copy current table markdown
- Export full result bundle JSON

### Experiment log 页签导出

针对当前筛选后的 log records：

- Export CSV
- Export JSON
- Copy markdown table

这两层导出的目标不同，但都保持统一结构，不再按 Manual/JSON 分叉。

## 12. 推荐使用流程

如果你的目标是做一轮普通版本上的系统实验，推荐顺序是：

1. 如果你想手工构造 braid 集合，进入 Manual input。
2. 如果你想从 AI / 程序粘贴 batch，进入 JSON input。
3. 设定 q parameter、models、comparison_mode。
4. 运行 batch。
5. 在 Results 中查看三张统一结果表。
6. 如果 pairwise rows 值得保存，把它们加入 Experiment log。
7. 在 Experiment log 里按 classification / input_source 做筛选。
8. 导出 CSV / JSON / markdown table，或导出完整 result bundle JSON。
