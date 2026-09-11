import json

LINES_PATH = "data/lines.json"
RESULT_PATH = "data/test_result.json"

with open(LINES_PATH, "r", encoding="utf-8") as f:
    lines = json.load(f)

with open(RESULT_PATH, "r", encoding="utf-8") as f:
    result = json.load(f)

valid_locations = {
    (line["page"], line["line"])
    for line in lines
}

topics = result.get("topics", [])

print(f"Topics to validate: {len(topics)}")

all_valid = True

for i, topic in enumerate(topics, start=1):
    start = (topic["start_page"], topic["start_line"])
    end = (topic["end_page"], topic["end_line"])

    start_valid = start in valid_locations
    end_valid = end in valid_locations

    print(f"\nTopic {i}: {topic['topic']}")
    print(
        f"  Start: {start[0]}:{start[1]} "
        f"-> {'VALID' if start_valid else 'INVALID'}"
    )
    print(
        f"  End:   {end[0]}:{end[1]} "
        f"-> {'VALID' if end_valid else 'INVALID'}"
    )

    if not start_valid or not end_valid:
        all_valid = False

if all_valid:
    print("\nAll topic boundaries reference valid transcript locations.")
else:
    print("\nSome topic boundaries are invalid.")
