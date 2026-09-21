"""Focused regression checks for the current Knot Atlas correspondence wording of the sl2 3D candidate branch."""

from __future__ import annotations

import unittest

import sympy as sp

from src.invariants.sl2_3d_colored_jones_candidate import (
    SL2_3D_KNOT_ATLAS_COMPARISON_RULE,
    SL2_3D_KNOT_ATLAS_FIVE_ONE_RELATION,
    SL2_3D_KNOT_ATLAS_SCOPE_NOTE,
    SL2_3D_KNOT_ATLAS_TREFOIL_RELATION,
    SL2_3D_KNOT_ATLAS_VERIFICATION_NOTE,
    compute_sl2_3d_knot_atlas_correspondence,
    evaluate_sl2_3d_knot_atlas_correspondence,
    get_sl2_3d_knot_atlas_reference_cases,
    get_sl2_3d_knot_atlas_summary_lines,
)


Q = sp.Symbol("q", nonzero=True)


class TestSl2ThreeDimKnotAtlasCorrespondence(unittest.TestCase):
    def test_reference_case_set_includes_3_1_5_1_and_5_2(self) -> None:
        self.assertEqual(
            [case.case_id for case in get_sl2_3d_knot_atlas_reference_cases()],
            ["3_1", "5_1", "5_2"],
        )

    def test_trefoil_is_currently_confirmed_against_knot_atlas_n2_data(self) -> None:
        check = compute_sl2_3d_knot_atlas_correspondence("3_1", q=Q)

        self.assertEqual(check.status, "confirmed")
        self.assertEqual(check.q_shift, 6)
        self.assertEqual(
            sp.simplify(check.candidate_output - Q**6 * check.substituted_reference),
            sp.Integer(0),
        )
        self.assertIn("q^6 J_2(3_1; q^2)", check.relation_text)

    def test_five_one_is_currently_confirmed_by_a_direct_q_shift_check(self) -> None:
        check = compute_sl2_3d_knot_atlas_correspondence("5_1", q=Q)

        self.assertEqual(check.status, "confirmed")
        self.assertIsNotNone(check.candidate_output)
        self.assertEqual(check.q_shift, 10)
        self.assertEqual(
            sp.simplify(check.candidate_output - Q**10 * check.substituted_reference),
            sp.Integer(0),
        )
        self.assertIn("q^10 J_2(5_1; q^2)", check.relation_text)

    def test_five_two_is_reference_only_until_a_project_braid_is_fixed(self) -> None:
        check = compute_sl2_3d_knot_atlas_correspondence("5_2", q=Q)

        self.assertEqual(check.status, "under_verification")
        self.assertIsNone(check.candidate_output)
        self.assertIsNone(check.q_shift)
        self.assertIn("not fixed yet", check.relation_text)

    def test_summary_lines_keep_the_shared_knot_atlas_wording(self) -> None:
        self.assertEqual(
            get_sl2_3d_knot_atlas_summary_lines(),
            (
                SL2_3D_KNOT_ATLAS_COMPARISON_RULE,
                SL2_3D_KNOT_ATLAS_TREFOIL_RELATION,
                SL2_3D_KNOT_ATLAS_FIVE_ONE_RELATION,
                SL2_3D_KNOT_ATLAS_SCOPE_NOTE,
                SL2_3D_KNOT_ATLAS_VERIFICATION_NOTE,
            ),
        )

    def test_batch_evaluation_keeps_the_same_status_sequence(self) -> None:
        checks = evaluate_sl2_3d_knot_atlas_correspondence(q=Q)

        self.assertEqual([check.case_id for check in checks], ["3_1", "5_1", "5_2"])
        self.assertEqual([check.status for check in checks], ["confirmed", "confirmed", "under_verification"])