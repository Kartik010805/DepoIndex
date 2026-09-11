import json


def location_key(page, line):
    return page * 1000 + line


# Load the extracted transcript
with open("data/lines.json", "r", encoding="utf-8") as f:
    transcript = json.load(f)


# Load the final manually corrected topics
with open("data/manual_corrected_topics.json", "r", encoding="utf-8") as f:
    data = json.load(f)


topics = data["topics"]


# Create a set of every valid page:line location in the transcript
valid_locations = {
    location_key(item["page"], item["line"])
    for item in transcript
}


errors = []
previous_start = None


for i, topic in enumerate(topics, start=1):

    required_fields = [
        "topic",
        "start_page",
        "start_line",
        "end_page",
        "end_line"
    ]

    # Check required fields
    for field in required_fields:
        if field not in topic:
            errors.append(
                f"Topic {i}: missing required field '{field}'"
            )

    if any(field not in topic for field in required_fields):
        continue


    # Convert start and end locations to comparable numbers
    start = location_key(
        topic["start_page"],
        topic["start_line"]
    )

    end = location_key(
        topic["end_page"],
        topic["end_line"]
    )


    # Check whether start location actually exists
    if start not in valid_locations:
        errors.append(
            f"Topic {i}: invalid start location "
            f"{topic['start_page']}:{topic['start_line']}"
        )


    # Check whether end location actually exists
    if end not in valid_locations:
        errors.append(
            f"Topic {i}: invalid end location "
            f"{topic['end_page']}:{topic['end_line']}"
        )


    # Start cannot occur after end
    if start > end:
        errors.append(
            f"Topic {i}: start is after end"
        )


    # Topics should appear chronologically
    if previous_start is not None and start < previous_start:
        errors.append(
            f"Topic {i}: topics are not in chronological order"
        )


    previous_start = start


print(f"Topics checked: {len(topics)}")


if errors:

    print("\nValidation errors found:")

    for error in errors:
        print(f"- {error}")

else:

    print("\nAll final topics passed deterministic validation.")