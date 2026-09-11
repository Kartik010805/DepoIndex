import json


with open("data/lines.json", "r", encoding="utf-8") as f:
    transcript = json.load(f)

with open("data/merged_topics_v2.json", "r", encoding="utf-8") as f:
    data = json.load(f)

topics = data["topics"]


def location_key(page, line):
    return page * 1000 + line


def get_context(page, line, before=2, after=2):
    target = location_key(page, line)

    indexed = []

    for item in transcript:
        key = location_key(item["page"], item["line"])

        if target - before <= key <= target + after:
            indexed.append(item)

    return indexed


for i, topic in enumerate(topics, start=1):

    print("\n" + "=" * 100)
    print(f"TOPIC {i}: {topic['topic']}")
    print(
        f"RANGE: "
        f"{topic['start_page']}:{topic['start_line']} "
        f"-> "
        f"{topic['end_page']}:{topic['end_line']}"
    )
    print("=" * 100)

    print("\n--- START BOUNDARY ---")

    start_context = get_context(
        topic["start_page"],
        topic["start_line"],
        before=3,
        after=3
    )

    for item in start_context:
        marker = "  <-- START" if (
            item["page"] == topic["start_page"]
            and item["line"] == topic["start_line"]
        ) else ""

        print(
            f"[{item['page']}:{item['line']}] "
            f"{item['text']}{marker}"
        )

    print("\n--- END BOUNDARY ---")

    end_context = get_context(
        topic["end_page"],
        topic["end_line"],
        before=3,
        after=3
    )

    for item in end_context:
        marker = "  <-- END" if (
            item["page"] == topic["end_page"]
            and item["line"] == topic["end_line"]
        ) else ""

        print(
            f"[{item['page']}:{item['line']}] "
            f"{item['text']}{marker}"
        )