import json
from pathlib import Path


FINAL_PATH = Path("data/final_grounded_topics_repaired.json")
LINES_PATH = Path("data/lines.json")
CHUNKS_PATH = Path("data/chunks.json")
OUTPUT_PATH = Path("data/final_validation_repaired.json")


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


def location_key(page, line):
    return (int(page), int(line))


def location_in_range(location, start, end):
    return start <= location <= end


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_line_set(lines):
    return {
        location_key(item["page"], item["line"])
        for item in lines
    }


def build_chunk_line_sets(chunks):
    chunk_map = {}

    for chunk in chunks:
        chunk_id = chunk.get("chunk_id")

        if chunk_id is None:
            continue

        locations = set()

        for item in chunk.get("lines", []):
            locations.add(
                location_key(
                    item["page"],
                    item["line"]
                )
            )

        chunk_map[int(chunk_id)] = locations

    return chunk_map


def validate_topic(topic, index, valid_lines, chunk_map):
    errors = []

    # ---------------------------------------------------------
    # Required fields
    # ---------------------------------------------------------
    for field in REQUIRED_FIELDS:
        if field not in topic:
            errors.append(f"missing required field: {field}")

    if errors:
        return errors

    # ---------------------------------------------------------
    # Basic values
    # ---------------------------------------------------------
    try:
        start = location_key(
            topic["start_page"],
            topic["start_line"]
        )

        end = location_key(
            topic["end_page"],
            topic["end_line"]
        )
    except (TypeError, ValueError):
        return ["invalid start/end location values"]

    # ---------------------------------------------------------
    # Start/end must exist in transcript
    # ---------------------------------------------------------
    if start not in valid_lines:
        errors.append(
            f"start location {start[0]}:{start[1]} does not exist"
        )

    if end not in valid_lines:
        errors.append(
            f"end location {end[0]}:{end[1]} does not exist"
        )

    # ---------------------------------------------------------
    # Chronological range
    # ---------------------------------------------------------
    if start > end:
        errors.append(
            f"start location {start[0]}:{start[1]} "
            f"is after end location {end[0]}:{end[1]}"
        )

    # ---------------------------------------------------------
    # Source chunks
    # ---------------------------------------------------------
    source_chunks = topic.get("source_chunks", [])

    if not isinstance(source_chunks, list):
        errors.append("source_chunks must be a list")
    else:
        for chunk_id in source_chunks:
            try:
                chunk_id = int(chunk_id)
            except (TypeError, ValueError):
                errors.append(
                    f"invalid source chunk id: {chunk_id}"
                )
                continue

            if chunk_id not in chunk_map:
                errors.append(
                    f"source chunk {chunk_id} does not exist"
                )

    # ---------------------------------------------------------
    # Evidence locations
    # ---------------------------------------------------------
    evidence_locations = topic.get("evidence_locations", [])

    if not isinstance(evidence_locations, list):
        errors.append("evidence_locations must be a list")
        evidence_locations = []

    previous_location = None

    for evidence_location in evidence_locations:

        if not isinstance(evidence_location, dict):
            errors.append(
                "evidence location must be an object"
            )
            continue

        if "page" not in evidence_location or "line" not in evidence_location:
            errors.append(
                "evidence location missing page or line"
            )
            continue

        try:
            loc = location_key(
                evidence_location["page"],
                evidence_location["line"]
            )
        except (TypeError, ValueError):
            errors.append(
                "invalid evidence location values"
            )
            continue

        # Must exist in transcript
        if loc not in valid_lines:
            errors.append(
                f"evidence location {loc[0]}:{loc[1]} "
                f"does not exist"
            )

        # Must be inside final topic range
        if not location_in_range(loc, start, end):
            errors.append(
                f"evidence location {loc[0]}:{loc[1]} "
                f"is outside topic range"
            )

        # Evidence locations should be chronological
        if previous_location is not None and loc < previous_location:
            errors.append(
                f"evidence location {loc[0]}:{loc[1]} "
                f"is out of chronological order"
            )

        previous_location = loc

        # -----------------------------------------------------
        # Evidence must belong to at least one source chunk
        # -----------------------------------------------------
        if source_chunks:
            belongs_to_source_chunk = False

            for chunk_id in source_chunks:
                try:
                    chunk_id = int(chunk_id)
                except (TypeError, ValueError):
                    continue

                if loc in chunk_map.get(chunk_id, set()):
                    belongs_to_source_chunk = True
                    break

            if not belongs_to_source_chunk:
                errors.append(
                    f"evidence location {loc[0]}:{loc[1]} "
                    f"is not contained in any source chunk"
                )

    # ---------------------------------------------------------
    # Grounding source
    # ---------------------------------------------------------
    if topic.get("grounding_source") != "grounded_merged_topics":
        errors.append(
            "grounding_source must be 'grounded_merged_topics'"
        )

    return errors


def main():
    final_topics = load_json(FINAL_PATH)
    lines = load_json(LINES_PATH)
    chunks = load_json(CHUNKS_PATH)

    valid_lines = build_line_set(lines)
    chunk_map = build_chunk_line_sets(chunks)

    print()
    print("=" * 60)
    print("FINAL GROUNDED TOPIC VALIDATION")
    print("=" * 60)
    print(f"Input: {FINAL_PATH}")
    print(f"Topics: {len(final_topics)}")
    print()

    results = []

    passed = 0
    failed = 0

    for index, topic in enumerate(final_topics, start=1):

        errors = validate_topic(
            topic,
            index,
            valid_lines,
            chunk_map
        )

        topic_name = topic.get(
            "topic",
            "<missing topic>"
        )

        if errors:
            failed += 1

            print(
                f"Topic {index}: FAIL - {topic_name}"
            )

            for error in errors:
                print(f"    - {error}")

            results.append(
                {
                    "topic_number": index,
                    "topic": topic_name,
                    "status": "FAIL",
                    "errors": errors,
                }
            )

        else:
            passed += 1

            print(
                f"Topic {index}: PASS - {topic_name}"
            )

            results.append(
                {
                    "topic_number": index,
                    "topic": topic_name,
                    "status": "PASS",
                    "errors": [],
                }
            )

    # ---------------------------------------------------------
    # Final summary
    # ---------------------------------------------------------
    overall_status = "PASS" if failed == 0 else "FAIL"

    report = {
        "status": overall_status,
        "total_topics": len(final_topics),
        "passed": passed,
        "failed": failed,
        "input_file": str(FINAL_PATH),
        "results": results,
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(
            report,
            f,
            indent=2,
            ensure_ascii=False
        )

    print()
    print("=" * 60)
    print(f"FINAL VALIDATION: {overall_status}")
    print("=" * 60)
    print(f"Total topics: {len(final_topics)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print()
    print(f"Saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()