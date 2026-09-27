import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from extract_metadata import extract_metadata


class MetadataExtractionTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pdf_path = ROOT / "data" / "raw" / "Persis_Yu_Deposition.pdf"

    def test_witness_is_extracted(self):
        metadata = extract_metadata(self.pdf_path)
        self.assertEqual(metadata["witness"], "Persis Yu")

    def test_examining_attorney_is_cleaned(self):
        metadata = extract_metadata(self.pdf_path)
        self.assertEqual(metadata["examining_attorney"], "Mr. Purcell")

    def test_redacted_matter_is_not_invented(self):
        metadata = extract_metadata(self.pdf_path)
        self.assertIsNone(metadata["matter"])

    def test_redacted_deposition_date_is_not_invented(self):
        metadata = extract_metadata(self.pdf_path)
        self.assertIsNone(metadata["deposition_date"])

    def test_redacted_parties_are_not_invented(self):
        metadata = extract_metadata(self.pdf_path)
        self.assertIsNone(metadata["parties"])

    def test_redaction_status_is_preserved(self):
        metadata = extract_metadata(self.pdf_path)
        self.assertEqual(
            metadata["administrative_information"],
            "redacted",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
