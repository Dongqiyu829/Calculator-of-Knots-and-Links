# Simple Examples

## 1. What This Document Is For

这份文档是给第一次使用这个项目的人看的。目标不是讲完整理论，而是通过几个最小、最具体的例子，让你快速知道现在该怎么操作、会看到什么输出、应该怎样理解这些输出。完整项目说明请看 `docs/current_summary.md`。

## 2. Before You Start

开始之前，你只需要准备一个能运行当前项目的 Python 环境。当前开发与验证环境是 Python 3.12.4，主要依赖是 `sympy`。

建议在项目根目录运行命令，最基本的格式是：

```bash
python examples/representation_summary_demo.py
```

如果你在当前开发环境里使用显式解释器路径，也可以写成：

```bash
C:/Users/dongqiyu/anaconda3/python.exe examples/representation_summary_demo.py
```

如果你不想逐条在命令行里敲 demo，也可以先启动一个简单图形界面：

```bash
python examples/demo_launcher_gui.py
```

这个界面现在会默认打开 `trefoil`，你可以在窗口里切换 `unknot_1 / trefoil / figure_eight`，再切换三条 branch 的显示；也可以直接手写生成元，或者点击 `+σi / -σi` 按钮构造一个自定义 braid，并在 formatter/raw 两种报告视图之间切换。

如果你现在想看“这个项目整体上已经像什么程序”，最推荐的新入口是：

```bash
python examples/multibranch_invariant_demo.py
```

这是当前最接近“整体程序视图”的例子，因为它会把同一个 braid example 放到多个 invariant branch 下统一打印。

现在这个 demo 展示的也是统一 formatter 生成的总览输出，而不再是手写 print 拼接。

## 3. Example 1 — See What Representations Are Supported

使用：

```bash
python examples/representation_summary_demo.py
```

这个例子的作用是先告诉你：当前项目到底支持哪些表示对象。它会依次打印当前已经实现的表示摘要，是最适合第一次运行的入口。

你会看到的输出重点通常包括：

- representation name
- dimension
- tensor-square decomposition

第一次看时，最值得关注的是：

- 当前支持的是 `sl2 fundamental`、`sl2 spin1`、`sl3 fundamental`
- 不同表示的维数不同
- tensor-square decomposition 已经作为后续 projector / channel 数据的基础被整理出来

这一节的目标很简单：先建立“这个项目支持哪些对象”的第一印象。

## 4. Example 2 — Inspect a Simple Local Braiding Model

使用：

```bash
python examples/sl2_fundamental_rmatrix_demo.py
```

这个例子展示的是最简单的局部两股 braiding 模型，也就是 `sl2 fundamental` 上的局部 R-matrix / braid_matrix 数据。

这里可以先用很直观的方式理解：

- raw matrix：更接近原始局部算子数据
- braid_matrix：更接近当前 braid-side 计算管线里实际使用的局部编织对象

第一次看这个 demo，建议重点关注：

- basis order
- eigenvalues
- minimal polynomial
- Yang-Baxter check

你不需要一开始就理解全部理论背景。只要先知道：这个 demo 是在看“局部两股模型是否构造正确、谱结构是否清楚、Yang-Baxter 关系是否满足”。

## 5. Example 3 — Build a Global Braid Operator

使用：

```bash
python examples/braid_operator_demo.py
```

这个例子会把一个很小的 braid word 装配成全局 braid operator，是从局部对象走向全局对象的第一步。

当前 demo 使用的 braid word 形式类似：

- `[1, 1, 1]` 表示 $\sigma_1 \sigma_1 \sigma_1$

直观理解就是：系统会按生成元顺序，把局部 braiding 数据一层一层嵌入到全局张量空间里，最后得到 global braid operator。

你通常会看到这些输出：

- word
- writhe
- total dimension
- construction steps

这一节最重要的理解是：局部两股模型不是最终输出，它们会被进一步装配成一个作用在整个 braid 上的全局线性算子。

## 6. Example 4 — Compute a Raw Closure Trace

使用：

```bash
python examples/raw_trace_demo.py
```

这个例子展示的是最原始的闭包 trace 层。它会把一个全局 braid operator 做闭包 trace，并打印对应的 raw expression 以及相关说明。

这层为什么有用：

- 它是从全局 braid operator 走向不变量层的重要中间步骤
- 它能帮助你看清当前系统最基础的闭包计算在做什么

但这里一定要注意：

- raw trace 是中间层
- 它不是当前正式工作规范的最终命名层
- 当前不应直接把它叫作标准 Jones polynomial 或 HOMFLY-PT polynomial

如果你看到一个 raw expression，不要立刻把它当成最终标准命名的不变量；在当前项目里，这种叫法是不准确的。

## 7. Example 5 — Run a P2-type Benchmark

使用：

```bash
python examples/benchmark_P2_demo.py
```

这个 demo 会批量跑 catalog 里的一组小 braid examples，比只跑单个 demo 更接近“实际使用”场景。它会把同一种表示分支上的多个标准小例子统一评估出来。

你通常会看到的结果包括：

- 每个 example 的标签
- 对应 braid word
- 相关 invariant / benchmark entry 摘要

为什么这一步重要：

- 它比单个例子更能体现“系统现在能不能稳定地批量输出结果”
- 它也是后续 regression / audit 层的重要基础

如果你想看对应的另一条分支，`P3-type` 也有类似入口：`examples/benchmark_P3_demo.py`。

## 8. Example 6 — Run the Jones-Compatible Benchmark

使用：

```bash
python examples/jones_benchmark_demo.py
```

这个例子会把 `unknot_1`、`trefoil`、`figure_eight` 放到同一个 benchmark 视图里，同时打印三条分支：

- `sl2 fundamental`：raw trace、unreduced P2、unknot normalization、reduced P2、Jones-compatible output
- `sl3 fundamental`：raw trace、P3-type EYB output
- `sl2 spin1`：raw trace 和 projector-aware branch status

如果你当前关心 Jones，这个 demo 最重要的一点是：这里真正应该和 Jones 比较的是 reduced 层，而不是 unreduced P2。

## 9. Example 7 — Check the Current Formal Working Convention

使用：

```bash
python examples/convention_audit_demo.py
```

这个例子不是第一次上手就必须马上看的，但如果你想知道“当前项目正式采用哪一层规范”，它是最重要的 demo。

这里需要明确三件事：

- 当前正式工作规范是 braid-side EYB normalization
- raw-side audit 是独立的理论审计层
- 这两层不能混为一谈

你可以把这个 demo 理解为“当前项目状态声明”的可运行版本。它不是为了再给你一个新不变量，而是为了告诉你：

- 哪一层结果是当前项目正式采用的工作层
- 哪一层结论仍然属于理论审计
- 当前已知的 raw-side 稳定候选行为是什么

当前需要保持清楚的口径是：

- `sl2/sl3 fundamental` 的 stabilization regression 已在当前 braid-side convention 下通过
- raw-side audit 仍然是独立层
- 当前 raw-side 最稳定的候选行为是 `raw_matrix + mu tensor identity -> (q + dim(V) - 1) * mu`
- 这个 scalar 与 braid-side 的 `q^dim(V)` 不是直接同一个 alpha

这不是“理论已经完全统一”的说法，恰好相反，这是当前项目对自身状态的诚实说明。

## 10. Suggested Reading Order

如果你只想快速上手，建议按这个顺序看：

1. representation summary
2. local rmatrix demo
3. braid operator demo
4. raw trace demo
5. benchmark demo
6. jones benchmark demo
7. convention audit demo

这个顺序的好处是：你会先看到支持对象，再看到局部模型、全局对象、原始 trace 层，最后再看到当前正式工作规范与理论审计层的关系。

如果你当前最关心的是 `sl2` 三维 `9x9` candidate branch 到 Knot Atlas 的对应关系，可以直接运行：

```bash
python examples/check_sl2_3d_knot_atlas_correspondence.py
```

这个脚本会直接打印当前共享口径：为什么这里要对照 Knot Atlas `n=2`、当前已确认的 `3_1` 与 `5_1` q-shift 对应关系，以及为什么 `5_2` 仍然只写作 under verification。

## 11. Common Misunderstandings

下面这些误解很常见，最好一开始就避免：

- raw trace 不是标准 Jones polynomial，也不应直接叫 HOMFLY-PT polynomial
- 如果比较 Jones，当前应该比较 `sl2 fundamental` 的 reduced P2 / Jones-compatible layer，而不是 unreduced P2
- 当前正式工作规范是 braid-side EYB normalization，不是 raw-side audit
- `sl2 spin1` 当前还不应直接叫成标准 colored Jones
- raw-side audit 不是“理论已经统一完成”的同义词
- 当前有一个简单 demo launcher GUI，但还没有完整数学交互 GUI，也还没有任意 diagram drawing input

## 12. Where to Go Next

如果你想继续看更完整的说明：

- 完整项目说明请看 `docs/current_summary.md`
- 更多 demo 请看 `examples/`
- 回归 / 测试请看 `tests/`

如果你已经跑完这份文档中的几个例子，下一步最自然的动作通常是：先看 `docs/current_summary.md`，再挑你关心的 demo 或测试继续深入。