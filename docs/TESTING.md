# Testing and CI Tiers

The recovered suite has three explicit tiers. Markers are assigned centrally in
`tests/conftest.py` so the authoritative historical test bodies are not
rewritten merely to organize automation.

## Installation

Use Python 3.12 or newer. From the repository root:

```bash
python -m pip install -e ".[test]"
```

Runtime dependency: `sympy`. Test dependency: `pytest`. Tkinter is supplied by
the Python standard library, but GUI tests need a usable Tk installation and a
display server. On Linux, use `xvfb-run -a` for GUI coverage.

## Tiers

| Tier | Command | Purpose |
| --- | --- | --- |
| Fast core regression | `python -m pytest -q -m "not slow and not gui"` | Archive integrity, registry, braid, R-matrix, invariant, and numerical regression checks suitable for pull requests. |
| GUI smoke | `xvfb-run -a python -m pytest -q -m gui` | Tkinter launch/workbench/preview and GUI-adjacent data-flow checks. |
| Extended mathematics | `xvfb-run -a python -m pytest -q -m slow` | Symbolic, multi-branch, and candidate-branch regressions that take materially longer. |
| Complete suite | `xvfb-run -a python -m pytest -q` | Every recovered and baseline test. |

The normal pull-request workflow runs the fast tier. The `Extended tests`
workflow preserves the complete suite for manual runs and the weekly main-branch
schedule; it does not delete or weaken slow coverage.

On the recovered Windows development environment, the tier runs measured about
2:42 for fast core (51 tests), 4:49 for GUI smoke (53 passed and one
environment-specific Tk skip), and 17:29 for extended mathematics (51 tests).
The GUI and slow sets intentionally overlap, so their union with fast core is
the complete 141-test suite.

## Historical recovery note

The authoritative source initially produced formatter, reference-catalog, and
Tk-environment discrepancies. The recovered implementation was not altered:
smoke assertions were aligned with its display/reference behavior, and tests
that truly require a Tk root skip only when Tk cannot initialize. The full
history and reproduction evidence remain in `docs/AUTHORITATIVE_RECOVERY.md`.
