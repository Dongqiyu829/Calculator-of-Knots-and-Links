# Windows distribution

Issue #38 extends the verified PyInstaller `onedir` path with a per-user Inno
Setup 6 installer. PySide6 and SymPy have a large runtime footprint, so the
folder-style bundle remains the packaged source for both the installer and the
portable ZIP; no fragile `onefile` build is introduced.

The maintained application version is `0.1.3`, sourced only from
`src/version.py`. The `v0.1.3` tag and GitHub Release are published; the
tag-driven Windows workflow successfully built, smoke-tested, and uploaded
the installer, portable ZIP, and checksum manifest.

## Local build

Use Python 3.12 or newer on Windows. Install Inno Setup 6 (the standard
per-user compiler) and run the maintained orchestration script:

```powershell
python -m pip install -e ".[test,desktop,build]"
choco install innosetup --no-progress -y
.\packaging\windows\build.ps1 -Python python
```

The script runs the fast regression selection, builds
`packaging/Calculator-of-Knots-and-Links.spec`, smoke-tests the packaged and
extracted portable executables with `--smoke-test` and `--version`, compiles
`packaging/windows/installer.iss`, verifies all expected candidate files, and
writes these assets under
`artifacts\`:

- `Calculator-of-Knots-and-Links-Windows-x64-Setup.exe`
- `Calculator-of-Knots-and-Links-Windows-x64-Portable.zip`
- `SHA256SUMS.txt`

Use `-SkipInstaller` when only the PyInstaller/portable path is available
locally. CI runs the complete build and compile path; interactive install and
uninstall acceptance remains a clean-machine checklist because silent Inno
Setup UI automation is runner-sensitive.

## GitHub Actions artifact

`.github/workflows/windows-build.yml` runs on `windows-latest` with Python 3.12
and Inno Setup 6. It invokes the same checked-in build script, verifies all
three stable assets, and uploads them from the completed workflow's
**Summary → Artifacts** section. The portable archive should be extracted as a
folder; do not move only the `.exe` out of its bundled directory.

## Release workflow

`.github/workflows/release.yml` is tag-driven. A future `vX.Y.Z` push validates
that the tag exactly matches `src.version.__version__`, runs the shared build
and installer checks, and publishes these exact stable assets:

- `Calculator-of-Knots-and-Links-Windows-x64-Setup.exe`
- `Calculator-of-Knots-and-Links-Windows-x64-Portable.zip`
- `SHA256SUMS.txt`

The manual `workflow_dispatch` path requires a tag input, performs the same
non-publishing build/checksum/smoke path, and uploads the same three files as
temporary Actions artifacts. No private secrets are needed; a real tag push
uses GitHub's provided token. Stable names intentionally match the README's
`releases/latest/download/...` links.

## Clean-machine acceptance checklist

- [ ] On a clean Windows machine, download the `v0.1.3` installer and `SHA256SUMS.txt`; independently verify the installer hash.
- [ ] Install without administrator elevation into the default `%LOCALAPPDATA%\Programs` location.
- [ ] Launch from the Start Menu; optionally verify the desktop shortcut.
- [ ] Open the invariant tab and confirm that the braid preview renders.
- [ ] Verify preview zoom, pan, and fit controls.
- [ ] Load a curated example and confirm that loading does not evaluate automatically.
- [ ] Open both the built-in invariant and Custom R/check-R application tabs.
- [ ] Run one cheap built-in invariant calculation.
- [ ] Save and reopen a `.knotcalc.json` project.
- [ ] Confirm the Mathematics / How it works panel updates with the workflow.
- [ ] Open the offline bilingual User Guide from Help.
- [ ] Load the custom R/check-R example and inspect its operator-only status.
- [ ] Export the braid preview as SVG and PNG.
- [ ] Export a result as JSON/text where applicable.
- [ ] Close and relaunch the application.
- [ ] Uninstall from Windows Settings and verify the per-user application directory is removed.
- [ ] Extract the portable ZIP, run `--version`, and run the packaged smoke check.

The unsigned binary may receive the normal Windows SmartScreen warning. Code
signing is not currently enabled; `v0.1.3` is the published stable release.

## Scope and caveats

- The installer is Inno Setup 6, per-user (`PrivilegesRequired=lowest`), with
  no PATH modification or administrator elevation.
- The bundle contains the maintained PySide6 application and runtime
  dependencies; it does not intentionally package development/test files or
  the historical Tkinter frontends.
- The onedir bundle also includes the offline `docs/USER_GUIDE.md` and
  `docs/MATHEMATICAL_IMPLEMENTATION.md` resources used by the Help menu.
- The build does not alter braid, R-matrix, q, trace, framing, normalization,
  branch-status, regression-fixture, or Knot Atlas behavior.
