import json
import re


def location_key(page, line):
    return page * 1000 + line


def range_length(topic):
    start = location_key(topic["start_page"], topic["start_line"])
    end = location_key(topic["end_page"], topic["end_line"])
    return end - start + 1


def overlap_length(a, b):
    start = max(
        location_key(a["start_page"], a["start_line"]),
        location_key(b["start_page"], b["start_line"])
    )
    end = min(
        location_key(a["end_page"], a["end_line"]),
        location_key(b["end_page"], b["end_line"])
    )

    if start > end:
        return 0

    return end - start + 1


def normalize(text):
    words = re.findall(r"[a-z0-9]+", text.lower())
    return set(words)


def similarity(a, b):
    words_a = normalize(a)
    words_b = normalize(b)

    if not words_a or not words_b:
        return 0

    return len(words_a & words_b) / len(words_a | words_b)


def labels_similar(a, b):
    label_score = similarity(a["topic"], b["topic"])
    evidence_score = similarity(
        a.get("evidence", ""),
        b.get("evidence", "")
    )

    return label_score >= 0.30 or evidence_score >= 0.25


def should_merge(a, b):
    overlap = overlap_length(a, b)

    if overlap == 0:
        return False

    smaller_range = min(range_length(a), range_length(b))

    overlap_ratio = overlap / smaller_range

    if overlap_ratio < 0.20:
        return False

    return labels_similar(a, b)


def merge_topics(a, b):
    start = min(
        (a["start_page"], a["start_line"]),
        (b["start_page"], b["start_line"])
    )

    end = max(
        (a["end_page"], a["end_line"]),
        (b["end_page"], b["end_line"])
    )

    merged = {
        "topic": a["topic"],
        "start_page": start[0],
        "start_line": start[1],
        "end_page": end[0],
        "end_line": end[1],
        "evidence": a.get("evidence", "")
    }

    chunks = set(a.get("source_chunks", []))
    chunks.update(b.get("source_chunks", []))
    merged["source_chunks"] = sorted(chunks)

    return merged


with open("data/candidate_topics.json", "r", encoding="utf-8") as f:
    data = json.load(f)

candidates = []

for item in data:
    for topic in item.get("topics", []):
        topic["source_chunks"] = [item["chunk_id"]]
        candidates.append(topic)

candidates.sort(
    key=lambda x: (
        x["start_page"],
        x["start_line"],
        x["end_page"],
        x["end_line"]
    )
)

merged = []

for candidate in candidates:
    if not merged:
        merged.append(candidate)
        continue

    previous = merged[-1]

    if should_merge(previous, candidate):
        merged[-1] = merge_topics(previous, candidate)
    else:
        merged.append(candidate)

with open("data/merged_topics_v2.json", "w", encoding="utf-8") as f:
    json.dump(
        {"topics": merged},
        f,
        indent=2,
        ensure_ascii=False
    )

print(f"Candidate topics: {len(candidates)}")
print(f"Merged topics: {len(merged)}")
print("Saved to data/merged_topics_v2.json")