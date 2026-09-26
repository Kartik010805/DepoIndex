import json
import re


# ============================================================
# Configuration
# ============================================================

INPUT_PATH = "data/grounded_candidate_topics_repaired.json"
OUTPUT_PATH = "data/grounded_merged_topics.json"


# ============================================================
# Location helpers
# ============================================================

def location_key(page, line):
    return page * 1000 + line


def range_length(topic):
    start = location_key(
        topic["start_page"],
        topic["start_line"]
    )

    end = location_key(
        topic["end_page"],
        topic["end_line"]
    )

    return end - start + 1


def overlap_length(a, b):
    start = max(
        location_key(
            a["start_page"],
            a["start_line"]
        ),
        location_key(
            b["start_page"],
            b["start_line"]
        )
    )

    end = min(
        location_key(
            a["end_page"],
            a["end_line"]
        ),
        location_key(
            b["end_page"],
            b["end_line"]
        )
    )

    if start > end:
        return 0

    return end - start + 1


# ============================================================
# Text similarity
# ============================================================

def normalize(text):
    words = re.findall(
        r"[a-z0-9]+",
        text.lower()
    )

    return set(words)


def similarity(a, b):
    words_a = normalize(a)
    words_b = normalize(b)

    if not words_a or not words_b:
        return 0

    return len(
        words_a & words_b
    ) / len(
        words_a | words_b
    )


def labels_similar(a, b):

    label_score = similarity(
        a.get("topic", ""),
        b.get("topic", "")
    )

    evidence_score = similarity(
        a.get("evidence", ""),
        b.get("evidence", "")
    )

    return (
        label_score >= 0.30
        or evidence_score >= 0.25
    )


# ============================================================
# Decide whether two candidates should merge
# ============================================================

def should_merge(a, b):

    overlap = overlap_length(a, b)

    if overlap == 0:
        return False

    smaller_range = min(
        range_length(a),
        range_length(b)
    )

    overlap_ratio = (
        overlap / smaller_range
    )

    if overlap_ratio < 0.20:
        return False

    return labels_similar(a, b)


# ============================================================
# Merge two topics
# ============================================================

def merge_topics(a, b):

    start = min(
        (
            a["start_page"],
            a["start_line"]
        ),
        (
            b["start_page"],
            b["start_line"]
        )
    )

    end = max(
        (
            a["end_page"],
            a["end_line"]
        ),
        (
            b["end_page"],
            b["end_line"]
        )
    )


    # --------------------------------------------------------
    # Basic merged topic
    # --------------------------------------------------------

    merged = {
        "topic": a["topic"],

        "start_page": start[0],
        "start_line": start[1],

        "end_page": end[0],
        "end_line": end[1],

        "evidence": a.get(
            "evidence",
            ""
        )
    }


    # --------------------------------------------------------
    # Preserve source chunks
    # --------------------------------------------------------

    source_chunks = set(
        a.get(
            "source_chunks",
            []
        )
    )

    source_chunks.update(
        b.get(
            "source_chunks",
            []
        )
    )

    merged["source_chunks"] = sorted(
        source_chunks
    )


    # --------------------------------------------------------
    # Preserve evidence locations
    # --------------------------------------------------------

    evidence_locations = []

    for item in a.get(
        "evidence_locations",
        []
    ):

        if (
            "page" in item
            and "line" in item
        ):

            evidence_locations.append(
                {
                    "page": item["page"],
                    "line": item["line"]
                }
            )


    for item in b.get(
        "evidence_locations",
        []
    ):

        if (
            "page" in item
            and "line" in item
        ):

            evidence_locations.append(
                {
                    "page": item["page"],
                    "line": item["line"]
                }
            )


    # --------------------------------------------------------
    # Remove duplicate evidence locations
    # --------------------------------------------------------

    unique_locations = {
        (
            item["page"],
            item["line"]
        )
        for item in evidence_locations
    }


    merged["evidence_locations"] = [
        {
            "page": page,
            "line": line
        }
        for page, line in sorted(
            unique_locations
        )
    ]


    return merged


# ============================================================
# Load grounded candidates
# ============================================================

with open(
    INPUT_PATH,
    "r",
    encoding="utf-8"
) as f:

    data = json.load(f)


# ============================================================
# Flatten candidates
# ============================================================

candidates = []


for topic in data.get(
    "topics",
    []
):

    candidates.append(
        topic
    )


# ============================================================
# Sort chronologically
# ============================================================

candidates.sort(
    key=lambda x: (
        x["start_page"],
        x["start_line"],
        x["end_page"],
        x["end_line"]
    )
)


# ============================================================
# Merge overlapping candidates
# ============================================================

merged = []


for candidate in candidates:

    if not merged:

        merged.append(
            candidate
        )

        continue


    previous = merged[-1]


    if should_merge(
        previous,
        candidate
    ):

        merged[-1] = merge_topics(
            previous,
            candidate
        )

    else:

        merged.append(
            candidate
        )


# ============================================================
# Save result
# ============================================================

with open(
    OUTPUT_PATH,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        {
            "topics": merged
        },
        f,
        indent=2,
        ensure_ascii=False
    )


# ============================================================
# Summary
# ============================================================

print()
print("=" * 60)
print("GROUNDED TOPIC MERGING")
print("=" * 60)

print(
    f"Grounded candidate topics: "
    f"{len(candidates)}"
)

print(
    f"Merged topics: "
    f"{len(merged)}"
)

print()

print(
    f"Saved to {OUTPUT_PATH}"
)