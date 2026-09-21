# Autopilot Workflow

This repository is intended to support an agent-driven development workflow with minimal owner intervention.

## Goal

The owner should only need to intervene for genuine product or mathematical decisions. Routine recovery, testing, refactoring, packaging, documentation, CI fixes, and small implementation choices should proceed without repeatedly asking the owner for confirmation.

## Source of truth

Agents must use, in order:

1. `AGENTS.md`
2. `docs/PROJECT_STATE.md`
3. `docs/TASKS.md`
4. `docs/MATH_CONVENTIONS.md`
5. Open GitHub issues and pull requests
6. Tests and archived compatibility fixtures

Private chat history is not authoritative.

## Autonomous loop

When operating in autopilot mode:

1. Read the current project state and task queue.
2. Select the highest-priority unblocked task.
3. Create a focused branch.
4. Implement the task.
5. Run all relevant tests.
6. Update state/task/convention documentation when facts changed.
7. Open a PR with evidence and remaining risks.
8. Address CI failures and review findings.
9. After the PR is accepted, continue with the next highest-priority unblocked task.

## Continue automatically when

Agents may proceed without owner confirmation for:

- repository cleanup and normalization
- test coverage
- documentation
- CI configuration
- packaging scaffolding
- dependency metadata
- mechanical refactors with preserved behavior
- GUI implementation that follows already documented product requirements
- bug fixes where expected behavior is established by tests/specification
- performance improvements that preserve mathematical outputs

## Stop and escalate when

Agents MUST stop rather than guess when any of the following occurs:

- two plausible mathematical conventions produce different results
- archived outputs conflict with authoritative source
- a change would alter knot/link invariant normalization
- R-matrix, braid orientation, framing, trace, tensor ordering, or q convention is ambiguous
- authoritative historical source is unavailable and reimplementation would require choosing conventions
- licensing/ownership is unclear
- secrets, credentials, paid services, or external accounts are required
- data loss or deletion of archival evidence is proposed
- a major product direction is not already documented

When blocked, update `docs/PROJECT_STATE.md` and create or update a GitHub issue describing:
- what is known
- what was tried
- the exact decision required
- safe options

## Merge policy

A change is eligible to merge only when:

- relevant tests pass
- no known regression is hidden or waived
- mathematical behavior changes are explicitly documented
- state/task docs are current
- the PR explains evidence, risks, and follow-up work

For mathematical-core changes, archived-output compatibility tests are necessary but not sufficient; source-level convention evidence must also agree.

## Current bootstrap blocker

The authoritative historical source currently lives on the owner's Windows machine at:

`C:\cpp\comp2012\Quantum Group Knot`

The first autonomous recovery task is to import that source into a dedicated recovery branch without redesigning it. Once the authoritative source is in GitHub, future work should be GitHub-native and should not depend on the owner's local machine.
