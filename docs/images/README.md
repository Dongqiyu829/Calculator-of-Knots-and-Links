# Maintained application screenshots

README screenshots must come from the real maintained PySide6 application. Do
not draw mockups or edit images to imply functionality that is not present.

From the repository root, after installing the desktop dependencies, refresh
the captures with:

```powershell
python tools/capture_desktop_screenshots.py --output-dir docs/images
```

On a Linux CI/maintainer desktop without a display, use the Qt offscreen
platform:

```bash
QT_QPA_PLATFORM=offscreen python tools/capture_desktop_screenshots.py --output-dir docs/images
```

The script instantiates `src.desktop.main_window.DesktopMainWindow`, loads the
maintained trefoil and sl2 fundamental check-R examples, and captures the
actual invariant/custom workflows plus the contextual explanation dock. It
does not evaluate an invariant or a custom operator. Review captures on the
target Windows build before linking them from public documentation.
