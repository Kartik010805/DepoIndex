import json
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from chunk import build_chunks


class ChunkMetadataTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(ROOT / "data" / "lines.json", "r", encoding="utf-8") as f:
            cls.lines = json.load(f)

        with open(ROOT / "data" / "metadata.json", "r", encoding="utf-8") as f:
            cls.metadata = json.load(f)

    def test_chunk_count_is_preserved(self):
        chunks = build_chunks(self.lines, self.metadata)
        self.assertEqual(len(chunks), 25)

    def test_metadata_is_present_on_every_chunk(self):
        chunks = build_chunks(self.lines, self.metadata)

        for chunk in chunks:
            self.assertEqual(chunk["metadata"], self.metadata)

    def test_witness_propagates(self):
        chunks = build_chunks(self.lines, self.metadata)

        self.assertTrue(
            all(chunk["metadata"]["witness"] == "Persis Yu" for chunk in chunks)
        )

    def test_examining_attorney_propagates(self):
        chunks = build_chunks(self.lines, self.metadata)

        self.assertTrue(
            all(
                chunk["metadata"]["examining_attorney"] == "Mr. Purcell"
                for chunk in chunks
            )
        )

    def test_redacted_fields_remain_null(self):
        chunks = build_chunks(self.lines, self.metadata)

        for chunk in chunks:
            self.assertIsNone(chunk["metadata"]["matter"])
            self.assertIsNone(chunk["metadata"]["deposition_date"])
            self.assertIsNone(chunk["metadata"]["parties"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
