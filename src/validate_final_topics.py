import json
from pathlib import Path

from semantic_validation import classify_semantic_support
from validation_states import (
    ValidationStatus,
    build_validation_state,
)


FINAL_PATH = Path("data/final_grounded_topics_repaired.json")
LINES_PATH = Path("data/lines.json")
CHUNKS_PATH = Path("data/chunks.json")

OUTPUT_PATH = Path(
    "data/final_grounded_topics_validated.json"
)

REPORT_PATH = Path(
    "data/final_validation_repaired.json"
)


REQUIRED_FIELDS = [
    "topic",
    "start_page",
    "start_line",
    "end_page",
    "end_line",
    "evidence",
    "evidence_locations",
    "source_chunks",
    "grounding_source",
]


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False,
        )


def location_key(page, line):
    return (
        int(page),
        int(line),
    )


def location_in_range(
    location,
    start,
    end,
):
    return start <= location <= end


def build_line_map(lines):
    return {
        location_key(
            item["page"],
            item["line"],
        ): item.get("text", "")
        for item in lines
    }


def build_line_set(lines):
    return set(
        build_line_map(lines).keys()
    )


def build_chunk_line_sets(chunks):
    chunk_map = {}

    for chunk in chunks:

        chunk_id = chunk.get("chunk_id")

        if chunk_id is None:
            continue

        locations = set()

        for item in chunk.get(
            "lines",
            [],
        ):
            locations.add(
                location_key(
                    item["page"],
                    item["line"],
                )
            )

        chunk_map[int(chunk_id)] = locations

    return chunk_map


# ============================================================
# STRUCTURAL VALIDATION
# ============================================================

def validate_structural(topic):
    errors = []

    for field in REQUIRED_FIELDS:

        if field not in topic:
            errors.append(
                f"missing required field: {field}"
            )

    if errors:
        return errors, None, None

    try:

        start = location_key(
            topic["start_page"],
            topic["start_line"],
        )

        end = location_key(
            topic["end_page"],
            topic["end_line"],
        )

    except (
        TypeError,
        ValueError,
    ):

        errors.append(
            "invalid start/end location values"
        )

        return errors, None, None

    if start > end:

        errors.append(
            f"start location "
            f"{start[0]}:{start[1]} "
            f"is after end location "
            f"{end[0]}:{end[1]}"
        )

    if not isinstance(
        topic.get("evidence_locations"),
        list,
    ):

        errors.append(
            "evidence_locations must be a list"
        )

    if not isinstance(
        topic.get("source_chunks"),
        list,
    ):

        errors.append(
            "source_chunks must be a list"
        )

    return errors, start, end


# ============================================================
# REFERENTIAL VALIDATION
# ============================================================

def validate_referential(
    topic,
    start,
    end,
    valid_lines,
    chunk_map,
):
    errors = []

    if start is None or end is None:
        return [
            "cannot perform referential validation "
            "because start/end locations are invalid"
        ]

    if start not in valid_lines:

        errors.append(
            f"start location "
            f"{start[0]}:{start[1]} "
            f"does not exist"
        )

    if end not in valid_lines:

        errors.append(
            f"end location "
            f"{end[0]}:{end[1]} "
            f"does not exist"
        )

    source_chunks = topic.get(
        "source_chunks",
        [],
    )

    if isinstance(
        source_chunks,
        list,
    ):

        for chunk_id in source_chunks:

            try:
                numeric_chunk_id = int(
                    chunk_id
                )

            except (
                TypeError,
                ValueError,
            ):

                errors.append(
                    f"invalid source chunk id: "
                    f"{chunk_id}"
                )

                continue

            if numeric_chunk_id not in chunk_map:

                errors.append(
                    f"source chunk "
                    f"{numeric_chunk_id} "
                    f"does not exist"
                )

    return errors


# ============================================================
# GROUNDING / PROVENANCE VALIDATION
# ============================================================

def validate_grounding(
    topic,
    start,
    end,
    valid_lines,
    chunk_map,
):
    errors = []

    if start is None or end is None:
        return [
            "cannot perform grounding validation "
            "because start/end locations are invalid"
        ]

    if topic.get(
        "grounding_source"
    ) != "grounded_merged_topics":

        errors.append(
            "grounding_source must be "
            "'grounded_merged_topics'"
        )

    source_chunks = topic.get(
        "source_chunks",
        [],
    )

    if not isinstance(
        source_chunks,
        list,
    ):

        errors.append(
            "source_chunks must be a list"
        )

        source_chunks = []

    evidence_locations = topic.get(
        "evidence_locations",
        [],
    )

    if not isinstance(
        evidence_locations,
        list,
    ):

        errors.append(
            "evidence_locations must be a list"
        )

        evidence_locations = []

    previous_location = None

    for evidence_location in evidence_locations:

        if not isinstance(
            evidence_location,
            dict,
        ):

            errors.append(
                "evidence location must be an object"
            )

            continue

        if (
            "page" not in evidence_location
            or "line" not in evidence_location
        ):

            errors.append(
                "evidence location missing "
                "page or line"
            )

            continue

        try:

            location = location_key(
                evidence_location["page"],
                evidence_location["line"],
            )

        except (
            TypeError,
            ValueError,
        ):

            errors.append(
                "invalid evidence location values"
            )

            continue

        # Evidence location must exist.
        if location not in valid_lines:

            errors.append(
                f"evidence location "
                f"{location[0]}:{location[1]} "
                f"does not exist"
            )

        # Evidence must belong to topic range.
        if not location_in_range(
            location,
            start,
            end,
        ):

            errors.append(
                f"evidence location "
                f"{location[0]}:{location[1]} "
                f"is outside topic range"
            )

        # Evidence locations must be chronological.
        if (
            previous_location is not None
            and location < previous_location
        ):

            errors.append(
                f"evidence location "
                f"{location[0]}:{location[1]} "
                f"is out of chronological order"
            )

        previous_location = location

        # Evidence must belong to at least one
        # declared source chunk.
        if source_chunks:

            belongs_to_source_chunk = False

            for chunk_id in source_chunks:

                try:
                    numeric_chunk_id = int(
                        chunk_id
                    )

                except (
                    TypeError,
                    ValueError,
                ):
                    continue

                if location in chunk_map.get(
                    numeric_chunk_id,
                    set(),
                ):

                    belongs_to_source_chunk = True
                    break

            if not belongs_to_source_chunk:

                errors.append(
                    f"evidence location "
                    f"{location[0]}:{location[1]} "
                    f"is not contained in any "
                    f"source chunk"
                )

    return errors


# ============================================================
# SEMANTIC VALIDATION
# ============================================================

def get_evidence_texts(
    topic,
    line_map,
):
    evidence_texts = []

    for location in topic.get(
        "evidence_locations",
        [],
    ):

        if not isinstance(
            location,
            dict,
        ):
            continue

        try:

            key = location_key(
                location["page"],
                location["line"],
            )

        except (
            KeyError,
            TypeError,
            ValueError,
        ):
            continue

        text = line_map.get(
            key,
            "",
        )

        if text:
            evidence_texts.append(text)

    return evidence_texts


def validate_semantic(
    topic,
    line_map,
):
    evidence_texts = get_evidence_texts(
        topic,
        line_map,
    )

    result = classify_semantic_support(
        topic.get(
            "topic",
            "",
        ),
        evidence_texts,
    )

    return result


# ============================================================
# MAIN VALIDATION
# ============================================================

def main():

    print()
    print("=" * 60)
    print("FINAL GROUNDED TOPIC VALIDATION")
    print("=" * 60)

    final_topics = load_json(
        FINAL_PATH
    )

    lines = load_json(
        LINES_PATH
    )

    chunks = load_json(
        CHUNKS_PATH
    )

    valid_lines = build_line_set(
        lines
    )

    line_map = build_line_map(
        lines
    )

    chunk_map = build_chunk_line_sets(
        chunks
    )

    print(
        f"Input: {FINAL_PATH}"
    )

    print(
        f"Topics: {len(final_topics)}"
    )

    print()

    validated_topics = []
    results = []

    passed = 0
    human_review = 0
    failed = 0

    previous_start = None

    for index, topic in enumerate(
        final_topics,
        start=1,
    ):

        topic_name = topic.get(
            "topic",
            "<missing topic>",
        )

        # ----------------------------------------------------
        # Structural
        # ----------------------------------------------------

        structural_errors, start, end = (
            validate_structural(topic)
        )

        structural_status = (
            ValidationStatus.PASS.value
            if not structural_errors
            else ValidationStatus.FAIL.value
        )

        # ----------------------------------------------------
        # Global chronological ordering
        # ----------------------------------------------------

        if start is not None:

            if (
                previous_start is not None
                and start < previous_start
            ):

                structural_errors.append(
                    "topic start is out of "
                    "chronological order"
                )

                structural_status = (
                    ValidationStatus.FAIL.value
                )

            previous_start = start

        # ----------------------------------------------------
        # Referential
        # ----------------------------------------------------

        referential_errors = (
            validate_referential(
                topic,
                start,
                end,
                valid_lines,
                chunk_map,
            )
        )

        referential_status = (
            ValidationStatus.PASS.value
            if not referential_errors
            else ValidationStatus.FAIL.value
        )

        # ----------------------------------------------------
        # Grounding
        # ----------------------------------------------------

        grounding_errors = (
            validate_grounding(
                topic,
                start,
                end,
                valid_lines,
                chunk_map,
            )
        )

        grounding_status = (
            ValidationStatus.PASS.value
            if not grounding_errors
            else ValidationStatus.FAIL.value
        )

        # ----------------------------------------------------
        # Semantic
        # ----------------------------------------------------

        semantic_result = validate_semantic(
            topic,
            line_map,
        )

        semantic_status = semantic_result[
            "status"
        ]

        # ----------------------------------------------------
        # Review reasons
        # ----------------------------------------------------

        review_reasons = []

        if (
            semantic_status
            == ValidationStatus.NEEDS_HUMAN_REVIEW.value
        ):

            review_reasons.append(
                semantic_result["reason"]
            )

        # ----------------------------------------------------
        # Build overall state
        # ----------------------------------------------------

        validation_state = (
            build_validation_state(
                structural=structural_status,
                referential=referential_status,
                grounding=grounding_status,
                semantic=semantic_status,
                review_reasons=review_reasons,
            )
        )

        overall_status = validation_state[
            "overall_status"
        ]

        # ----------------------------------------------------
        # Combine deterministic errors
        # ----------------------------------------------------

        all_errors = (
            structural_errors
            + referential_errors
            + grounding_errors
        )

        # ----------------------------------------------------
        # Preserve every existing topic field.
        # Add validation information only.
        # ----------------------------------------------------

        validated_topic = dict(topic)

        validated_topic[
            "validation_state"
        ] = validation_state

        validated_topic[
            "semantic_validation"
        ] = semantic_result

        validated_topics.append(
            validated_topic
        )

        # ----------------------------------------------------
        # Report entry
        # ----------------------------------------------------

        results.append(
            {
                "topic_number": index,
                "topic": topic_name,
                "status": overall_status,
                "errors": all_errors,
                "validation_state": validation_state,
                "semantic_validation": semantic_result,
            }
        )

        # ----------------------------------------------------
        # Console output
        # ----------------------------------------------------

        if (
            overall_status
            == ValidationStatus.PASS.value
        ):

            passed += 1

            print(
                f"Topic {index}: PASS - "
                f"{topic_name}"
            )

        elif (
            overall_status
            == ValidationStatus.NEEDS_HUMAN_REVIEW.value
        ):

            human_review += 1

            print(
                f"Topic {index}: "
                f"NEEDS_HUMAN_REVIEW - "
                f"{topic_name}"
            )

        else:

            failed += 1

            print(
                f"Topic {index}: FAIL - "
                f"{topic_name}"
            )

            for error in all_errors:

                print(
                    f"    - {error}"
                )

    # ========================================================
    # Overall status
    # ========================================================

    if failed > 0:

        overall_status = (
            ValidationStatus.FAIL.value
        )

    elif human_review > 0:

        overall_status = (
            ValidationStatus.NEEDS_HUMAN_REVIEW.value
        )

    else:

        overall_status = (
            ValidationStatus.PASS.value
        )

    # ========================================================
    # Validation report
    # ========================================================

    report = {
        "status": overall_status,
        "total_topics": len(final_topics),
        "passed": passed,
        "needs_human_review": human_review,
        "failed": failed,
        "input_file": str(FINAL_PATH),
        "output_file": str(OUTPUT_PATH),
        "results": results,
    }

    save_json(
        OUTPUT_PATH,
        validated_topics,
    )

    save_json(
        REPORT_PATH,
        report,
    )

    print()
    print("=" * 60)
    print(
        f"FINAL VALIDATION: "
        f"{overall_status}"
    )
    print("=" * 60)

    print(
        f"Total topics: {len(final_topics)}"
    )

    print(
        f"PASS: {passed}"
    )

    print(
        f"NEEDS_HUMAN_REVIEW: "
        f"{human_review}"
    )

    print(
        f"FAIL: {failed}"
    )

    print()
    print(
        f"Validated topics saved to "
        f"{OUTPUT_PATH}"
    )

    print(
        f"Validation report saved to "
        f"{REPORT_PATH}"
    )


if __name__ == "__main__":
    main()