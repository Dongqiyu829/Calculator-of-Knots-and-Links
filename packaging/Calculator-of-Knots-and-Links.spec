# PyInstaller onedir configuration for the maintained PySide6 application.
# Build from the repository root with:
#   python -m PyInstaller --clean --noconfirm packaging/Calculator-of-Knots-and-Links.spec

from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules


project_root = Path(SPECPATH).resolve().parent
# SymPy loads parser/printing modules dynamically. Include its runtime modules,
# while deliberately excluding SymPy's development and test trees.
hiddenimports = [
    name
    for name in collect_submodules("sympy")
    if not any(
        part in {"tests", "testing"} or part.startswith("test") or part.startswith("_test")
        for part in name.split(".")
    )
]

analysis = Analysis(
    [str(project_root / "packaging" / "desktop_entry.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=[],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # Only the maintained PySide6 frontend belongs in the frozen bundle. Some
    # development environments also have PyQt bindings installed, and
    # PyInstaller rejects collecting multiple Qt bindings in one application.
    excludes=["tkinter", "pytest", "PyQt5", "PyQt6", "PySide2"],
    noarchive=False,
)

pyz = PYZ(analysis.pure)

executable = EXE(
    pyz,
    analysis.scripts,
    analysis.binaries,
    analysis.datas,
    [],
    name="Calculator-of-Knots-and-Links",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
)

COLLECT(
    executable,
    analysis.binaries,
    analysis.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="Calculator-of-Knots-and-Links",
)
