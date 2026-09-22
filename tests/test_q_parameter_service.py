"""Exact q parsing at the public application-service boundary."""

from __future__ import annotations

import pytest
import sympy as sp

from src.services import QParameterParseError, parse_q_text


def test_q_text_preserves_exact_and_symbolic_inputs() -> None:
    assert parse_q_text("2") == sp.Integer(2)
    assert parse_q_text("3/2") == sp.Rational(3, 2)
    parameter = parse_q_text("q")
    assert str(parameter) == "q"
    assert parameter.is_nonzero is True


@pytest.mark.parametrize("text", ["", "   ", "["])
def test_q_text_errors_are_structured(text: str) -> None:
    with pytest.raises(QParameterParseError, match="q must"):
        parse_q_text(text)
