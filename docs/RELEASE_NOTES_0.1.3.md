# Calculator of Knots and Links v0.1.3

Published as [v0.1.3](https://github.com/Dongqiyu829/Calculator-of-Knots-and-Links/releases/tag/v0.1.3).

## English

This release brings the already-merged M6 usability and performance work to
the Windows desktop build:

- The braid preview follows continuous physical strands. A visible underpass
  gap is now local to its crossing, in both the Qt view and SVG export.
- Invariant results offer Compact and Detailed views. Compact is the default;
  it presents exact symbolic standard Jones-variable and Atlas-comparable
  relabelings only where the maintained conversion is unambiguous. Numeric
  `q` results remain scalar-only, and spin-1 remains explicitly candidate.
- Built-in symbolic evaluation avoids repeated local research diagnostics.
  The validated diagnostic builders remain available, and exact primary
  outputs are unchanged. Benchmarks and the follow-up backend design are in
  [Performance](PERFORMANCE.md).

No mathematical conventions, R/check-R matrices, braid signs or order,
normalization, formal/candidate status, oracle fixtures, or deterministic
exports change in this release. The installer and portable ZIP retain their
stable Windows asset names.

## 中文

本次版本将已合并的 M6 易用性与性能改进带入 Windows 桌面程序：

- 辫子预览按连续的实际股线绘制；下穿处的可见间隙仅出现在对应交叉附近，
  Qt 视图与 SVG 导出保持一致。
- 不变量结果提供“简洁 / 详细”两种视图，默认使用简洁视图。仅当现有
  变量替换能够无歧义地作精确 Laurent 重标记时，才显示符号 Jones 标准变量
  及可与 Knot Atlas 对照的形式。数值 `q` 仍只显示标量结果；spin-1 分支
  仍明确标为候选。
- 内置符号计算避免重复运行局部研究诊断；完整验证构造仍可使用，精确
  主输出不变。测量结果与后续后端设计见 [性能文档](PERFORMANCE.md)。

本次发布不改变数学约定、R/check-R 矩阵、辫子符号或顺序、归一化、正式 / 候选
状态、外部参照数据或确定性导出。Windows 安装版与便携版继续使用稳定的文件名。
