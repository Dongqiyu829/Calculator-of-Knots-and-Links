"""Public entrypoints for the ordinary braid workbench GUI."""

from __future__ import annotations

import argparse

from src.catalog.braid_examples import get_braid_example
from src.gui.braid_workbench_app import (
    BraidWorkbenchApp,
    WORKBENCH_DEFAULT_Q_TEXT,
    evaluate_single_workbench_braid,
    get_workbench_example_labels,
    launch_braid_workbench_gui,
    parse_workbench_q_parameter,
)
from src.workbench.comparison import evaluate_workbench_pair


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Launch or inspect the ordinary braid workbench GUI entrypoint.")
    parser.add_argument("--list", action="store_true", help="List the built-in braid examples available in the workbench.")
    parser.add_argument("--compare", nargs=2, metavar=("BRAID_A", "BRAID_B"), help="Compare two built-in examples in CLI mode.")
    parser.add_argument("--q", default=WORKBENCH_DEFAULT_Q_TEXT, help="Value used for q in CLI comparison mode. Default: 2")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)

    if args.list:
        for label in get_workbench_example_labels():
            print(label)
        return 0

    if args.compare:
        q_parameter = parse_workbench_q_parameter(args.q)
        left = get_braid_example(args.compare[0]).to_braid_word()
        right = get_braid_example(args.compare[1]).to_braid_word()
        print(evaluate_workbench_pair(left, right, q=q_parameter).summary())
        return 0

    launch_braid_workbench_gui()
    return 0


__all__ = [
    "BraidWorkbenchApp",
    "WORKBENCH_DEFAULT_Q_TEXT",
    "evaluate_single_workbench_braid",
    "get_workbench_example_labels",
    "launch_braid_workbench_gui",
    "main",
    "parse_workbench_q_parameter",
]


if __name__ == "__main__":
    raise SystemExit(main())
