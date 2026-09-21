# Current Summary and Guide

## 1. Abstract

这个项目是一个基于量子群 / R-matrix 思路的扭结不变量计算系统原型，当前重点是把局部编织数据、全局 braid operator、raw trace、EYB-normalized output 和验证层清楚地分开并逐步固化。现在已经支持 `sl2 fundamental`、`sl2 spin1`、`sl3 fundamental` 三个核心表示对象，并能完成对应的局部 braiding / projector 数据、braid word 输入、全局 braid operator、raw closure trace，以及 A-type fundamental 分支上的 EYB-normalized 输出。当前项目中的正式工作规范是 braid-side EYB normalization：它已经在 `sl2/sl3 fundamental` 上通过了 conjugation / stabilization regression。与此同时，raw-side 理论并没有被假装“已经完全闭合”，它目前被保留为独立的 convention audit 层。当前还提供了一个简单的 demo launcher GUI 用于统一浏览和运行 examples，但任意 knot diagram 输入、以及更一般的 RT normalization 仍然不在当前正式功能范围内。

当前 `sl2 fundamental` 还额外形成了一条正式的 reduced P2 / Jones-compatible output layer。当前默认比较 convention 使用 `t = q^-2`。

与此同时，当前系统已经开始形成一个多分支拓扑不变量程序结构：`sl2 fundamental` 是 formal 的 Jones-compatible branch，`sl3 fundamental` 是 formal 的 P3-type EYB branch，而“`sl2 的3维表示下的9x9矩阵`”（内部仍兼容 `sl2_spin1`）已经从 exploratory 的 projector-aware raw branch 升级为 colored Jones candidate branch。

当前 `sl2` 三维 `9x9` 分支已经明确区分 raw trace、quantum trace before normalization、unreduced candidate output、unknot normalization 与 reduced candidate output，并通过统一 registry / formatter / benchmark / GUI 对外暴露，不再只是 raw trace-only 分支。

当前这条 `sl2` 三维 `9x9` 线还已经补上了明确的 Knot Atlas 对照口径：Knot Atlas 把 `J_n` 用在 `(n+1)` 维 `sl2` 表示上，因此当前程序把这条 3 维分支和 Knot Atlas 的 `n=2` colored Jones 数据对照。当前已经确认 `3_1` 满足 `reduced candidate output = q^6 J_2(3_1; q^2)`，也已经直接确认 `5_1` 满足 `reduced candidate output = q^10 J_2(5_1; q^2)`；`5_2` 已进入 verification set，但当前项目里的 braid representative 还没有最后固定，所以仍只写作 under verification。这里刻意只声明“current calibrated correspondence”，不把它包装成 theorem-level 的最终 colored Jones normalization 结论。

当前系统也已经有统一的多分支结果对象和统一的报告输出层，便于未来让 CLI / GUI / 文档共用同一套展示逻辑；`examples/demo_launcher_gui.py` 现在还能在现有 skeleton 上切换 formatter/raw 视图，并支持内置 example 与自定义 braid 输入。

当前 GUI 的 braid preview 也已经从主窗口逻辑中拆成独立 renderer 模块，至少在 strand endpoint、over/under crossing 显示、generator label 对齐，以及较长 braid 的横向留白/滚动方面做了整理，避免 GUI 主文件继续堆积绘图细节。

当前普通版本还已经形成一个独立的 braid workbench GUI：它现在明确把输入接口分成 `Manual input` 与 `JSON input` 两套前端，但两边都统一进入同一个内部数据层、同一个 comparison runner、同一个结果表结构、同一个 experiment log 和同一个导出流程。也就是说，输入接口分立，但功能不分裂：manual 与 JSON 都支持 single / pairwise / all、q parameter、models、结果表、以及 CSV / JSON / markdown 导出。这个 workbench 是当前主开发线上的研究工具入口；`legacy_fast` 仍然只保留为稳定保底路径。

当前项目还明确区分两条程序线：普通版本是主开发版本，新的 candidate branch、comparison benchmark、GUI 行为修复与 preview renderer 改进都优先在普通版本推进；`legacy_fast` 仅作为稳定保底与回退参考，不再承担主开发目标。

## 2. Current Scope

### 当前已经支持

- `sl2 fundamental`
- `sl2 spin1`
- `sl3 fundamental`
- local braiding / projector data
- braid word input
- global braid operator
- raw closure trace
- A-type fundamental 的 EYB-normalized output
- `sl2 fundamental` 的 reduced P2 / Jones-compatible output layer
- 多分支 invariant program skeleton（`sl2 fundamental` / `sl3 fundamental` / `sl2 spin1`）
- simple demo launcher GUI
- independent braid workbench GUI
- separated Manual input / JSON input frontends over one shared workbench spec and runner
- benchmark catalog
- conjugation / stabilization regression
- convention audit
- pair comparison across the three main branches
- experiment log with CSV / JSON / markdown export
- presentation-friendly braid preview mode

### 当前还不支持 / 暂不作为正式功能

- 完整数学交互 GUI / diagram editor
- 任意 knot diagram 图形输入
- generalized RT normalization for all reps
- `sl2` 的三维表示下 `9x9` 分支的 theorem-level colored Jones 命名
- 新的 Lie algebra families

换句话说，这个项目现在已经是一个可运行、可验证、可对比的计算原型，但它还不是一个“任意输入、任意表示、任意归一化都已经统一完成”的完整平台。

## Quick Start in 5 Demos

如果你是第一次打开这个项目，建议不要先看完整 demo 列表，而是先跑下面 5 个最关键的入口：

1. `examples/representation_summary_demo.py`：先确认当前项目到底支持哪些表示对象。
2. `examples/sl2_fundamental_rmatrix_demo.py`：看最简单的局部两股 braiding 模型长什么样。
3. `examples/braid_operator_demo.py`：看 braid word 怎样被装配成全局 braid operator。
4. `examples/benchmark_P2_demo.py`：看当前系统如何批量跑一组标准小例子。
5. `examples/convention_audit_demo.py`：看当前项目正式采用哪一层规范，以及 raw-side audit 与 braid-side convention 的关系。

如果你更想用图形界面统一浏览这些 demo，也可以直接启动：`examples/demo_launcher_gui.py`。

如果你当前关心这条 `sl2` 三维 candidate branch 与 Knot Atlas 的对应关系，最直接的入口是：`examples/check_sl2_3d_knot_atlas_correspondence.py`。

如果你想把当前普通版本当成实验工作台来使用，而不是只看 demo，那么更推荐直接启动：`examples/braid_workbench_gui.py`。当前 workbench 的推荐理解方式是：

- `Manual input`：面向人手工构造 braid batch，支持图形化 builder、preview、label/notes 编辑。
- `JSON input`：面向 AI 或程序批量导入 braid batch，使用固定 schema 做严格校验。
- `Results`：无论输入来源如何，统一显示 single braid result table、pairwise comparison table、summary table。
- `Experiment log`：无论输入来源如何，统一记录 pairwise rows，并保留 `input_source = manual/json`。

## 3. Quick Start

这一节是最推荐的上手入口。如果你是第一次接触这个项目，建议先直接运行几个 demo，看系统目前能算什么、输出什么。

### 环境

- Python: 当前开发与验证环境是 Python 3.12.4
- 主要依赖: `sympy`
- 建议在项目根目录运行示例脚本

当前还提供了一个简单图形化入口：

```bash
python examples/demo_launcher_gui.py
```

这个 GUI 的作用是把当前多分支 invariant skeleton 可视化出来：既能看内置 example，也能输入自定义 braid word，并在 formatter/raw 两种视图之间切换。它仍然不是 diagram editor，也不是完整的数学交互 GUI。

如果你已经在当前仓库根目录下，统一运行格式可以写成：

```bash
python examples/benchmark_P2_demo.py
```

在当前开发环境里，也可以直接使用已经配置好的解释器，例如：

```bash
C:/Users/dongqiyu/anaconda3/python.exe examples/benchmark_P2_demo.py
```

### 最推荐先跑的 demo

- `examples/representation_summary_demo.py`：先看当前支持哪些 Lie algebra / representation 对象，以及 tensor-square decomposition 的摘要。
- `examples/sl2_fundamental_rmatrix_demo.py`：看 `sl2 fundamental` 的局部 R-matrix / braid_matrix 数据。
- `examples/sl3_fundamental_rmatrix_demo.py`：看 `sl3 fundamental` 的局部 braiding 数据与谱结构。
- `examples/sl2_spin1_rmatrix_demo.py`：看 `sl2 spin1` 的 9x9 局部模型。
- `examples/sl3_projector_demo.py`：看 `sl3 fundamental` 的 projector / channel 结构。
- `examples/sl2_spin1_projector_demo.py`：看 `sl2 spin1` 的 projector / channel 结构。
- `examples/compare_9x9_local_data_demo.py`：直接比较两个 9x9 局部模型，即 `sl3 fundamental` 与 `sl2 spin1`。
- `examples/compare_9x9_raw_trace_demo.py`：比较两个 9x9 模型在 raw trace 层上的行为差异。
- `examples/compare_9x9_discriminating_power_demo.py`：比较当前 `sl2` 三维 `9x9` candidate branch 与 `sl3 fundamental` `9x9` branch 的 pairwise discriminating behavior，并输出结构化 summary。
- `examples/braid_operator_demo.py`：看 braid word 怎样被装配成全局 braid operator。
- `examples/raw_trace_demo.py`：看 raw closure trace 层会输出什么表达式。
- `examples/sl2_fundamental_eyb_demo.py`：看 `sl2 fundamental` 当前的 EYB-normalized 输出。
- `examples/sl3_fundamental_eyb_demo.py`：看 `sl3 fundamental` 当前的 EYB-normalized 输出。
- `examples/compare_A_type_invariants_demo.py`：比较当前两个 A-type fundamental 分支的 EYB-normalized 输出风格。
- `examples/benchmark_P2_demo.py`：批量运行 `P2-type` benchmark catalog。
- `examples/benchmark_P3_demo.py`：批量运行 `P3-type` benchmark catalog。
- `examples/markov_move_demo.py`：查看 conjugation / stabilization 的经验性回归检查。
- `examples/eyb_partial_trace_demo.py`：查看 partial trace 诊断，理解 raw-side 与 braid-side 为什么不能直接混为一谈。
- `examples/eyb_stabilization_ratio_demo.py`：直接看当前 braid-side normalization 的 stabilization ratio 是否为 1。
- `examples/convention_audit_demo.py`：查看当前项目的最终规范说明，即 raw-side audit 与 braid-side working convention 的并存关系。

### 建议的最小起步顺序

如果你只想用最少的时间理解当前项目，建议按下面顺序运行：

1. `examples/representation_summary_demo.py`
2. `examples/sl2_fundamental_rmatrix_demo.py`
3. `examples/braid_operator_demo.py`
4. `examples/raw_trace_demo.py`
5. `examples/benchmark_P2_demo.py`
6. `examples/convention_audit_demo.py`

这条路径可以让你从“支持哪些对象”一路看到“当前正式工作规范是什么”。

## 4. What the User Inputs

当前项目的输入层主要有三类：

- braid word
- representation choice
- 固定 catalog examples

### braid word 的当前约定

当前 braid word 使用 Artin 生成元的整数记法：

- `1` 表示 $\sigma_1$
- `2` 表示 $\sigma_2$
- `-1` 表示 $\sigma_1^{-1}$
- `-2` 表示 $\sigma_2^{-1}$

例如：

- `(1, 1, 1)` 表示 $\sigma_1 \sigma_1 \sigma_1$
- `(1, -2, 1, -2)` 表示 $\sigma_1 \sigma_2^{-1} \sigma_1 \sigma_2^{-1}$

两个极简输入例子：

- `num_strands = 2, generators = [1, 1, 1]`：表示一个 2-strand braid 上的 $\sigma_1^3$，是当前 demo 中最常见的 trefoil-style 例子。
- `num_strands = 1, generators = []`：表示 1-strand identity braid，也就是没有任何生成元作用的最小输入。

当前 braid word 还支持：

- 空 braid
- 1-strand identity braid

也就是说，当 `num_strands = 1` 时，允许生成元列表为空，这会被视为 identity braid。

### representation choice

当前支持的表示选择是固定且有限的：

- `sl2 fundamental`
- `sl2 spin1`
- `sl3 fundamental`

其中：

- `sl2 fundamental` 与 `sl3 fundamental` 目前已经接入 A-type fundamental 的 EYB-normalized 输出
- “`sl2 的3维表示下的9x9矩阵`” 当前已经具有 candidate normalization、quantum trace、unknot normalization 与 reduced candidate output，但仍不应被直接包装成“标准 colored Jones 已完成”
- 当前还新增了一个可复现的 `9x9 vs 9x9` discriminating-power benchmark；它强调两条 `9x9` 分支的通道结构不同、局部谱数据不同，而实际分辨力应以 benchmark 结果为准，而不是仅凭 channel 数目作武断判断。

### catalog examples

为了方便批量验证，项目还内置了一组 benchmark braid examples。当前常用的例子包括：

- `unknot_1`
- `trefoil`
- `figure_eight`

### 当前还不能直接输入什么

当前用户还不能：

- 直接在 GUI 里画 knot
- 直接输入任意 planar diagram
- 直接输入更一般的 link diagram 并自动做 Reidemeister / braid conversion

这些属于后续扩展目标，而不是当前正式输入层。

## 5. What the System Outputs

当前系统会输出多种不同层次的对象。理解这些层次很重要，因为它们的数学含义并不相同。

> 同一个 demo 可能同时打印 representation data、local braiding data、global braid operator、raw trace 和 EYB-normalized expression；这些对象的数学层次不同，不应混用名称。

### 表示层输出

- representation summary
- tensor-square decomposition

这层主要回答“当前表示是什么”“张量平方如何分解”“不同 channel 的维度与标签是什么”。

### 局部模型输出

- raw matrix
- `braid_matrix`
- eigenvalues
- minimal polynomial
- channel labels
- projector data

这层对应局部两股编织的模型数据。对于 `sl3 fundamental` 和 `sl2 spin1`，projector/channel 结构已经显式实现并做过验证。

### 全局 braid 输出

- braid operator
- operator dimension
- construction steps
- writhe

这层把一个 braid word 逐步装配成全局线性算子。它是从局部 braiding 走向全局闭包计算的桥梁。

### invariant 输出

- raw closure trace
- EYB-normalized expression（当前只对 A-type fundamental 正式提供）
- `sl2 fundamental` 的 reduced P2 / Jones-compatible output（当前默认比较 convention 为 `t = q^-2`）

这里需要特别强调：

- raw closure trace 是 raw trace 层对象
- 它不应直接被叫作 Jones polynomial 或 HOMFLY-PT polynomial
- 当前项目中的正式工作规范是 braid-side EYB normalization，而不是 raw trace 本身

### 审计 / 验证输出

- benchmark entries
- conjugation checks
- stabilization checks
- convention audit results

这层的目标不是“再算一个新不变量”，而是回答：

- 当前结果是否稳定
- 当前 normalization 是否与 Markov move 的经验性回归一致
- raw-side 与 braid-side 的关系到底已经澄清到什么程度

## 6. Recommended Usage Paths

不同类型的用户，最适合的使用路径并不一样。下面给出三条实用路线。

### 路线 A：只想快速看结果的用户

建议顺序：

1. `examples/representation_summary_demo.py`
2. `examples/sl2_fundamental_rmatrix_demo.py`
3. `examples/braid_operator_demo.py`
4. `examples/benchmark_P2_demo.py`
5. `examples/convention_audit_demo.py`

这条路线适合想快速知道“项目现在已经能做什么”的用户。你会先看到支持对象，再看到一个局部模型，然后看到全局 braid operator，再看到 benchmark，最后看到当前正式规范的总结。

### 路线 B：想比较 9x9 模型的用户

建议优先看：

1. `examples/sl3_fundamental_rmatrix_demo.py`
2. `examples/sl2_spin1_rmatrix_demo.py`
3. `examples/sl3_projector_demo.py`
4. `examples/sl2_spin1_projector_demo.py`
5. `examples/compare_9x9_local_data_demo.py`
6. `examples/compare_9x9_raw_trace_demo.py`

这条路线适合想理解两个 9x9 局部模型为什么“维数一样但语义不同”的用户。它也能帮助你看到 projector/channel 结构在这两个模型中的作用。

### 路线 C：想理解当前规范与理论关系的用户

建议优先看：

1. `examples/sl2_fundamental_eyb_demo.py`
2. `examples/sl3_fundamental_eyb_demo.py`
3. `examples/benchmark_P2_demo.py`
4. `examples/benchmark_P3_demo.py`
5. `examples/markov_move_demo.py`
6. `examples/eyb_partial_trace_demo.py`
7. `examples/eyb_stabilization_ratio_demo.py`
8. `examples/convention_audit_demo.py`

这条路线适合想弄清楚“当前为什么把 braid-side EYB normalization 当作正式工作规范，而 raw-side 仍然保留为 audit 层”的用户或开发者。

## 7. Project Architecture

当前项目的目录分层已经比较清楚，重点不只是“有哪些目录”，而是“每层负责什么”。

简洁地看，当前工程数据流可以写成：`algebra -> rmatrix -> braid -> invariants -> examples/tests`。

这条流的意义是：先定义表示对象，再构造局部 braiding 数据，再装配全局 braid operator，然后进入不变量 / 回归 / 审计层，最后由 demo 和测试把结果对外呈现并固定下来。

### `src/algebra/`

职责：Lie algebra 和 representation 的基础元数据。

这一层负责表示对象的定义、维数信息、tensor-square decomposition 摘要，以及对更高层模块暴露统一的结构化表示接口。

### `src/rmatrix/`

职责：局部两股 braiding 模型与 projector 数据。

这一层负责：

- `sl2 fundamental` 的局部模型
- `sl2 spin1` 的 9x9 局部模型
- `sl3 fundamental` 的 9x9 局部模型
- raw matrix 与 braid_matrix 的组织
- projector / channel 结构

这里是整个系统的“局部输入物理层 / 代数层”。

### `src/braid/`

职责：把 braid word 变成全局 braid operator。

这一层负责：

- braid word 数据结构
- 合法性检查
- writhe 计算
- 按生成元逐步装配全局算子
- 输出 operator dimension 与 construction steps

它把局部 braiding 数据提升到全局闭包计算可用的算子层。

### `src/invariants/`

职责：不变量相关的计算、比较、回归和审计。

这一层目前包含几个相互区分的子层：

- raw closure trace
- A-type fundamental 的 EYB-normalized invariant
- benchmark catalog evaluation
- Markov regression checks
- partial-trace diagnostics
- convention audit

这一层最重要的工程原则是：不要把不同数学层次混在一起命名。raw trace、EYB-normalized output、regression、audit 都是不同职责。

### `src/catalog/`

职责：内置 benchmark braid examples。

这一层提供固定、可复现的输入样本，方便做批量比较、演示和回归检查。

### `examples/`

职责：面向用户的 demo 入口。

这一层不是测试替代品，而是让用户快速看到：

- 当前支持哪些对象
- 局部数据长什么样
- 全局算子怎么构造
- 当前 benchmark / regression / audit 的输出是什么

当前 `examples/demo_launcher_gui.py` 已经接到当前多分支 invariant skeleton，可直接在 GUI 里选择 catalog example 并查看三条 branch 的统一结果卡片。

当前 `examples/braid_workbench_gui.py` 则是更适合研究工作流的主入口：它提供 braid builder、三分支 evaluation、pair comparison、experiment log、过滤、详情查看，以及结构化导出。

### `tests/`

职责：回归测试。

当前已经加入 braid-side EYB normalization 的 stabilization regression 测试，用来锁定“当前正式工作规范”不会被无意破坏。

## 8. Current Formal Working Convention

这一节是当前项目最重要的状态说明之一。

### 当前项目的正式工作规范是什么

当前项目的正式工作规范是 braid-side working convention，也就是当前 `sl2/sl3 fundamental` 上采用的 braid-side EYB normalization。

这意味着：

- 当前 `sl2 fundamental` 和 `sl3 fundamental` 的 EYB-normalized 输出，是项目中应被视为正式工作层的结果
- 这个工作层已经通过了 conjugation / stabilization regression
- 在当前项目语境里，如果用户问“现在哪一层是正式规范”，答案应当是 braid-side EYB normalization

### 为什么要这样明确

因为当前项目里同时存在：

- 一个可以工作的 braid-side normalization
- 一个仍在审计中的 raw-side 理论层

如果不把这两层明确分开，用户很容易误以为：

- raw trace 已经等于标准不变量
- raw-side partial trace 理论已经与 braid-side normalization 完全统一

这些理解在当前阶段都不准确。

### 当前已经验证到什么程度

在当前 braid-side convention 下：

- `sl2 fundamental` 的 stabilization regression 已通过
- `sl3 fundamental` 的 stabilization regression 已通过
- conjugation regression 也保持通过

因此，当前项目把 braid-side EYB normalization 视为“正式工作规范”是有代码验证基础的，而不是口头声明。

### 这不代表什么

这并不代表：

- raw-side 理论已经完全统一
- 所有理论层之间的精确转换公式已经完成
- 所有表示都已经有标准 RT normalization

当前 raw-side 部分仍然保留为独立 audit 层，这是一种刻意的、诚实的工程分层。

## 9. Raw-side Audit vs Braid-side Convention

这两层的角色不同，必须明确区分。

### raw-side audit 主要检查什么

raw-side audit 主要检查局部对象与 partial trace 条件之间的关系，例如：

- 不同 local object 的选择会导致什么 partial trace 行为
- `mu ⊗ identity`、`identity ⊗ mu`、`mu ⊗ mu` 这些权重放置方式分别会给出什么结果
- 哪些组合能够稳定表现为 `scalar * mu`

它的目标是“理论审计”，不是“直接定义当前项目的正式输出层”。

### braid-side working convention 主要负责什么

braid-side working convention 主要负责当前项目中真正对外工作的 invariant 规范。它的职责是：

- 定义当前 `sl2/sl3 fundamental` 的 EYB-normalized 输出
- 在现有代码实现上与 braid operator 管线对接
- 通过 stabilization / conjugation regression

它是当前项目的正式工作层。

### 当前两者的关系

当前最核心的结论是：

- braid-side normalization 现在能工作，并通过 regression
- raw-side 最稳定的候选表现为 `raw_matrix + mu ⊗ identity -> (q + dim(V) - 1) * mu`
- 这个标量与 braid-side 的 `q^dim(V)` 不是直接同一个 alpha
- 因此，当前项目采用“工作规范”和“理论审计层”并存的结构

这不是在掩盖问题，而是在避免把一个已经能工作的实现层和一个尚未完全统一的理论层硬塞成同一个结论。

### 当前 raw-side audit 的最重要结果

对于当前已经审计的 `sl2/sl3 fundamental`：

- 最稳定的 raw-side 候选是 `raw_matrix + mu tensor identity`
- 它给出的行为是 `(q + dim(V) - 1) * mu`
- 这个规律在 `sl2 fundamental` 上表现为 `(q + 1) mu`
- 在 `sl3 fundamental` 上表现为 `(q + 2) mu`
- 它与当前 braid-side 的 `q^dim(V)` 共享相同的参数 `q`，但不是直接相同的 scalar

因此，当前项目的结论不是“理论统一完成”，而是“理论关系已经被清楚审计，并以分层方式保存”。

## 10. Mathematical Background (Brief)

这一节只提供理解代码对象所需的最小数学背景。

### representation

项目从表示出发，例如 `sl2 fundamental`、`sl2 spin1`、`sl3 fundamental`。这些表示决定了局部空间维数，也决定了局部 R-matrix 的大小与谱结构。

### tensor-square decomposition

当一个表示和自身做张量平方时，会分解成若干 channel。projector 数据正是用来把这些 channel 显式拆开。

### local braiding

局部 braiding 由两股上的局部线性算子给出。代码里会区分 raw matrix 与 braid_matrix，因为它们在解释层和归一化层上的角色并不完全相同。

### projectors

projectors 把张量平方空间分解到不同 channel 上，并让局部 braiding 的特征值结构更透明。当前 `sl3 fundamental` 和 `sl2 spin1` 的 projector/channel 结构已经显式实现并验证。

### braid operator

给定 braid word 后，系统会把每个局部生成元依次提升为全局算子，再按顺序相乘，得到全局 braid operator。

### raw closure trace

raw closure trace 是直接对全局 operator 做 trace 得到的表达式。它是一个有用的中间层，但当前不应直接把它命名成 Jones 或 HOMFLY-PT。

### EYB-normalized invariant

EYB-normalized invariant 是在 braid-side working convention 下，对 raw operator 结果进行当前项目正式采用的归一化后得到的输出。当前这层只在 A-type fundamental 分支上正式提供，也就是 `sl2 fundamental` 与 `sl3 fundamental`。

## 11. Verified Results

下面这些结论已经通过当前代码层面的实现、demo 或回归运行得到验证：

- [x] `sl3 fundamental` 的 projector family checks 已通过
- [x] `sl2 spin1` 的 projector family checks 已通过
- [x] `sl3 fundamental` 与 `sl2 spin1` 的 projector/channel 结构已经显式实现并验证
- [x] `P2-type` benchmark catalog 可以批量运行
- [x] `P3-type` benchmark catalog 可以批量运行
- [x] conjugation regression passes
- [x] stabilization regression passes under current braid-side convention
- [x] 当前 braid-side EYB normalization 是有回归测试保护的正式工作层
- [x] convention audit 已识别出当前 raw-side 的稳定候选行为
- [x] `sl2 fundamental` 的 reduced P2 已作为 Jones-compatible layer 固定，并在 `unknot_1`、`trefoil`、`figure_eight` 上按默认比较 convention `t = q^-2` 通过回归

这些“已验证结果”并不意味着所有理论问题都已经结束，但它们确实定义了项目当前可依赖的工程基础。

## 12. Current Limitations

当前限制需要明确写出来，避免用户误判项目完成度：

- 当前只有简单 demo launcher GUI，尚未实现完整数学交互 GUI
- 图形化 knot 输入尚未实现
- 任意 planar diagram 输入尚未实现
- raw-side 与 braid-side 的精确转换公式尚未完全统一
- “`sl2 的3维表示下的9x9矩阵`” 已经从 raw/projector-aware 层升级到 colored Jones candidate branch，但仍没有 theorem-level 的最终 RT / colored Jones normalization 结论
- generalized RT normalization for all reps 尚未实现
- 新的 Lie algebra families 尚未展开
- 当前重点仍是明确规范与验证，而不是全面功能扩展

尤其需要再次强调：

- raw trace 不是当前项目中应当直接对外宣称的标准 knot polynomial
- raw-side audit 也不应被描述成“理论统一已经完成”

## 13. Suggested Next Steps

如果后续继续开发，比较合理的顺序是：

1. 写一份更偏论文式的 convention note，把当前 braid-side working convention 与 raw-side audit 的分层关系再正式整理一次。
2. 继续追 raw-side 到 braid-side 的精确变换公式，明确哪些差异来自局部对象选择、哪些差异来自 normalization 选择。
3. 在规范彻底清楚之后，再评估是否推进 `sl2 spin1` 的 RT normalization / colored Jones 对应命名。
4. 最后再考虑 GUI 和 diagram input，把它们建立在已经稳定的规范之上。

在当前阶段，最重要的不是继续横向扩展功能，而是保持“规范清楚、验证明确、术语诚实”。