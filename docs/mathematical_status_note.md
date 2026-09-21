# 数学状态说明

## 1. Executive Summary

当前项目已经形成一个多分支的 topology invariant program skeleton。它围绕 braid word、表示上的局部 braiding 数据、全局 braid operator，以及按 branch 区分的输出层来组织，而不是把所有输出混成一个没有层次的“结不变量计算器”。

目前最强、最正式的分支是：

- `sl2 fundamental` -> Jones-compatible branch

目前已经 formal、并且在程序结构中稳定可用，但还没有进一步提升为更强 classical-object alignment 声称的分支是：

- `sl3 fundamental` -> P3-type EYB branch

目前处于 candidate / formalizing 阶段、但尚未提升为 theorem-level 结论的分支是：

- `sl2 spin1` -> colored Jones candidate branch based on the sl2 3-dimensional 9x9 local data

当前程序已经有统一的 branch registry、benchmark 层、formatter/report 层，以及接到真实 program skeleton 的 GUI，而不是仅仅由若干孤立脚本或 mock 页面组成。但这并不意味着所有分支都已经完成 formal normalization；不同分支目前处在不同的数学成熟度上。

因此，这份说明刻意区分以下几类状态，不将它们混写：

- mathematical claim
- engineering validation
- current formal working convention
- exploratory branch
- proven / aligned / tested / not yet settled

在本说明中：

- “proven” 仅用于当前实现中已经被精确固定的代数关系或分支层对象，不把 smoke test 叫成 theorem
- “aligned” 表示在当前固定的 comparison layer 与 benchmark 例子上已经对齐，而不是对任意输入都作出新的数学定理声称
- “tested” 表示已经由当前仓库中的 regression、demo 或 smoke test 验证
- “not yet settled” 表示理论桥、命名层或 normalization 层仍然故意保持开放，不假装已经闭合

## 2. Mathematical Input Objects

当前程序的数学输入对象主要包括以下几类。

### 2.1 Braid words

程序当前以 braid word 作为主要拓扑输入。内部对象是 `BraidWord`，由以下数据组成：

- strand 数 `n`
- 一列 Artin generators `sigma_i` 与 `sigma_i^-1`

也就是说，当前程序工作在 braid 层，而不是一般 knot diagram 输入层。它目前并不声称自己是一个完整的 planar diagram engine，也不声称已经实现任意 diagram 到 braid 的统一正规化管线。

### 2.2 Representations

当前支持的表示是：

- `sl2 fundamental`
- `sl3 fundamental`
- `sl2 spin1`

这些表示决定了局部 braiding operator 作用在哪个 `V tensor V` 上，也决定了全局 braid operator 的装配方式。

### 2.3 Local braiding operators on `V tensor V`

每条 branch 的局部输入对象都不是抽象的“一个 R 矩阵名称”，而是一个具体作用在 `V tensor V` 上的局部 braiding operator。

对于两个 3 维表示分支：

- `sl3 fundamental`
- `sl2 spin1`

真正参与 braid 计算的局部对象都是 `9 x 9`，因为它们作用在 `V tensor V` 上，而不是直接作用在 `V` 上。

因此，当前项目中的 `sl3 fundamental` 和 `sl2 spin1` 都不应被理解为“3 x 3 braid operator”。对这两条线来说，当前真正相关的局部模型都是 `9 x 9` 的 braiding object。

### 2.4 Global braid operators

从局部 braiding operator 与 braid word 出发，程序会构造全局 braid operator。这个对象是从局部表示论数据走向闭包 trace、EYB 输出以及 branch-level invariant output 的程序桥梁。

## 3. Current Program Branches

当前程序必须按 branch 来理解，而不能假设它已经形成了一个数学上完全统一、命名上完全闭合的单层输出系统。

### A. `sl2 fundamental`

`sl2 fundamental` 当前已经形成 formal 的 Jones-compatible branch。

它明确区分以下输出层：

- raw trace
- unreduced `P2`
- reduced `P2`
- Jones-compatible output

当前默认的 comparison convention 是：

- `t = q^-2`

这条线之所以是 formal main line，不是因为程序“把某个 sl2 表达式随便叫成 Jones”，而是因为它已经把 unreduced 与 reduced 层明确拆开，并把 Jones-compatible 输出固定在 reduced 层上。

### B. `sl3 fundamental`

`sl3 fundamental` 当前是 formal 的 `P3`-type EYB branch。

它已经具有：

- 稳定的 branch identity
- 稳定的 branch status
- 稳定的 benchmark 输出
- 稳定的 formatter/report 展示
- 通过 shared registry 接入 GUI 与统一 skeleton 的能力

但它目前还没有进一步被包装成某个更强 classical object 的对齐层。因此当前最准确的说法是：它已经是 formal and usable 的 `P3`-type EYB branch，但 claim strength 低于 `sl2 fundamental` 的 Jones-compatible branch。

### C. `sl2 spin1`

`sl2 spin1` 当前不再只是 exploratory 的 projector-aware raw branch。它已经升级为基于 `sl2` 三维表示 `9 x 9` 局部数据的 colored Jones candidate branch。

它已经有：

- `9 x 9` 的局部 braiding object
- projector-aware local data
- projector-aware structural checks
- 通过统一 registry / benchmark / formatter skeleton 的 branch integration

但它目前还没有 theorem-level 完整锁定的 formal RT normalization。因此当前最准确的口径仍然是 colored Jones candidate branch，而不是已经最终定名的 colored Jones branch。

## 4. What Is Actually Guaranteed

这一节只陈述当前真正已经被固定、被检查或仍未闭合的内容，不将不同级别的“保证”混写。

### 4.1 已经被当前程序正式固定的内容

以下内容已经在当前程序结构中被固定下来。

- `sl2 fundamental` 的 reduced / Jones-compatible layer 已由专门的 regression 路径固定，构成当前 formal main branch output layer
- `unknot_1`、`trefoil`、`figure_eight` 已作为当前主线中的固定参考例子出现于 branch 比较与 benchmark 中
- unified branch registry 能稳定地用一个统一接口评估当前三条分支
- multibranch benchmark 层能稳定地在当前 catalog 上跨 branch 运行
- formatter/report 层能稳定输出 branch result 与 multibranch benchmark entry
- GUI 已接到真实 evaluator / formatter skeleton，而不是 mock shell

这些都是程序层面已经固定的保证。它们说明当前主线结构是稳定的，但本身不应被误读为关于任意未来 branch 或任意 normalization 的 theorem。

### 4.2 已由结构检查保证、且当前稳定可用，但尚未提升为更强 formal claim 的内容

以下内容已经通过有意义的结构检查或工程验证，但其 claim strength 低于 `sl2 fundamental` 主线。

- `sl3 fundamental` 作为 formal `P3`-type EYB branch，当前已经稳定可用
- `sl2 spin1` 的 projector-aware checks 已经通过：
  - sum to identity
  - pairwise orthogonality
  - reconstruction
- `sl3 fundamental` 与 `sl2 spin1` 各自都已有 coherent 的 `9 x 9` local object，并已接入同一套 braid-operator 管线

这些内容重要且非平凡，但它们本身还不足以把所有 branch 都提升到同一强度的 normalization 声称。

### 4.3 还没有被正式保证的内容

以下内容目前仍然故意保持开放。

- `sl3 fundamental` 尚未进一步被锁定为某个更强 classical object 的对齐层
- `sl2 spin1` 尚未完成 theorem-level 最终 RT normalization；当前只应称为 colored Jones candidate branch
- raw-side audit 到 braid-side working convention 之间的理论桥尚未在一个最终概念包里完全闭合
- GUI 已经工作，并不意味着所有数学归一化问题都已经解决

## 5. Why the `sl2 fundamental` Branch Is Considered Formal

`sl2 fundamental` 被视为 formal，并不是因为程序把某个 sl2 输出直接重命名成 Jones，而是因为当前项目已经把相关层次明确分开，并把 reduced layer 作为真正的 comparison layer。

### 5.1 最初遇到的 normalization 问题

项目早期曾经遇到的关键问题之一，是 unreduced `P2` 类型表达式与 standard Jones polynomial 之间被比较得过于直接。这样的比较在数学上并不准确，因为命名层与 normalization 层没有被区分清楚。

### 5.2 为什么 unreduced `P2` 不能直接拿来和 Jones 比较

unreduced `P2` 本身是一个合理的程序输出层，但它不是当前项目中与 Jones 直接比较的正确层。若不进一步处理 normalization，就不能把 unreduced 输出直接叫成 Jones-compatible。

因此当前程序明确区分：

- current braid-side EYB pipeline
- 该 pipeline 里产生的 unreduced `P2`
- 通过当前 unknot value 归约得到的 reduced `P2`
- 最终用于比较的 Jones-compatible output

### 5.3 为什么 reduced `P2` 才是这里正确的比较层

reduced 层去除了 unreduced 输出中的额外 normalization 因子，因此在当前项目中，它才是数学上正确的 Jones comparison layer。

在当前代码库中，这个 reduced 层已经由专门的 regression 工作固定下来，并被暴露为 formal comparison output。

### 5.4 为什么现在可以把它叫作 Jones-compatible branch

当前这一分支之所以被称作 Jones-compatible，不是因为“看起来像 Jones”，而是因为：

- 程序现在明确使用 reduced layer，而不是 unreduced layer
- 默认比较 convention 已固定为 `t = q^-2`
- 相关 regression 已在当前 benchmark 例子上固定该层

因此，准确的说法应当是：

- 当前 `sl2 fundamental` 是程序中的 formal Jones-compatible branch
- 这一地位由 reduced-layer regression 与 branch integration 支持
- 这不应被误读成脱离当前实现语境、对任意输入成立的新 theorem 声称

## 6. Why the `sl3 fundamental` Branch Is Reasonable but More Modest

`sl3 fundamental` 之所以是合理的，不是因为它只是“程序顺手算出来的另一个表达式”，而是因为它已经具有连贯的 local object、稳定的 braid-operator integration、稳定的 EYB 输出层，以及与 branch registry、benchmark、formatter、GUI 的稳定集成。

在这个意义上，它已经是 formal 且 usable 的分支。

但它当前的 claim strength 仍然刻意比 `sl2 fundamental` 更保守。

当前最准确的说法是：

- 这条线在当前 braid-side working convention 下，是 formal 的 `P3`-type EYB branch
- 它的 branch identity 与 program integration 已经稳定
- 它在当前项目中的 benchmark behavior 已稳定
- 它还没有像 `sl2 fundamental` 一样，被进一步锁定到更强 classical-object alignment 层

因此，对 `sl3 fundamental` 的最好描述是：

- formal and usable
- branch-level 稳定
- 但 claim strength 明确低于 `sl2 fundamental`

这样写的目的，是避免把它过度宣传成已经达到比当前事实更强的数学地位。

## 7. Why the `sl2 spin1` 9x9 Branch Is Candidate Rather Than Fully Formal

`sl2 spin1` 这条线应被认真对待，但仍不能被过度命名。

### 7.1 为什么它不能直接叫 colored Jones

当前程序尚未为这条线完成 formal RT normalization。缺少这一层时，直接把它叫成完成态的 colored Jones branch，会明显超出当前项目的实际状态。

### 7.2 当前已经有哪些有意义的检查

这条线已经有具有数学意义的局部结构：

- 作用在 `V tensor V` 上的 `9 x 9` braiding object
- 显式的 projector-aware local data
- 以下结构检查：
  - sum to identity
  - pairwise orthogonality
  - reconstruction

这些检查之所以重要，是因为它们表明当前的局部分解与 projector 包是 coherent 的，而不是随意塞进程序的若干矩阵。

当前这条线还已经提升到 candidate normalization 层，而不再只是 projector-aware raw trace-only branch。现在程序中会显式区分：

- raw trace
- quantum trace before normalization
- unreduced candidate output
- unknot normalization
- reduced candidate output

### 7.3 为什么这些检查仍不足以把它提升为 formal normalized branch

projector-aware structural correctness 不等于 branch-level formal normalization。前者说明局部代数包是值得信赖、值得继续用来做实验的；后者则需要完成最终的 normalization 叙述，才能支撑更强的拓扑命名声称。

因此，这条线当前被称为 candidate，不是因为它“只是半成品”，而是因为它已经从 local structural level 继续向上推进到了 branch-level candidate normalization，但仍未上升到 fully settled branch level。

### 7.4 当前它在程序中的地位

当前这条线在程序中的位置是：

- 作为一个 coherent 的 colored Jones candidate comparison branch
- 在统一 multibranch skeleton 中支撑 quantum-trace / candidate normalization 实验
- 为将来的最终 RT normalization 工作提供真实、已结构化的基础

当前仓库里还新增了一个 `9x9 vs 9x9` discriminating-power benchmark，用来系统比较：

- `sl2` 的3维表示下的 `9x9` candidate branch，其中 `3 tensor 3 = 5 plus 3 plus 1`
- `sl3 fundamental` 的 `9x9` branch，其中 `3 tensor 3 = 6 plus 3bar`

这份 benchmark 刻意不把“通道更多”直接包装成“分辨力一定更强”。当前更准确的解释是：

- 两条线的 channel structure 不同
- 局部 spectral data 不同
- 实际 branch-level discriminating power 应以 benchmark 输出为准

这已经是有意义的程序地位，只是它还不是与 `sl2 fundamental` 同级别的 formal output branch。

### 7.5 当前与 Knot Atlas 的对应关系声明

当前这条线已经有一个明确但刻意保守的外部对应关系声明：Knot Atlas 把 `J_n` 记作 `(n+1)` 维 `sl2` 表示下的 colored Jones 数据，因此当前程序里的 3 维 `sl2 spin1` candidate branch 对照的是 Knot Atlas 的 `n=2` 数据。

当前已经确认：

- `3_1`：`reduced candidate output = q^6 J_2(3_1; q^2)`
- `5_1`：`reduced candidate output = q^10 J_2(5_1; q^2)`

当前仍只写作 under verification：

- `5_2`：Knot Atlas 的 `J_2` 参考多项式已经固定，但当前项目内要使用的 braid representative 还没有最后固定

这组 statement 的语义必须收紧在“current calibrated correspondence”层面，而不是 theorem-level 最终 normalization 结论。

## 8. Local 9x9 Braiding Data: Level of Confidence

对于当前的 `9 x 9` local objects，应当区分三个不同层次：

- local structural correctness
- branch-level formal correctness
- classical-object alignment

这三个层次不能混为一谈。

### 8.1 `sl3 fundamental`

对于 `sl3 fundamental`，当前的 `9 x 9` braiding data 已经达到 formal branch usage level。

这意味着：

- 它不是仅供观察的实验性 local data
- 它已经作为 formal `P3`-type EYB branch 的局部基础被正式使用
- 它已稳定接入 branch registry 与 benchmark 层

但这并不自动推出它已经被提升为更强的 classical-object alignment 声称。当前能说的是：在程序内部，它已经足够可信，可以作为 formal branch 的 local foundation。

### 8.2 `sl2 spin1`

对于 `sl2 spin1`，当前 `9 x 9` braiding data 已通过 projector-aware structural checks，因此作为 local data 是有意义且值得信赖的。

当前程序支持的说法是：

- 它在 projector-aware 层面上是 structurally coherent 的
- 它适合作为当前实现中的 candidate branch usage

但当前程序还不支持更强的说法，即“这条 branch-level normalization 已经完成”。

### 8.3 应有的层级区分

因此，当前最准确的层级关系是：

- local structural correctness：`sl3 fundamental` 与 `sl2 spin1` 都已经具备
- branch-level formal correctness：`sl3 fundamental` 已 formal，`sl2 spin1` 当前处于 candidate / formalizing 阶段
- classical-object alignment：`sl2 fundamental` 最强，`sl3 fundamental` 更保守，`sl2 spin1` 尚不声称

## 9. Current Working Convention and Raw-side Audit

当前程序正式采用的是 braid-side working convention 作为官方输出层。

这意味着：

- 当前 formal outputs 来自 braid-side working layer
- branch-level formal reporting 围绕这一层组织
- multibranch skeleton、formatter、benchmark、GUI 也都从这一层取输出

与此同时，raw-side audit 仍被保留。

保留 raw-side audit 不是因为程序不能用，而是因为 raw-side candidate behavior 与当前采用的 braid-side convention 之间的理论桥还不应被过早地“语言上抹平”。

因此：

- raw-side audit 当前是 explanatory / audit layer
- 它不是主要输出层
- 它被保留，是为了不隐藏尚未完全闭合的理论桥

这是一种有意识的学术诚实，而不是程序失效的表现。

## 10. Why the Program Is Already Usable

即使保持上述区分，当前程序依然已经是值得数学家使用的。

### 10.1 同一个 braid example 可以统一比较多个 branch

现在同一个 braid example 已经可以通过统一 branch registry 在多条 branch 上一起计算，从而比较不同 branch 的行为，而不需要在多个互不相干的脚本之间来回切换。

### 10.2 formal / candidate / exploratory status 是显式的

程序现在在 branch 层已经显式标出 formal、candidate 与 exploratory 等不同状态，这降低了把所有输出误当作同一数学强度对象的风险。

### 10.3 当前程序不是一堆孤立脚本

当前项目已经具有：

- unified branch result object
- unified branch registry
- multibranch benchmark layer
- formatter/report layer
- 接到真实 evaluator 的 GUI

因此它已经是一个 coherent 的 program skeleton，而不是零散 demo 的堆积。

### 10.4 当前已经适合的使用方式

当前程序已经适合：

- 小例子比较
- branch behavior inspection
- exploratory invariant experiments
- future normalization work 的程序基础建设

这已经构成了一个有意义的使用层级，即便不是所有 branch 都已经 formalized。

## 11. What the Program Does Not Yet Claim

当前程序明确不声称以下内容。

- 它不声称所有 branch 都已经 formalized
- 它不声称 `sl2 spin1` 已经可以直接叫 colored Jones
- 它不声称 `sl3 fundamental` 已经提升到更强 classical-object alignment 层
- 它不声称 raw-side / braid-side 的理论统一已经全部结束
- 它不声称 GUI 接上真实 skeleton 就意味着数学上的 normalization 问题已经解决

这些“不声称”不是缺陷，而是当前项目状态陈述的一部分。

## 12. Reproducibility and Verification

如果数学读者希望亲自检查当前状态，至少应查看以下测试与 demo。

### Tests

- `tests/test_sl2_jones_compatible_regression.py`
  - 固定当前 `sl2 fundamental` 的 Jones-compatible regression layer，并在当前 benchmark 例子上锁定该输出层
- `tests/test_multibranch_benchmark_smoke.py`
  - 检查 multibranch benchmark skeleton 是否能一致地评估当前各条 branch
- `tests/test_branch_formatter_smoke.py`
  - 检查 formatter/report layer 是否能稳定地渲染当前 branch result 与 multibranch result object

### Demos

- `examples/multibranch_invariant_demo.py`
  - 展示同一个 braid example 如何在当前 unified branch structure 中被跨 branch 评估
- `examples/jones_benchmark_demo.py`
  - 展示当前 `sl2 fundamental` 的 reduced / Jones-compatible layer，并同时呈现其他 branch 在标准小例子上的输出

这些测试与 demo 的地位是 engineering validation 与 reproducibility tool。它们的作用是让当前实现状态可检查、可重复，而不是把它们当作 theorem statement 本身。

## 13. Outlook

当前后续路线是清楚的。

- 推进 `sl3 fundamental` 的进一步标准化与解释层整理
- 推进 `sl2 spin1` 的 formal RT normalization
- 继续整理 raw-side / braid-side 理论桥
- 在已经统一的 program skeleton 之上继续增强 GUI 与 richer input 层

当前最重要的一点是：未来工作已经可以在一个 branch-explicit、status-explicit 的程序结构上继续推进，而不必回到一个混合了不同强度声称的未分层脚本集合。
