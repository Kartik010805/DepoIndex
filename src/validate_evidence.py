import json

LINES_PATH = "data/lines.json"
CHUNKS_PATH = "data/chunks.json"
TEST_RESULT_PATH = "data/test_grounded_result.json"


with open(LINES_PATH, "r", encoding="utf-8") as f:
    transcript_lines = json.load(f)

with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
    chunks = json.load(f)

with open(TEST_RESULT_PATH, "r", encoding="utf-8") as f:
    result = json.load(f)


# Every valid transcript page/line location.
valid_locations = {
    (item["page"], item["line"])
    for item in transcript_lines
}


# The test was generated from chunk 1.
test_chunk = chunks[0]

chunk_locations = {
    (item["page"], item["line"])
    for item in test_chunk["lines"]
}


def location_key(page, line):
    return int(page), int(line)


def validate_topic(topic):
    errors = []

    required_fields = [
        "topic",
        "start_page",
        "start_line",
        "end_page",
        "end_line",
        "evidence",
        "evidence_locations",
    ]

    # ---------------------------------------------------------
    # 1. Required fields
    # ---------------------------------------------------------

    for field in required_fields:
        if field not in topic:
            errors.append(f"Missing field: {field}")

    if errors:
        return errors

    # ---------------------------------------------------------
    # 2. Topic boundaries
    # ---------------------------------------------------------

    start = location_key(
        topic["start_page"],
        topic["start_line"]
    )

    end = location_key(
        topic["end_page"],
        topic["end_line"]
    )

    if start not in valid_locations:
        errors.append(
            f"Invalid start location: "
            f"{topic['start_page']}:{topic['start_line']}"
        )

    if end not in valid_locations:
        errors.append(
            f"Invalid end location: "
            f"{topic['end_page']}:{topic['end_line']}"
        )

    if start > end:
        errors.append("Start location occurs after end location.")

    # ---------------------------------------------------------
    # 3. Evidence locations
    # ---------------------------------------------------------

    evidence_locations = topic["evidence_locations"]

    if not isinstance(evidence_locations, list):
        errors.append("evidence_locations must be a list.")
        return errors

    if not evidence_locations:
        errors.append("No evidence locations supplied.")

    previous_location = None

    for evidence_location in evidence_locations:

        if not isinstance(evidence_location, dict):
            errors.append("Invalid evidence location object.")
            continue

        if (
            "page" not in evidence_location
            or "line" not in evidence_location
        ):
            errors.append(
                "Evidence location must contain page and line."
            )
            continue

        location = location_key(
            evidence_location["page"],
            evidence_location["line"]
        )

        # -----------------------------------------------------
        # 4. Does the evidence location exist at all?
        # -----------------------------------------------------

        if location not in valid_locations:
            errors.append(
                f"Evidence location does not exist: "
                f"{location[0]}:{location[1]}"
            )

        # -----------------------------------------------------
        # 5. Is the evidence inside the topic range?
        # -----------------------------------------------------

        if location < start or location > end:
            errors.append(
                f"Evidence location outside topic range: "
                f"{location[0]}:{location[1]}"
            )

        # -----------------------------------------------------
        # 6. Is the evidence actually from the supplied chunk?
        # -----------------------------------------------------

        if location not in chunk_locations:
            errors.append(
                f"Evidence location is not present in "
                f"the supplied chunk: "
                f"{location[0]}:{location[1]}"
            )

        # -----------------------------------------------------
        # 7. Evidence must be chronological
        # -----------------------------------------------------

        if (
            previous_location is not None
            and location < previous_location
        ):
            errors.append(
                "Evidence locations are not chronological."
            )

        previous_location = location

    return errors


topics = result.get("topics", [])

print(f"Validating {len(topics)} topic(s)...")

all_valid = True

for index, topic in enumerate(topics, start=1):

    errors = validate_topic(topic)

    if errors:
        all_valid = False

        print(f"\nTopic {index}: FAIL")

        for error in errors:
            print(f"  - {error}")

    else:
        print(
            f"Topic {index}: PASS - "
            f"{topic['topic']}"
        )


print()

if all_valid:
    print("Evidence/provenance/grounding validation: PASS")
else:
    print("Evidence/provenance/grounding validation: FAIL")