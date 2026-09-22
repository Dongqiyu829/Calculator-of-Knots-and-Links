# Windows distribution

Issue #34 establishes the first standalone distribution path for the maintained
PySide6 application. It deliberately targets a PyInstaller `onedir` build:
PySide6 and SymPy have a large runtime footprint, and a folder-style bundle is
easier to inspect and more reliable than forcing a fragile `onefile` archive at
this stage.

The maintained application version is `0.1.0`. This PR adds and validates the
release machinery but intentionally does not create the `v0.1.0` tag or publish
the first public release.

## Local build

Use Python 3.12 or newer on Windows:

```powershell
python -m pip install -e ".[desktop,build]"
python -m PyInstaller --clean --noconfirm packaging/Calculator-of-Knots-and-Links.spec
```

The output directory is `dist\Calculator-of-Knots-and-Links\` and the
executable is `dist\Calculator-of-Knots-and-Links\Calculator-of-Knots-and-Links.exe`.
Run the packaging-only smoke check from that directory:

```powershell
dist\Calculator-of-Knots-and-Links\Calculator-of-Knots-and-Links.exe --smoke-test
```

The check constructs the maintained desktop window, exercises Qt resource and
runtime imports, and exits without entering an event loop or evaluating an
invariant. It is intentionally not a replacement for the application itself.

## GitHub Actions artifact

`.github/workflows/windows-build.yml` runs on `windows-latest` with Python 3.12.
It runs the fast regression selection before packaging, builds the checked-in
specification, creates the deterministic
`Calculator-of-Knots-and-Links-windows-x64.zip`, extracts the ZIP, and runs the
extracted executable with `--smoke-test`. Only after that verification does it
upload the ZIP as the workflow artifact. The workflow can be started manually
with `workflow_dispatch`, and also runs for pull requests and pushes to `main`.

Download the artifact from the completed workflow's **Summary → Artifacts**
section. Extract the ZIP as a folder and run the executable in place; do not
move only the `.exe` out of its bundled directory.

## Release workflow

`.github/workflows/release.yml` is tag-driven. A future `vX.Y.Z` push validates
that the tag exactly matches `src.version.__version__`, runs the fast tests and
both packaged smoke checks, creates the versioned ZIP and a companion
`Calculator-of-Knots-and-Links-X.Y.Z-windows-x64.zip.sha256`, and publishes both
files with the normal GitHub-provided token. Any mismatch fails before release
publication. A manual `workflow_dispatch` requires a tag input and performs the
same build/checksum/smoke path as a non-publishing dry run, uploading temporary
workflow artifacts instead.

The first supported release format is therefore a portable `onedir` ZIP. There
is no MSI/NSIS/Inno Setup installer or code signing yet. A future installer
should preserve the same extracted-folder behavior and be justified by a
reliability/user-installation need; Windows SmartScreen may warn for the
unsigned preview binary.

## Scope and caveats

- This is a standalone folder bundle, not an installer, MSI, NSIS package, or
  GitHub Release.
- The bundle contains the maintained PySide6 application and its runtime
  dependencies; it does not intentionally package development/test files or
  the historical Tkinter frontends.
- Windows Defender or corporate policy may inspect an unsigned local executable
  more slowly. Code signing is outside this issue.
- The build does not alter braid, R-matrix, q, trace, framing, normalization,
  branch-status, regression-fixture, or Knot Atlas behavior.
