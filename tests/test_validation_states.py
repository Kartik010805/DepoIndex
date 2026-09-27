import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from validation_states import (
    ValidationStatus,
    build_validation_state,
    determine_overall_status,
    is_terminal_failure,
    needs_human_review,
    is_validated,
)


class ValidationStateTests(unittest.TestCase):

    def test_all_pass(self):
        result = build_validation_state(
            structural="PASS",
            referential="PASS",
            grounding="PASS",
            semantic="PASS",
        )

        self.assertEqual(
            result["overall_status"],
            ValidationStatus.PASS.value
        )

        self.assertTrue(
            is_validated(result)
        )


    def test_semantic_review(self):
        result = build_validation_state(
            structural="PASS",
            referential="PASS",
            grounding="PASS",
            semantic="NEEDS_HUMAN_REVIEW",
        )

        self.assertEqual(
            result["overall_status"],
            ValidationStatus.NEEDS_HUMAN_REVIEW.value
        )

        self.assertTrue(
            needs_human_review(result)
        )


    def test_hard_failure_overrides_review(self):
        result = build_validation_state(
            structural="PASS",
            referential="FAIL",
            grounding="PASS",
            semantic="NEEDS_HUMAN_REVIEW",
        )

        self.assertEqual(
            result["overall_status"],
            ValidationStatus.FAIL.value
        )

        self.assertTrue(
            is_terminal_failure(result)
        )


    def test_multiple_reviews(self):
        result = build_validation_state(
            structural="NEEDS_HUMAN_REVIEW",
            referential="NEEDS_HUMAN_REVIEW",
            grounding="PASS",
            semantic="PASS",
        )

        self.assertEqual(
            result["overall_status"],
            ValidationStatus.NEEDS_HUMAN_REVIEW.value
        )


    def test_fail_takes_precedence(self):
        result = determine_overall_status({
            "structural": "FAIL",
            "referential": "PASS",
            "grounding": "NEEDS_HUMAN_REVIEW",
            "semantic": "PASS",
        })

        self.assertEqual(
            result,
            "FAIL"
        )


    def test_invalid_status_is_rejected(self):
        with self.assertRaises(ValueError):
            build_validation_state(
                structural="PASS",
                referential="INVALID",
                grounding="PASS",
                semantic="PASS",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
