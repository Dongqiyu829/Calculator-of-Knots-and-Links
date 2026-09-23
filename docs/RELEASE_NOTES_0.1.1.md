# Calculator of Knots and Links v0.1.1

> `v0.1.1` was published on 2026-09-23 as the current stable Windows release.

## English

This maintenance release packages the completed M5 productization work:

- a redesigned Qt-native braid visualization with deterministic geometry,
  zoom/pan/fit, and SVG/PNG export;
- curated examples with provenance and explicit formal/candidate/diagnostic
  status metadata;
- deterministic `.knotcalc.json` project save/load that never evaluates on load;
- a frontend-neutral Mathematics / How it works explanation panel;
- unified File → Export routes for maintained result and operator serializers;
- a bilingual offline User Guide bundled with the Windows application.

The mathematical boundaries are unchanged. In particular:

- sl2 fundamental remains the formal Jones-compatible branch;
- sl3 fundamental remains the formal P3/A2-style branch;
- sl2 spin-1 remains a candidate branch and is not promoted to a final
  literature identification;
- custom raw `R`/`check-R` workflows remain operator-only unless an explicit
  enhancement recipe exists.

The project-native Artin signs, generator order, tensor ordering, q variables,
trace/framing conventions, fixtures, and external-oracle mappings are unchanged.

## 中文

本维护版本打包了已完成的 M5 产品化工作：

- 全新维护的 Qt 原生辫子可视化，提供确定性几何、缩放/平移/适应窗口以及
  SVG/PNG 导出；
- 带来源和明确 formal/candidate/diagnostic 状态元数据的精选示例；
- 确定性的 `.knotcalc.json` 项目保存/加载，加载时不会自动计算；
- 前端无关的 Mathematics / How it works 数学说明面板；
- 统一的 File → Export 路由，复用维护中的结果和算子序列化器；
- 随 Windows 应用离线打包的双语用户指南。

数学边界保持不变：

- sl2 fundamental 仍是 formal、与 Jones 兼容的分支；
- sl3 fundamental 仍是 formal、P3/A2 风格的分支；
- sl2 spin-1 仍是 candidate 分支，不提升为最终文献标识；
- 自定义原始 `R`/`check-R` 工作流仍仅提供算子能力，除非存在明确的增强方案。

项目原生 Artin 符号、生成元顺序、张量顺序、q 变量、迹/framing 约定、回归
fixture 和外部 oracle 映射均未改变。
