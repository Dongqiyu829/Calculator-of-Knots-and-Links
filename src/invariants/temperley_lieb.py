"""Exact sl2-fundamental Jones scalar in a planar Temperley–Lieb basis.

The coefficients and closure rule are calibrated in ``docs/MATH_CONVENTIONS.md``
from this project's check-R and EYB data.  No tensor-space braid operator is
constructed here.  This module deliberately supports only the maintained sl2
fundamental branch, not sl3 or the spin-1 candidate.
"""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

from src.braid.braid_word import BraidWord


@dataclass(frozen=True, slots=True)
class TLDiagram:
    """A planar matching, top endpoints first and bottom endpoints second."""

    strands: int
    partner: tuple[int, ...]

    def __post_init__(self) -> None:
        if self.strands < 1 or len(self.partner) != 2 * self.strands:
            raise ValueError("TL diagram must have two endpoints per positive strand count")
        for index, mate in enumerate(self.partner):
            if mate < 0 or mate >= len(self.partner) or mate == index or self.partner[mate] != index:
                raise ValueError("TL diagram partner data must be a fixed-point-free matching")


class _Components:
    """Small disjoint-set structure for stacking and closing pairings."""

    def __init__(self, size: int) -> None:
        self.parent = list(range(size))

    def find(self, index: int) -> int:
        while self.parent[index] != index:
            self.parent[index] = self.parent[self.parent[index]]
            index = self.parent[index]
        return index

    def join(self, left: int, right: int) -> None:
        self.parent[self.find(left)] = self.find(right)


def identity_diagram(strands: int) -> TLDiagram:
    """Vertical-through identity in the project's left-to-right strand order."""

    if strands < 1:
        raise ValueError("TL diagrams require at least one strand")
    return TLDiagram(strands, tuple(range(strands, 2 * strands)) + tuple(range(strands)))


def generator_diagram(strands: int, index: int) -> TLDiagram:
    """Cup/cap E_i on the adjacent one-based Artin strand pair."""

    if index < 1 or index >= strands:
        raise ValueError("TL generator index must identify adjacent strands")
    partner = list(identity_diagram(strands).partner)
    left = index - 1
    right = index
    partner[left] = right
    partner[right] = left
    partner[strands + left] = strands + right
    partner[strands + right] = strands + left
    return TLDiagram(strands, tuple(partner))


def multiply_diagrams(left: TLDiagram, right: TLDiagram) -> tuple[TLDiagram, int]:
    """Stack left above right; return the surviving pairing and closed loops."""

    if left.strands != right.strands:
        raise ValueError("TL diagram factors must have the same strand count")
    strands = left.strands
    components = _Components(4 * strands)
    for diagram, offset in ((left, 0), (right, 2 * strands)):
        for endpoint, mate in enumerate(diagram.partner):
            if endpoint < mate:
                components.join(offset + endpoint, offset + mate)
    for index in range(strands):
        components.join(strands + index, 2 * strands + index)

    boundary: dict[int, list[int]] = {}
    for index in range(strands):
        boundary.setdefault(components.find(index), []).append(index)
        boundary.setdefault(components.find(3 * strands + index), []).append(strands + index)
    roots = {components.find(index) for index in range(4 * strands)}
    closed_loops = 0
    partner = [-1] * (2 * strands)
    for root in roots:
        endpoints = boundary.get(root, ())
        if not endpoints:
            closed_loops += 1
        elif len(endpoints) == 2:
            a, b = endpoints
            partner[a] = b
            partner[b] = a
        else:
            raise AssertionError("Stacked TL diagrams did not leave paired boundary endpoints")
    return TLDiagram(strands, tuple(partner)), closed_loops


def closure_loops(diagram: TLDiagram) -> int:
    """Count loops after joining corresponding top and bottom endpoints."""

    strands = diagram.strands
    components = _Components(2 * strands)
    for endpoint, mate in enumerate(diagram.partner):
        if endpoint < mate:
            components.join(endpoint, mate)
    for index in range(strands):
        components.join(index, strands + index)
    return len({components.find(index) for index in range(2 * strands)})


@dataclass(frozen=True, slots=True)
class TemperleyLiebScalarResult:
    """Exact closure data; intentionally no full operator or ordinary trace."""

    closure_trace: sp.Expr
    unreduced_expression: sp.Expr
    unknot_normalization: sp.Expr
    reduced_expression: sp.Expr
    basis_term_count: int


def evaluate_temperley_lieb_jones(braid_word: BraidWord, *, q: sp.Expr) -> TemperleyLiebScalarResult:
    """Evaluate the maintained reduced-P2/Jones-compatible sl2 scalar.

    Positive ``sigma_i`` maps to ``q I - E_i`` and inverse ``sigma_i^-1``
    to ``q^-1 I - E_i``.  Diagrams multiply in the input word order.  A
    closed diagram contributes ``(q+q^-1)**number_of_loops``.
    """

    strands = braid_word.num_strands
    delta = q + q**-1
    identity = identity_diagram(strands)
    generators = {abs(value): generator_diagram(strands, abs(value)) for value in braid_word.generators}
    coefficients: dict[TLDiagram, sp.Expr] = {identity: sp.Integer(1)}
    for signed_generator in braid_word.generators:
        e_diagram = generators[abs(signed_generator)]
        identity_coefficient = q if signed_generator > 0 else q**-1
        next_coefficients: dict[TLDiagram, sp.Expr] = {}
        for diagram, coefficient in coefficients.items():
            next_coefficients[diagram] = next_coefficients.get(diagram, sp.Integer(0)) + identity_coefficient * coefficient
            composed, loops = multiply_diagrams(diagram, e_diagram)
            next_coefficients[composed] = next_coefficients.get(composed, sp.Integer(0)) - coefficient * delta**loops
        coefficients = {
            diagram: expanded
            for diagram, coefficient in next_coefficients.items()
            if (expanded := sp.expand(coefficient)) != 0
        }

    closure_trace = sp.simplify(
        sp.Add(*(coefficient * delta ** closure_loops(diagram) for diagram, coefficient in coefficients.items()))
    )
    unreduced = sp.simplify(q ** (-2 * braid_word.writhe()) * closure_trace)
    reduced = sp.simplify(unreduced / delta)
    return TemperleyLiebScalarResult(
        closure_trace=closure_trace,
        unreduced_expression=unreduced,
        unknot_normalization=sp.simplify(delta),
        reduced_expression=reduced,
        basis_term_count=len(coefficients),
    )
