# Calculator of Knots and Links v0.1.4

Release tag: `v0.1.4`.

## English

v0.1.4 brings the post-v0.1.3 performance backends and desktop integration into
one user-facing Windows release.

- The built-in invariant desktop workflow now defaults to the exact
  **Fast scalar** matrix-free EYB backend. The explicit global-matrix path
  remains available as **Reference / diagnostics**, and the public service API
  keeps `explicit` as its backward-compatible default.
- An exact **Temperley–Lieb** backend is available for sl2-fundamental Jones
  calculations only. It is calibrated from this project's existing check-R,
  trace, writhe, and unknot conventions and is never applied to sl3 or spin-1.
- Scalar backends preserve the established primary invariant output while
  truthfully omitting ordinary raw trace/full-operator diagnostics.
- The desktop result-worker callback path is marshalled back to the Qt GUI
  thread through bound slots, fixing the Windows responsiveness regression
  found during packaged user testing.
- The **Custom R/check-R operator** workflow now uses the same two-page,
  resizable desktop structure as the invariant workflow: setup/preview on one
  page and validation/operator results on another.
- Matrix-free, explicit, and Temperley–Lieb parity tests, Knot Atlas checks,
  Windows packaging checks, and packaged smoke tests remain green.

No mathematical convention, R/check-R matrix, braid sign/order, q convention,
trace/framing normalization, formal/candidate status, oracle fixture, project
schema, or deterministic result meaning changes in this release.

## 中文

v0.1.4 将 v0.1.3 之后完成的性能后端与桌面集成正式合并为一个面向用户的
Windows 版本。

- 内置不变量桌面工作流默认使用精确的 **Fast scalar** 无全局矩阵 EYB 后端；
  显式全局矩阵路径继续作为 **Reference / diagnostics** 保留，公共 service API
  的默认值仍是兼容旧调用者的 `explicit`。
- sl2 基本表示的 Jones 计算新增精确 **Temperley–Lieb** 后端。其生成元、闭合迹、
  writhe 与 unknot 归一化均从本项目既有约定校准，不会用于 sl3 或 spin-1。
- 标量后端保持既有主要不变量输出，但不会伪造普通 raw trace 或完整算子诊断。
- 桌面计算完成后的回调现在通过绑定的 Qt slot 回到 GUI 主线程，修复了真实
  Windows 打包版测试中发现的“未响应”问题。
- **Custom R/check-R operator** 工作流改为与不变量工作流一致的双页可调整布局：
  一页负责矩阵/辫子设置与预览，另一页负责验证与算子结果。
- matrix-free、explicit、Temperley–Lieb 的精确一致性测试、Knot Atlas 校验、
  Windows 打包检查和 packaged smoke tests 继续通过。

本次发布不改变数学约定、R/check-R 矩阵、辫子符号/顺序、q 约定、迹或 framing
归一化、formal/candidate 状态、oracle 数据、项目 schema 或确定性结果含义。
