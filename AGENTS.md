# AGENTS.md

## Purpose

This repository is being converted from a research bundle into a maintainable, installable desktop application for knot and link calculations.

Agents working in this repository must treat the repository itself as the source of truth. Do not rely on private chat history.

Before making changes, read:

1. `AGENTS.md`
2. `docs/PROJECT_STATE.md`
3. `docs/TASKS.md`
4. Relevant tests and mathematical documentation

## Product direction

Initial target:

- Windows desktop application
- Local/offline execution
- No Python installation required for end users
- Mathematical core reusable independently of the GUI

Preferred stack unless evidence from the recovered source suggests otherwise:

- Python
- SymPy-compatible mathematical core
- PySide6 desktop UI
- pytest
- PyInstaller
- GitHub Actions

## Architecture rule

The mathematical core MUST remain independent of the GUI.

Allowed dependency direction:

`core -> services -> gui`

The core must not import PySide6 or other presentation frameworks.

## Mathematical correctness

Existing validated mathematical behaviour is part of the public contract.

Never silently change conventions involving:

- braid-generator orientation/sign
- tensor-factor ordering
- R-matrix normalization
- q conventions
- Markov trace normalization
- framing conventions
- eigenvalue ordering
- polynomial normalization

If a convention must change:

1. document it in `docs/MATH_CONVENTIONS.md`
2. add or update regression tests
3. call it out explicitly in the PR

Do not rewrite mathematically validated algorithms merely for style.

## Agent workflow

For every task:

1. Read project state and task queue.
2. Work on the highest-priority task whose dependencies are satisfied.
3. Prefer small, reviewable changes.
4. Preserve behaviour before refactoring.
5. Add tests for newly exposed behaviour.
6. Run the relevant test suite.
7. Update `docs/PROJECT_STATE.md` if the factual state changed.
8. Update `docs/TASKS.md` when a task is completed or materially re-scoped.
9. Open a PR instead of pushing broad refactors directly to `main`.

## PR requirements

Every PR should explain:

- What changed
- Why it changed
- Tests run
- Whether mathematical behaviour changed
- Remaining risks or follow-up work

## Definition of done

A task is complete only when:

- implementation works
- existing tests still pass
- new behaviour has tests when practical
- documentation matches reality
- application entry points still launch
- no mathematical convention changed silently


## Autopilot mode

This repository may be operated in autonomous agent mode.

When instructed to run autonomously, follow `docs/AUTOPILOT.md`. Continue through the highest-priority unblocked tasks without repeatedly asking the owner for routine implementation decisions.

Never use autonomy as permission to guess unresolved mathematical conventions. The stop/escalation rules in `docs/AUTOPILOT.md` are mandatory.
