import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from semantic_validation import (
    classify_semantic_support,
    lexical_support,
    evidence_coverage,
)


class SemanticValidationTests(unittest.TestCase):

    def test_strong_evidence_passes(self):
        topic = "Scope of Expert Retention and Testimony"
        evidence = [
            "The expert was retained to provide testimony concerning the scope of the expert's work.",
            "The witness explained the expected testimony and scope of her expert report.",
        ]

        result = classify_semantic_support(topic, evidence)

        self.assertEqual(result["status"], "PASS")
        self.assertGreater(result["topic_support"], 0)
        self.assertGreater(result["coverage"], 0)


    def test_weak_evidence_requires_human_review(self):
        topic = "Scope of Expert Retention and Testimony"
        evidence = [
            "The witness discussed her work and professional experience."
        ]

        result = classify_semantic_support(topic, evidence)

        self.assertEqual(
            result["status"],
            "NEEDS_HUMAN_REVIEW"
        )


    def test_no_evidence_fails(self):
        topic = "Scope of Expert Retention and Testimony"
        evidence = []

        result = classify_semantic_support(topic, evidence)

        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["topic_support"], 0.0)
        self.assertEqual(result["coverage"], 0.0)


    def test_unrelated_evidence_requires_review(self):
        topic = "Scope of Expert Retention and Testimony"
        evidence = [
            "The witness discussed accounting records from a different transaction."
        ]

        result = classify_semantic_support(topic, evidence)

        self.assertEqual(
            result["status"],
            "NEEDS_HUMAN_REVIEW"
        )


    def test_lexical_support_is_bounded(self):
        topic = "Expert testimony"
        evidence = "The expert provided testimony about the case."

        score = lexical_support(topic, evidence)

        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)


    def test_evidence_coverage(self):
        topic = "Expert testimony"
        evidence = [
            "The expert provided testimony.",
            "The witness discussed unrelated records.",
        ]

        result = evidence_coverage(topic, evidence)

        self.assertEqual(result["total_items"], 2)
        self.assertGreaterEqual(result["score"], 0.0)
        self.assertLessEqual(result["score"], 1.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
