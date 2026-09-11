import json


TOPICS_FILE = "data/manual_corrected_topics.json"
TRANSCRIPT_FILE = "data/lines.json"


with open(TOPICS_FILE, "r", encoding="utf-8") as f:
    topics = json.load(f)["topics"]

with open(TRANSCRIPT_FILE, "r", encoding="utf-8") as f:
    transcript = json.load(f)


# Select 20 representative topics.
# These include early, middle, late, overlapping, and manually corrected cases.
selected_indices = [
    1, 2, 3, 5, 6,
    7, 8, 9, 10, 11,
    14, 15, 16, 17, 18,
    19, 20, 22, 28, 29
]


transcript_lookup = {
    (item["page"], item["line"]): item["text"]
    for item in transcript
}


def get_nearby_lines(page, line, radius=2):
    nearby = []

    target = page * 1000 + line

    for item in transcript:
        current = item["page"] * 1000 + item["line"]

        if abs(current - target) <= radius:
            nearby.append(item)

    return nearby


print("=" * 80)
print("DEPOINDEX MANUAL VALIDATION")
print("=" * 80)

print()
print("Review the 20 selected topics for:")
print("1. Location accuracy")
print("2. Topic relevance")
print("3. Boundary quality")
print("4. Redundancy")
print()


for number, topic_index in enumerate(selected_indices, start=1):

    topic = topics[topic_index - 1]

    start_page = topic["start_page"]
    start_line = topic["start_line"]

    end_page = topic["end_page"]
    end_line = topic["end_line"]

    print()
    print("=" * 80)
    print(f"MANUAL REVIEW {number}/20")
    print("=" * 80)

    print(f"Topic: {topic['topic']}")

    print(
        f"Range: "
        f"{start_page}:{start_line} -> "
        f"{end_page}:{end_line}"
    )

    print()
    print(f"Evidence: {topic.get('evidence', '')}")

    print()
    print("--- START BOUNDARY ---")

    start_lines = get_nearby_lines(
        start_page,
        start_line
    )

    for item in start_lines:
        marker = ""

        if (
            item["page"] == start_page
            and item["line"] == start_line
        ):
            marker = "  <--- TOPIC START"

        print(
            f"{item['page']}:{item['line']} "
            f"{item['text']}{marker}"
        )

    print()
    print("--- END BOUNDARY ---")

    end_lines = get_nearby_lines(
        end_page,
        end_line
    )

    for item in end_lines:
        marker = ""

        if (
            item["page"] == end_page
            and item["line"] == end_line
        ):
            marker = "  <--- TOPIC END"

        print(
            f"{item['page']}:{item['line']} "
            f"{item['text']}{marker}"
        )

    print()
    print("Manual decision:")
    print("[ ] PASS")
    print("[ ] NEEDS CORRECTION")
    print()
    