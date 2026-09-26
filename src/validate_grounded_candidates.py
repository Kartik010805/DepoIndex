import json


# ============================================================
# Configuration
# ============================================================

GROUNDED_PATH = "data/grounded_candidate_topics_repaired.json"
TRANSCRIPT_PATH = "data/lines.json"
CHUNKS_PATH = "data/chunks.json"

OUTPUT_PATH = "data/grounding_validation_repaired.json"


# ============================================================
# Helpers
# ============================================================

def location_key(page, line):
    return page * 1000 + line


def location_in_range(location, start, end):
    key = location_key(
        location["page"],
        location["line"]
    )

    return start <= key <= end


# ============================================================
# Load files
# ============================================================

with open(
    GROUNDED_PATH,
    "r",
    encoding="utf-8"
) as f:
    grounded_data = json.load(f)


with open(
    TRANSCRIPT_PATH,
    "r",
    encoding="utf-8"
) as f:
    transcript = json.load(f)


with open(
    CHUNKS_PATH,
    "r",
    encoding="utf-8"
) as f:
    chunks = json.load(f)


# ============================================================
# Valid transcript locations
# ============================================================

valid_transcript_locations = {
    (
        line["page"],
        line["line"]
    )
    for line in transcript
}


# ============================================================
# Source chunk locations
# ============================================================

chunk_locations = {}

for chunk in chunks:

    chunk_locations[chunk["chunk_id"]] = {
        (
            line["page"],
            line["line"]
        )
        for line in chunk["lines"]
    }


# ============================================================
# Validate topics
# ============================================================

topics = grounded_data.get("topics", [])

errors = []
passed = 0


print()
print(
    f"Validating {len(topics)} repaired grounded "
    f"candidate topics..."
)
print()


for index, topic in enumerate(
    topics,
    start=1
):

    topic_errors = []


    # --------------------------------------------------------
    # Required fields
    # --------------------------------------------------------

    required_fields = [
        "topic",
        "start_page",
        "start_line",
        "end_page",
        "end_line",
        "evidence",
        "evidence_locations",
        "source_chunks"
    ]


    for field in required_fields:

        if field not in topic:

            topic_errors.append(
                f"missing required field '{field}'"
            )


    if topic_errors:

        errors.append(
            {
                "topic_number": index,
                "topic": topic.get(
                    "topic",
                    "UNKNOWN"
                ),
                "errors": topic_errors
            }
        )

        print(
            f"Topic {index}: FAIL"
        )

        continue


    # --------------------------------------------------------
    # Topic boundaries
    # --------------------------------------------------------

    start = location_key(
        topic["start_page"],
        topic["start_line"]
    )

    end = location_key(
        topic["end_page"],
        topic["end_line"]
    )


    if start > end:

        topic_errors.append(
            "topic start is after topic end"
        )


    # --------------------------------------------------------
    # Validate start location
    # --------------------------------------------------------

    start_location = (
        topic["start_page"],
        topic["start_line"]
    )


    if start_location not in valid_transcript_locations:

        topic_errors.append(
            f"invalid start location "
            f"{topic['start_page']}:{topic['start_line']}"
        )


    # --------------------------------------------------------
    # Validate end location
    # --------------------------------------------------------

    end_location = (
        topic["end_page"],
        topic["end_line"]
    )


    if end_location not in valid_transcript_locations:

        topic_errors.append(
            f"invalid end location "
            f"{topic['end_page']}:{topic['end_line']}"
        )


    # --------------------------------------------------------
    # Validate evidence locations
    # --------------------------------------------------------

    evidence_locations = topic[
        "evidence_locations"
    ]


    if not isinstance(
        evidence_locations,
        list
    ):

        topic_errors.append(
            "evidence_locations is not a list"
        )

    elif len(evidence_locations) == 0:

        topic_errors.append(
            "no evidence locations"
        )

    else:

        previous_location = None


        for evidence in evidence_locations:

            # ----------------------------------------------
            # Structure
            # ----------------------------------------------

            if (
                not isinstance(evidence, dict)
                or "page" not in evidence
                or "line" not in evidence
            ):

                topic_errors.append(
                    "invalid evidence location format"
                )

                continue


            location = (
                evidence["page"],
                evidence["line"]
            )


            # ----------------------------------------------
            # Must exist in transcript
            # ----------------------------------------------

            if location not in valid_transcript_locations:

                topic_errors.append(
                    f"evidence location "
                    f"{evidence['page']}:{evidence['line']} "
                    f"does not exist in transcript"
                )


            # ----------------------------------------------
            # Must be inside topic range
            # ----------------------------------------------

            if not location_in_range(
                evidence,
                start,
                end
            ):

                topic_errors.append(
                    f"evidence location "
                    f"{evidence['page']}:{evidence['line']} "
                    f"is outside topic range"
                )


            # ----------------------------------------------
            # Chronological evidence
            # ----------------------------------------------

            current_key = location_key(
                evidence["page"],
                evidence["line"]
            )


            if (
                previous_location is not None
                and current_key < previous_location
            ):

                topic_errors.append(
                    "evidence locations are not chronological"
                )


            previous_location = current_key


            # ----------------------------------------------
            # Must belong to source chunk
            # ----------------------------------------------

            source_chunks = topic[
                "source_chunks"
            ]

            found_in_source_chunk = False


            for chunk_id in source_chunks:

                if chunk_id not in chunk_locations:

                    topic_errors.append(
                        f"unknown source chunk {chunk_id}"
                    )

                    continue


                if location in chunk_locations[
                    chunk_id
                ]:

                    found_in_source_chunk = True
                    break


            if not found_in_source_chunk:

                topic_errors.append(
                    f"evidence location "
                    f"{evidence['page']}:{evidence['line']} "
                    f"is not present in topic's "
                    f"source chunk(s)"
                )


    # --------------------------------------------------------
    # Validate source chunks
    # --------------------------------------------------------

    source_chunks = topic[
        "source_chunks"
    ]


    if not isinstance(
        source_chunks,
        list
    ):

        topic_errors.append(
            "source_chunks is not a list"
        )

    elif len(source_chunks) == 0:

        topic_errors.append(
            "source_chunks is empty"
        )


    # --------------------------------------------------------
    # Result
    # --------------------------------------------------------

    if topic_errors:

        errors.append(
            {
                "topic_number": index,
                "topic": topic["topic"],
                "errors": topic_errors
            }
        )

        print(
            f"Topic {index}: FAIL - "
            f"{topic['topic']}"
        )

        for error in topic_errors:

            print(
                f"    - {error}"
            )

    else:

        passed += 1

        print(
            f"Topic {index}: PASS - "
            f"{topic['topic']}"
        )


# ============================================================
# Overall result
# ============================================================

validation_passed = (
    len(errors) == 0
)


output = {
    "total_topics": len(topics),
    "passed_topics": passed,
    "failed_topics": len(errors),
    "validation_passed": validation_passed,
    "errors": errors
}


# ============================================================
# Save report
# ============================================================

with open(
    OUTPUT_PATH,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        output,
        f,
        indent=2,
        ensure_ascii=False
    )


# ============================================================
# Summary
# ============================================================

print()
print("=" * 60)

if validation_passed:

    print(
        "GROUNDING VALIDATION: PASS"
    )

else:

    print(
        "GROUNDING VALIDATION: FAIL"
    )

print("=" * 60)

print(
    f"Total topics: {len(topics)}"
)

print(
    f"Passed: {passed}"
)

print(
    f"Failed: {len(errors)}"
)

print()
print(
    f"Saved to {OUTPUT_PATH}"
)