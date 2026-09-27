import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(
    0,
    str(ROOT / "src")
)

from semantic_validation import (
    classify_semantic_support
)


TOPICS_PATH = (
    ROOT
    / "data"
    / "final_grounded_topics_repaired.json"
)

LINES_PATH = (
    ROOT
    / "data"
    / "lines.json"
)

OUTPUT_PATH = (
    ROOT
    / "data"
    / "semantic_validation.json"
)


def load_json(path):
    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def build_line_index(lines):
    """
    Create direct lookup:

        (page, line) -> transcript text
    """

    return {
        (
            int(item["page"]),
            int(item["line"])
        ): item["text"]

        for item in lines
    }


def validate_topic(
    topic,
    line_index
):
    """
    Validate semantic/evidence support for one topic.
    """

    topic_name = topic.get(
        "topic",
        ""
    )

    evidence_locations = topic.get(
        "evidence_locations",
        []
    )

    evidence_texts = []

    missing_locations = []

    for location in evidence_locations:

        page = location.get("page")
        line = location.get("line")

        key = (
            int(page),
            int(line)
        )

        text = line_index.get(key)

        if text is None:

            missing_locations.append(
                f"{page}:{line}"
            )

        else:

            evidence_texts.append(text)

    # ---------------------------------------------------------
    # Hard provenance failure
    # ---------------------------------------------------------

    if missing_locations:

        return {
            "status": "FAIL",
            "reason": (
                "Evidence location(s) do not exist "
                "in the transcript."
            ),
            "topic_support": 0.0,
            "coverage": 0.0,
            "evidence_count": len(evidence_texts),
            "missing_locations": missing_locations,
        }

    # ---------------------------------------------------------
    # Semantic/evidence validation
    # ---------------------------------------------------------

    result = classify_semantic_support(
        topic_name,
        evidence_texts
    )

    return {
        "status": result["status"],
        "reason": result["reason"],
        "topic_support": result["topic_support"],
        "coverage": result["coverage"],
        "evidence_count": len(evidence_texts),
        "missing_locations": [],
    }


def main():

    topics = load_json(
        TOPICS_PATH
    )

    lines = load_json(
        LINES_PATH
    )

    line_index = build_line_index(
        lines
    )

    validation_results = []

    pass_count = 0
    review_count = 0
    fail_count = 0

    for index, topic in enumerate(
        topics,
        start=1
    ):

        result = validate_topic(
            topic,
            line_index
        )

        record = {
            "topic_index": index,
            "topic": topic.get("topic"),
            "start_page": topic.get("start_page"),
            "start_line": topic.get("start_line"),
            "end_page": topic.get("end_page"),
            "end_line": topic.get("end_line"),
            "evidence_locations": topic.get(
                "evidence_locations",
                []
            ),
            "status": result["status"],
            "reason": result["reason"],
            "topic_support": result[
                "topic_support"
            ],
            "coverage": result[
                "coverage"
            ],
            "evidence_count": result[
                "evidence_count"
            ],
            "missing_locations": result[
                "missing_locations"
            ],
        }

        validation_results.append(
            record
        )

        if result["status"] == "PASS":
            pass_count += 1

        elif result["status"] == "NEEDS_HUMAN_REVIEW":
            review_count += 1

        else:
            fail_count += 1

    output = {
        "validation_type": (
            "deterministic_semantic_evidence"
        ),
        "total_topics": len(topics),
        "passed": pass_count,
        "needs_human_review": review_count,
        "failed": fail_count,
        "results": validation_results,
    }

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            indent=2,
            ensure_ascii=False
        )

    print("=" * 60)
    print("SEMANTIC / EVIDENCE VALIDATION")
    print("=" * 60)

    print(
        f"Total topics: {len(topics)}"
    )

    print(
        f"PASS: {pass_count}"
    )

    print(
        f"NEEDS_HUMAN_REVIEW: {review_count}"
    )

    print(
        f"FAIL: {fail_count}"
    )

    print(
        f"Saved to {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()
