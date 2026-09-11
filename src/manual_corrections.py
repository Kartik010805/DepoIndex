import json


INPUT_FILE = "data/merged_topics_v2.json"
OUTPUT_FILE = "data/manual_corrected_topics.json"


def set_range(
    topic,
    start_page=None,
    start_line=None,
    end_page=None,
    end_line=None
):
    if start_page is not None:
        topic["start_page"] = start_page

    if start_line is not None:
        topic["start_line"] = start_line

    if end_page is not None:
        topic["end_page"] = end_page

    if end_line is not None:
        topic["end_line"] = end_line


with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)


original_topics = data["topics"]

corrected_topics = []


for original_number, topic in enumerate(original_topics, start=1):

    if original_number == 2:
        set_range(
            topic,
            end_page=13,
            end_line=17
        )

    elif original_number == 8:
        set_range(
            topic,
            end_page=23,
            end_line=7
        )

    elif original_number == 14:
        set_range(
            topic,
            start_page=27,
            start_line=2,
            end_page=27,
            end_line=12
        )

    elif original_number == 15:
        set_range(
            topic,
            start_page=27,
            start_line=13
        )

    elif original_number == 16:
        set_range(
            topic,
            end_page=34,
            end_line=8
        )

    elif original_number == 17:
        set_range(
            topic,
            start_page=34,
            start_line=9
        )

    elif original_number == 18:
        set_range(
            topic,
            end_page=36,
            end_line=2
        )

    elif original_number == 20:
        topic21 = original_topics[20]

        topic["end_page"] = topic21["end_page"]
        topic["end_line"] = topic21["end_line"]

        existing_chunks = topic.get("source_chunks", [])
        next_chunks = topic21.get("source_chunks", [])

        topic["source_chunks"] = sorted(
            set(existing_chunks + next_chunks)
        )

        topic["evidence"] = (
            "Continuous discussion of ITT degree value and "
            "post-graduation earnings hypotheticals, including "
            "whether unusually large salary increases would be "
            "outliers and how those outcomes should be interpreted."
        )

    elif original_number == 21:
        continue

    elif original_number == 28:
        set_range(
            topic,
            end_page=58,
            end_line=7
        )

    elif original_number == 29:
        set_range(
            topic,
            start_page=58,
            start_line=8
        )

    elif original_number == 30:
        set_range(
            topic,
            end_page=64,
            end_line=22
        )

    elif original_number == 32:
        set_range(
            topic,
            end_page=68,
            end_line=2
        )

    elif original_number == 34:
        set_range(
            topic,
            end_page=68,
            end_line=25
        )

    elif original_number == 36:
        set_range(
            topic,
            end_page=74,
            end_line=12
        )

    elif original_number == 41:
        set_range(
            topic,
            end_page=84,
            end_line=9
        )

    corrected_topics.append(topic)


output = {
    "topics": corrected_topics
}


with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(
        output,
        f,
        indent=2,
        ensure_ascii=False
    )


print("Manual corrections completed.")
print(f"Original topics: {len(original_topics)}")
print(f"Final topics: {len(corrected_topics)}")
print(f"Saved to {OUTPUT_FILE}")