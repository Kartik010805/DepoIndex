import json


with open("data/merged_topics_v2.json", "r", encoding="utf-8") as f:
    data = json.load(f)

topics = data["topics"]

print(f"Total topics: {len(topics)}")
print("=" * 80)

for i, topic in enumerate(topics, start=1):
    print(f"\n{i}. {topic['topic']}")
    print(
        f"   Location: "
        f"{topic['start_page']}:{topic['start_line']} "
        f"-> "
        f"{topic['end_page']}:{topic['end_line']}"
    )

    if topic.get("source_chunks"):
        print(f"   Chunks: {topic['source_chunks']}")

    if topic.get("evidence"):
        print(f"   Evidence: {topic['evidence']}")