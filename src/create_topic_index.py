import json


INPUT_FILE = "data/manual_corrected_topics.json"
OUTPUT_FILE = "data/topic_index.md"


with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)


topics = data["topics"]


with open(OUTPUT_FILE, "w", encoding="utf-8") as f:

    f.write("# DepoIndex — Topic Index\n\n")

    f.write(
        "Chronological index of meaningful deposition topics "
        "with attorney-verifiable transcript locations.\n\n"
    )

    f.write(f"**Total topics:** {len(topics)}\n\n")

    f.write("---\n\n")

    for i, topic in enumerate(topics, start=1):

        f.write(f"## {i}. {topic['topic']}\n\n")

        f.write(
            f"**Start:** "
            f"{topic['start_page']}:{topic['start_line']}\n\n"
        )

        f.write(
            f"**End:** "
            f"{topic['end_page']}:{topic['end_line']}\n\n"
        )

        if topic.get("evidence"):
            f.write(
                f"**Supporting Evidence:** "
                f"{topic['evidence']}\n\n"
            )

        if topic.get("source_chunks"):
            chunks = ", ".join(
                str(chunk)
                for chunk in topic["source_chunks"]
            )

            f.write(
                f"**Source Chunks:** {chunks}\n\n"
            )

        f.write("---\n\n")


print("Topic Index created.")
print(f"Topics written: {len(topics)}")
print(f"Saved to {OUTPUT_FILE}")