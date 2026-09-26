import json


# ============================================================
# Configuration
# ============================================================

INPUT_PATH = "data/grounded_candidate_topics.json"
TRANSCRIPT_PATH = "data/lines.json"
OUTPUT_PATH = "data/grounded_candidate_topics_repaired.json"


# ============================================================
# Helpers
# ============================================================

def location_key(page, line):
    return page * 1000 + line


def get_valid_lines_on_page(transcript, page):
    """
    Return all valid transcript lines on a specific page,
    sorted by line number.
    """

    lines = [
        item
        for item in transcript
        if item["page"] == page
    ]

    lines.sort(
        key=lambda item: item["line"]
    )

    return lines


def repair_boundary(page, line, transcript, boundary_type):
    """
    Repair an invalid page/line boundary.

    If the page exists, use the nearest valid transcript line
    on that page.

    For an end boundary, use the last valid line on the page.

    For a start boundary, use the first valid line on the page.
    """

    page_lines = get_valid_lines_on_page(
        transcript,
        page
    )

    if not page_lines:
        return None

    if boundary_type == "start":

        return {
            "page": page_lines[0]["page"],
            "line": page_lines[0]["line"]
        }

    return {
        "page": page_lines[-1]["page"],
        "line": page_lines[-1]["line"]
    }


# ============================================================
# Load files
# ============================================================

with open(
    INPUT_PATH,
    "r",
    encoding="utf-8"
) as f:
    data = json.load(f)


with open(
    TRANSCRIPT_PATH,
    "r",
    encoding="utf-8"
) as f:
    transcript = json.load(f)


# ============================================================
# Valid transcript locations
# ============================================================

valid_locations = {
    (
        item["page"],
        item["line"]
    )
    for item in transcript
}


# ============================================================
# Repair topics
# ============================================================

topics = data["topics"]

repairs = []


for index, topic in enumerate(
    topics,
    start=1
):

    # --------------------------------------------------------
    # Check start boundary
    # --------------------------------------------------------

    start = (
        topic["start_page"],
        topic["start_line"]
    )

    if start not in valid_locations:

        repaired = repair_boundary(
            topic["start_page"],
            topic["start_line"],
            transcript,
            "start"
        )

        if repaired is not None:

            old_value = (
                topic["start_page"],
                topic["start_line"]
            )

            topic["start_page"] = repaired["page"]
            topic["start_line"] = repaired["line"]

            repairs.append(
                {
                    "topic_number": index,
                    "topic": topic["topic"],
                    "boundary": "start",
                    "old": {
                        "page": old_value[0],
                        "line": old_value[1]
                    },
                    "new": repaired
                }
            )


    # --------------------------------------------------------
    # Check end boundary
    # --------------------------------------------------------

    end = (
        topic["end_page"],
        topic["end_line"]
    )

    if end not in valid_locations:

        repaired = repair_boundary(
            topic["end_page"],
            topic["end_line"],
            transcript,
            "end"
        )

        if repaired is not None:

            old_value = (
                topic["end_page"],
                topic["end_line"]
            )

            topic["end_page"] = repaired["page"]
            topic["end_line"] = repaired["line"]

            repairs.append(
                {
                    "topic_number": index,
                    "topic": topic["topic"],
                    "boundary": "end",
                    "old": {
                        "page": old_value[0],
                        "line": old_value[1]
                    },
                    "new": repaired
                }
            )


# ============================================================
# Save repaired data
# ============================================================

output = {
    "topics": topics,
    "repairs": repairs
}


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
# Print report
# ============================================================

print()
print("=" * 60)
print("TOPIC BOUNDARY REPAIR")
print("=" * 60)

print(
    f"Topics checked: {len(topics)}"
)

print(
    f"Boundaries repaired: {len(repairs)}"
)

print()


if repairs:

    for repair in repairs:

        print(
            f"Topic {repair['topic_number']}: "
            f"{repair['topic']}"
        )

        print(
            f"  Boundary: {repair['boundary']}"
        )

        print(
            f"  Old: "
            f"{repair['old']['page']}:"
            f"{repair['old']['line']}"
        )

        print(
            f"  New: "
            f"{repair['new']['page']}:"
            f"{repair['new']['line']}"
        )

        print()

else:

    print("No invalid boundaries found.")


print(
    f"Saved to {OUTPUT_PATH}"
)