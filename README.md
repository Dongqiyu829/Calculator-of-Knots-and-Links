# Calculator of Knots and Links

Calculator of Knots and Links is a research-oriented knot/link invariant calculator with a maintained PySide6 desktop frontend, a reusable Python/SymPy service boundary, and preserved historical benchmark/reference code.

The project prioritizes mathematical correctness, reproducibility, and explicit convention handling over UI polish.

## Download Windows App / 下载 Windows 应用

### 🌟 Download Windows Installer / 下载 Windows 安装版

[![Download Windows Installer](https://img.shields.io/badge/Download%20Windows%20Installer-Calculator%20of%20Knots%20and%20Links-2563eb?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/Dongqiyu829/Calculator-of-Knots-and-Links/releases/latest/download/Calculator-of-Knots-and-Links-Windows-x64-Setup.exe)

[Download Windows Installer / 下载 Windows 安装版](https://github.com/Dongqiyu829/Calculator-of-Knots-and-Links/releases/latest/download/Calculator-of-Knots-and-Links-Windows-x64-Setup.exe)

**Windows 10/11 x64.** No Python, Conda, Git, or compiler is required. Ordinary users should use the installer.

**Windows 10/11 x64。** 无需 Python、Conda、Git 或编译器。普通用户请优先使用安装版。

- Portable ZIP / 便携版 ZIP: [Download Portable ZIP / 下载便携版 ZIP](https://github.com/Dongqiyu829/Calculator-of-Knots-and-Links/releases/latest/download/Calculator-of-Knots-and-Links-Windows-x64-Portable.zip)
- SHA-256 checksum / SHA-256 校验和: [SHA256SUMS.txt](https://github.com/Dongqiyu829/Calculator-of-Knots-and-Links/releases/latest/download/SHA256SUMS.txt)
- Latest Release / 最新发布: [View Latest Release / 查看最新发布](https://github.com/Dongqiyu829/Calculator-of-Knots-and-Links/releases/latest)

The installer is unsigned, so Windows SmartScreen may show its usual warning for a new download. Verify the checksum when required.

安装程序未进行代码签名，因此 Windows SmartScreen 可能对新下载显示常规提示；需要时请核对校验和。

**Release state / 发布状态:** **v0.1.2 is the latest published release.** The
stable `releases/latest/download/...` links above resolve to its Windows
installer, portable ZIP, and checksum assets.

**发布状态：****v0.1.2 已正式发布并且是当前最新版本。** 上面的稳定
`releases/latest/download/...` 链接会直接指向 v0.1.2 的 Windows 安装版、
便携版 ZIP 和校验文件。

**Install / 安装:** run the installer, keep the per-user default location, and launch from the Start Menu (an optional desktop shortcut is available). No administrator elevation or PATH change is needed.

**安装说明：** 运行安装程序，保留默认的当前用户安装位置，然后从开始菜单启动（可选创建桌面快捷方式）。无需管理员权限，也不会修改 PATH。

## Screenshots and demo / 截图与演示

Public screenshots are refreshed from the real maintained PySide6 application;
the repository does not use fabricated mockups. Maintainers can reproduce the
captures after installing the desktop dependencies with:

```powershell
python tools/capture_desktop_screenshots.py --output-dir docs/images
```

On a headless Linux maintainer machine, set `QT_QPA_PLATFORM=offscreen` before
running the same command. The script loads the maintained trefoil and custom
sl2 check-R examples, captures the actual workflow and explanation dock, and
does not evaluate an invariant. Review the resulting `docs/images/*.png` files
on Windows before publishing them. See [the screenshot refresh notes](docs/images/README.md).

公共截图由真实维护中的 PySide6 应用刷新，不使用虚构的界面模型。安装桌面依赖后，维护者可运行上面的命令生成截图；脚本只加载维护中的示例，不会计算不变量。发布前请在 Windows 上检查生成的 `docs/images/*.png`。

## Current status

The historical source recovery, package/test baseline, service-layer refactor, and the core M3 desktop workflow are complete.

The repository now contains:

- the recovered braid, algebra, R-matrix, invariant, benchmark, Tkinter/workbench, and catalog code;
- a maintained PySide6 desktop application;
- frontend-neutral application services and result DTOs;
- a convention-explicit custom R/check-R braid-operator engine;
- representative regression fixtures from the authoritative recovered implementation;
- an offline external Knot Atlas oracle suite for independent mathematical validation.

M4 distribution is complete. The supported Windows release provides a reproducible
PyInstaller `onedir` application, a per-user Inno Setup installer, a portable ZIP,
and SHA-256 checksums. **v0.1.2 is published and is the current stable release.**

## Desktop application

Install the desktop dependencies and launch the maintained application with:

```bash
python -m pip install -e ".[desktop]"
python -m src.desktop
```

The desktop application does not evaluate invariants on startup. Expensive invariant and custom-matrix operations run only on request and are dispatched outside the Qt UI thread.

Query the maintained version without starting Qt:

```bash
python -m src.desktop --version
```

### Built-in invariant workflow

The primary desktop tab supports both catalog examples and project-native custom braids.
Its **Braid setup / preview** page offers an explicit **Manual braid input** mode
and a large resizable diagram. **Calculation / results** keeps a scrollable
branch checklist, separate branch details, and result tabs. The curated example
and Mathematics panels open from **View** and share a side dock area.

Users can:

- choose a built-in knot/link/braid example;
- enter a custom braid by strand count and signed Artin generators;
- select one or more available invariant branches;
- enter exact or symbolic q values such as `2`, `3/2`, or `q`;
- run calculations in a background Qt worker;
- inspect formal/candidate status, normalization, variable convention, representation metadata, notes, and warnings;
- copy selected or complete text results;
- copy deterministic JSON;
- export results to JSON or text.

Current built-in branches are:

- `sl2_fundamental` — Jones-compatible, **formal**;
- `sl3_fundamental` — A2/sl3 fundamental, **formal**;
- `sl2_spin1` / workbench model `sl2_3d_9x9` — 3-dimensional spin-1 branch, **candidate**.

The candidate branch remains explicitly labelled as such and is not presented as having a fully resolved external normalization.

### Curated examples and project files

The desktop window includes a searchable curated example browser. Examples are
evidence-backed presets for knots/links, braid-sign demonstrations, and custom
R/check-R diagnostics. Their status and provenance remain visible; selecting
**Load example** only populates the matching workflow and refreshes its braid
preview—it never starts an expensive calculation.

Use **File → Save Project** or **Save Project As…** to write a deterministic,
UTF-8 `.knotcalc.json` setup document. **Open Project…** restores either the
invariant or custom R/check-R tab without trusting or evaluating a stored
result. The format is versioned (`schema_version: 1`) and keeps symbolic q
and matrix input as text.

### Custom R / check-R workflow

The advanced desktop tab accepts user-supplied local matrices and constructs braid-group operators.

Supported features include:

- paste matrix text or load simple text/JSON contents;
- explicitly choose whether the input is raw `R` or `check-R`;
- convert raw `R` using the documented convention `check-R = P R`;
- infer or validate the local dimension `d`;
- check matrix shape and tensor-square compatibility;
- inspect invertibility;
- optionally test the check-R braid relation;
- optionally test the standard raw-R Yang-Baxter equation;
- distinguish relation status as verified, failed, not checked, or undecidable;
- enter arbitrary signed braid words;
- use the inverse local operator for negative generators;
- construct the full `d^n x d^n` braid operator;
- inspect ordered generator diagnostics and tensor-growth warnings;
- copy/export deterministic JSON.

This workflow constructs braid operators only. An arbitrary R-matrix is **not** automatically treated as a knot/link invariant recipe: quantum trace/enhancement, Markov normalization, framing, and related data are separate mathematical structure.

## Mathematical implementation

For the full mathematical derivation and code map—from braid words and representation bases through raw \(R\), \(\check R = PR\), Yang-Baxter validation, tensor embedding, enhanced traces, branch normalization, worked trefoil/figure-eight examples, and the custom R-matrix extension—see:

- [Mathematical Implementation Guide](docs/MATHEMATICAL_IMPLEMENTATION.md)

The guide is intended for both human readers and AI coding agents. Exact convention records remain in `docs/MATH_CONVENTIONS.md`, while independent external checks remain in `docs/EXTERNAL_VALIDATION.md`.

## Mathematical validation

The project keeps internal compatibility regression data separate from independent external validation.

Representative recovered outputs are frozen in:

- `tests/fixtures/representative_invariant_regressions.json`

External validation is documented in:

- `docs/EXTERNAL_VALIDATION.md`
- `tests/fixtures/knot_atlas_oracles.json`

The Knot Atlas suite currently includes `3_1`, `4_1`, `5_1`, `5_2`, and `6_1`.

Current calibrated external correspondences include:

- Knot Atlas braid generators map to project generators by a global sign reversal across the calibration set;
- Jones/sl2 fundamental uses the documented variable correspondence `q_atlas = q_project^2`;
- sl3/A2 fundamental uses `q_atlas = q_project^-1`;
- the spin-1/A1 weight-2 comparison remains diagnostic/candidate rather than being forced to match.

The custom check-R engine is also parity-tested against the built-in sl2 fundamental braid operator on representative braids, including symbolic coverage.

Measured built-in evaluation baselines, the non-CI profiling command, and
future backend designs are recorded in [Performance](docs/PERFORMANCE.md).

## Repository contents

- `src/` — mathematical engine, services, maintained PySide6 desktop application, recovered Tkinter/workbench code
- `examples/` — historical CLI/demo/GUI entry scripts
- `data/` — historical benchmark registries
- `tests/` — unit, regression, architecture, GUI-smoke, external-oracle, and compatibility tests
- `docs/` — project state, API contract, mathematical conventions, validation and recovery documentation
- `archive/report_bundle.zip` — original snapshot retained as provenance
- `CITATION.cff` — citation metadata

## Development setup

Install the package and test dependencies with:

```bash
python -m pip install -e ".[test]"
```

Install both test and desktop dependencies as needed for development.

Test tiers, CI behavior, and headless GUI instructions are documented in `docs/TESTING.md`.

Important project documents:

- `AGENTS.md` — development and agent rules
- `docs/PROJECT_STATE.md` — current project state
- `docs/TASKS.md` — prioritized task queue
- `docs/APPLICATION_API.md` — supported frontend-neutral application API
- `docs/MATHEMATICAL_IMPLEMENTATION.md` — complete end-to-end mathematical implementation guide
- `docs/MATH_CONVENTIONS.md` — established braid/R-matrix/q/trace conventions
- `docs/CUSTOM_RMATRIX_ENGINE.md` — custom R/check-R operator contract
- `docs/EXTERNAL_VALIDATION.md` — independent Knot Atlas validation
- `docs/REPRESENTATIVE_REGRESSIONS.md` — recovered compatibility baselines
- `docs/AUTHORITATIVE_RECOVERY.md` — source-recovery provenance
- `docs/DISTRIBUTION.md` — Windows standalone build and artifact instructions

## Distribution status

The first Windows standalone distribution path uses a PyInstaller `onedir` bundle. On Windows:

```powershell
python -m pip install -e ".[desktop,build]"
python -m PyInstaller --clean --noconfirm packaging/Calculator-of-Knots-and-Links.spec
```

The executable is produced under `dist\\Calculator-of-Knots-and-Links\\`. A packaging-only `--smoke-test` mode constructs the maintained PySide6 window, verifies bundled runtime imports, and exits without entering the normal event loop or evaluating an invariant.

The Windows GitHub Actions workflow builds the bundle, smoke-tests the packaged executable, creates `Calculator-of-Knots-and-Links-windows-x64.zip`, extracts that ZIP, smoke-tests the extracted executable again, and only then uploads it as an Actions artifact.

See `docs/DISTRIBUTION.md` for exact local-build, release, and artifact-download
instructions. CI builds both the portable ZIP and the Inno Setup installer.
Manual workflow dispatch remains available as a non-publishing validation path
for future releases. See the [v0.1.2 release notes](docs/RELEASE_NOTES_0.1.2.md).

## Development principle

Mathematical correctness comes first. Refactors must preserve validated braid, R-matrix, tensor-ordering, q, trace, framing, eigenvalue, and polynomial conventions unless a change is explicitly documented, independently justified, and regression-tested.

## Citation

If you use this repository in academic work, please cite the software repository using the metadata in `CITATION.cff`.

GitHub can export citation formats through the repository's **Cite this repository** feature.

## Author

Qiyu Dong
