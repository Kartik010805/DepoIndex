import ast
import json
import unittest
from pathlib import Path


class TestRunPipelineMetadata(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        source = Path("src/run_pipeline.py").read_text(encoding="utf-8")
        tree = ast.parse(source)

        functions = {
            node.name: node
            for node in tree.body
            if isinstance(node, ast.FunctionDef)
        }

        required = ["build_candidate_record", "build_prompt"]

        for name in required:
            if name not in functions:
                raise AssertionError(
                    f"Required function '{name}' not found in run_pipeline.py"
                )

        module = ast.Module(
            body=[
                functions["build_candidate_record"],
                functions["build_prompt"],
            ],
            type_ignores=[],
        )
        module = ast.fix_missing_locations(module)

        namespace = {
            "json": json,
        }

        exec(
            compile(
                module,
                "run_pipeline_metadata_test",
                "exec",
            ),
            namespace,
        )

        cls.build_candidate_record = staticmethod(
            namespace["build_candidate_record"]
        )

        cls.build_prompt = staticmethod(
            namespace["build_prompt"]
        )

        with open(
            "data/chunks.json",
            "r",
            encoding="utf-8",
        ) as f:
            cls.chunk = json.load(f)[0]

    def test_candidate_record_preserves_metadata(self):
        topics = [{"topic": "Test Topic"}]

        record = self.build_candidate_record(
            self.chunk,
            topics,
        )

        self.assertEqual(
            record["metadata"],
            self.chunk["metadata"],
        )

        self.assertEqual(
            record["metadata"]["witness"],
            "Persis Yu",
        )

        self.assertEqual(
            record["metadata"]["examining_attorney"],
            "Mr. Purcell",
        )

    def test_candidate_record_preserves_topics(self):
        topics = [{"topic": "Test Topic"}]

        record = self.build_candidate_record(
            self.chunk,
            topics,
        )

        self.assertEqual(
            record["topics"],
            topics,
        )

    def test_candidate_record_preserves_chunk_location(self):
        record = self.build_candidate_record(
            self.chunk,
            [{"topic": "Test Topic"}],
        )

        self.assertEqual(
            record["start_page"],
            self.chunk["start_page"],
        )

        self.assertEqual(
            record["start_line"],
            self.chunk["start_line"],
        )

        self.assertEqual(
            record["end_page"],
            self.chunk["end_page"],
        )

        self.assertEqual(
            record["end_line"],
            self.chunk["end_line"],
        )

    def test_prompt_contains_metadata(self):
        prompt = self.build_prompt(self.chunk)

        self.assertIn(
            "DOCUMENT METADATA",
            prompt,
        )

        self.assertIn(
            "Witness: Persis Yu",
            prompt,
        )

        self.assertIn(
            "Examining Attorney: Mr. Purcell",
            prompt,
        )

        self.assertIn(
            "Matter/Case: Not available",
            prompt,
        )

        self.assertIn(
            "Deposition Date: Not available",
            prompt,
        )

        self.assertIn(
            "Parties: Not available",
            prompt,
        )

    def test_prompt_preserves_source_locations(self):
        prompt = self.build_prompt(self.chunk)

        first_line = self.chunk["lines"][0]

        expected_location = (
            f"[Page {first_line['page']}, Line {first_line['line']}]"
        )

        self.assertIn(
            expected_location,
            prompt,
        )


if __name__ == "__main__":
    unittest.main()
