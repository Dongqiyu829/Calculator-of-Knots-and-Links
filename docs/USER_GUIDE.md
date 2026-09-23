# User Guide / 用户指南

This guide describes the maintained Windows desktop application. It is also
bundled with the packaged application so Help works offline.

本指南介绍维护中的 Windows 桌面应用。它会随打包程序一起提供，因此离线时也可通过“帮助”菜单阅读。

## Installation / 安装

Download the **Windows Installer** from the bilingual README download section
for a normal per-user installation. Keep the default `%LOCALAPPDATA%\Programs`
location; no administrator elevation or PATH change is required. The portable
ZIP is useful when you want to unpack a folder without installing.

从 README 的双语下载区下载 **Windows 安装版** 进行普通的当前用户安装。建议保留默认的 `%LOCALAPPDATA%\Programs` 位置；无需管理员权限，也不会修改 PATH。需要免安装运行时可解压便携版 ZIP。

Windows SmartScreen may warn because the preview binaries are unsigned. Verify
`SHA256SUMS.txt` when downloading from an unfamiliar network.

由于预览程序未进行代码签名，Windows SmartScreen 可能显示常规警告。从不熟悉的网络下载时，请核对 `SHA256SUMS.txt`。

## First launch and interface / 首次启动与界面

The main window has two maintained workflows:

1. **Invariant calculation** — choose a catalog example or enter a custom
   signed Artin braid, choose branches and an exact/symbolic `q`, then press
   **Calculate**.
2. **Custom R/check-R operator** — provide an explicitly labelled raw `R` or
   `check-R`, validate optional relations, and optionally construct a braid
   operator.

主窗口包含两个维护中的工作流：

1. **不变量计算**——选择目录示例或输入带符号的 Artin 辫子，选择分支和精确/符号 `q`，然后点击 **Calculate**。
2. **自定义 R/check-R 算子**——明确选择原始 `R` 或 `check-R`，可选验证关系，再构造辫子算子。

The **Mathematics / How it works** dock is contextual. Its text comes from the
frontend-neutral service catalog and changes with the selected branch, braid,
or matrix input. Opening it never evaluates an invariant.

Use **View → Curated examples** or **View → Mathematics / How it works** to
open the side panels. They share one dock area and can be closed to give the
working page more room.

**Mathematics / How it works** 面板会随当前分支、辫子或矩阵输入变化。说明文字来自前端无关的 service 目录；打开面板不会计算不变量。

通过 **View → Curated examples** 或 **View → Mathematics / How it works** 打开侧边面板。两者共用一个停靠区域；关闭后可扩大工作页面。

## Curated examples / 精选示例

Open the **Curated examples** dock, filter by category or search text, inspect
the status/provenance details, and press **Load example** explicitly. Loading
only fills the matching maintained workflow and refreshes the braid preview;
it does not start an expensive calculation.

在 **Curated examples** 面板中按类别或关键字筛选，查看状态与来源，然后明确点击 **Load example**。加载只会填充相应工作流并刷新辫子预览，不会自动启动昂贵计算。

Status words are intentional:

- **formal** — a maintained project branch with frozen conventions and
  regression/external evidence;
- **candidate** — useful maintained research output whose normalization is not
  promoted to a final literature identification (the sl2 spin-1 branch);
- **diagnostic** — an audit or demonstration, not an invariant claim;
- **negative control** — an intentionally failing or boundary example.

状态词有明确含义：

- **formal**——约定、回归和外部证据已经冻结的维护分支；
- **candidate**——仍在研究中的输出，未提升为最终文献标识（sl2 spin-1 分支）；
- **diagnostic**——审计或演示，不代表不变量声明；
- **negative control**——有意展示失败或边界的示例。

## Braid input and preview / 辫子输入与预览

The project-native convention is **`+i = sigma_i` and `-i = sigma_i^-1`**.
Generator order and strand numbering are preserved exactly. The preview shows
writhe, strand count, generator sequence, and final permutation. Use the mouse
wheel to zoom, drag to pan, and **Fit** to restore the complete diagram.

项目原生约定是 **`+i = sigma_i`、`-i = sigma_i^-1`**。生成元顺序和股线编号严格保留。预览显示 writhe、股线数、生成元序列和最终置换；滚轮缩放、拖动平移，点击 **Fit** 恢复完整视图。

The diagram distinguishes over/under crossings for positive and negative
generators. SVG and PNG preview exports are available from the preview controls
and the **File → Export** menu.

图形会正确区分正、负生成元的上下穿越。预览控件以及 **File → Export** 菜单都可导出 SVG 和 PNG。

## Built-in invariant workflow / 内置不变量工作流

The invariant tab has two pages. On **Braid setup / preview**, choose
**Built-in example** or **Manual braid input** from Input mode. For a manual
braid, enter the strand count and signed generators; the large diagram updates
without calculating. The input and preview areas can be resized by dragging
their divider. On **Calculation / results**, select branches from the
scrollable checklist, read the selected branch details beside it, enter `q`,
and press **Calculate**. The control and result areas are also resizable.

不变量标签页分成两页。在 **Braid setup / preview** 中，通过 Input mode 选择
**Built-in example** 或 **Manual braid input**。手动输入时填写股线数和带符号的
生成元；大幅预览图会更新，但不会自动计算。拖动分隔线可调整输入区和预览区大小。
在 **Calculation / results** 中，从可滚动的列表勾选分支，在旁边阅读分支详情，
输入 `q` 后点击 **Calculate**。控制区与结果区同样可以调整大小。

Choose one or more branch checkboxes. The service-owned explanation identifies
representation dimension, tensor channels, enhanced trace, normalization, and
the active variable convention. Formal and candidate labels remain visible in
the result tabs. `q` accepts exact values such as `2` and `3/2`, or symbolic
expressions such as `q`.

选择一个或多个分支复选框。service 说明会列出表示维数、张量通道、增强迹、归一化和变量约定。结果标签会保留 formal/candidate 标记。`q` 支持 `2`、`3/2` 等精确值和 `q` 等符号表达式。

Calculation runs outside the Qt UI thread. A result is not produced merely by
opening an example, explanation, or project file.

计算在 Qt UI 线程之外执行。打开示例、说明或项目文件不会自动产生结果。

## Custom R/check-R workflow / 自定义 R/check-R 工作流

Choose the input kind explicitly:

- raw `R` is converted by the maintained convention `check-R = P R`;
- direct `check-R` is used as the braid generator;
- negative generators use the inverse local check-R when it is invertible.

请明确选择输入类型：

- 原始 `R` 按维护中的约定转换为 `check-R = P R`；
- 直接输入的 `check-R` 作为辫子生成元使用；
- 可逆时，负生成元使用局部 check-R 的逆。

Structural validity, check-R braid-relation status, and raw-R Yang–Baxter status
are separate facts. A verified braid relation still means **operator evidence**
only; no arbitrary matrix is automatically a knot/link invariant. Enhancement,
weighted trace, Markov normalization, and framing data would be needed for that
claim.

结构有效性、check-R 辫子关系状态和原始 R 的 Yang–Baxter 状态彼此独立。即使辫子关系验证通过，也只代表**算子证据**；任意矩阵都不会自动成为结/链不变量。要作出不变量声明还需要增强结构、加权迹、Markov 归一化和 framing 数据。

## Projects and exports / 项目与导出

Use **File → Save Project** or **Save Project As…** to write deterministic,
UTF-8 `.knotcalc.json` setup state. **File → Open Project…** restores the
appropriate workflow without trusting stored results or evaluating anything.

使用 **File → Save Project** 或 **Save Project As…** 保存确定性的 UTF-8 `.knotcalc.json` 设置状态。**File → Open Project…** 会恢复相应工作流，不会信任文件中的结果或自动计算。

The **File → Export** submenu enables only applicable actions:

- invariant result as text or JSON;
- custom operator result as JSON;
- current braid preview as SVG or PNG.

**File → Export** 子菜单只启用当前可用的操作：

- 不变量结果文本或 JSON；
- 自定义算子 JSON；
- 当前辫子预览 SVG 或 PNG。

The export formats use the maintained service serializers. Project files are
setup documents, not serialized Python objects.

导出格式使用维护中的 service 序列化器。项目文件只保存设置，不是序列化的 Python 对象。

## Common errors / 常见错误

- Select a branch before calculating.
- Enter valid integers in the generator field; `0` and out-of-range indices
  are rejected.
- Select `R` or `check-R` before custom validation; the application never
  guesses the convention.
- A failed relation check is diagnostic evidence, not a reason to relabel the
  matrix as an invariant.
- Very large tensor dimensions may be expensive; the workflow displays a
  growth warning before construction.

- 计算前请至少选择一个分支。
- 生成元必须是合法整数；`0` 和超出范围的编号会被拒绝。
- 自定义验证前必须选择 `R` 或 `check-R`；程序不会猜测约定。
- 关系验证失败是诊断证据，不会把矩阵改称为不变量。
- 很大的张量维数可能非常昂贵；工作流会在构造前显示增长警告。

## Full mathematics and uninstall / 完整数学说明与卸载

Help includes the bundled **Mathematical Implementation** guide. It records
the braid order, tensor basis, `R`/`check-R`, q, trace, framing, and branch
normalization conventions. The public repository also contains
`docs/MATH_CONVENTIONS.md` and `docs/EXTERNAL_VALIDATION.md`.

帮助菜单包含离线的 **Mathematical Implementation** 指南，其中记录辫子顺序、张量基、`R`/`check-R`、q、迹、framing 和分支归一化约定。仓库还提供 `docs/MATH_CONVENTIONS.md` 与 `docs/EXTERNAL_VALIDATION.md`。

For the installer, uninstall from Windows Settings → Apps → Installed apps.
The per-user installer does not require administrator elevation. Portable users
can close the application and delete the extracted folder.

安装版请在 Windows“设置 → 应用 → 已安装的应用”中卸载，无需管理员权限。便携版退出程序后直接删除解压目录即可。
