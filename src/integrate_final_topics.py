import json
import re


# ============================================================
# Configuration
# ============================================================

MANUAL_PATH = "data/manual_corrected_topics.json"
GROUNDED_PATH = "data/grounded_merged_topics.json"

OUTPUT_PATH = "data/final_grounded_topics.json"


# ============================================================
# Location helpers
# ============================================================

def location_key(page, line):
    return page * 1000 + line


def range_overlap(a, b):
    """
    Calculate the number of transcript locations
    overlapping between two topic ranges.
    """

    a_start = location_key(
        a["start_page"],
        a["start_line"]
    )

    a_end = location_key(
        a["end_page"],
        a["end_line"]
    )

    b_start = location_key(
        b["start_page"],
        b["start_line"]
    )

    b_end = location_key(
        b["end_page"],
        b["end_line"]
    )

    start = max(a_start, b_start)
    end = min(a_end, b_end)

    if start > end:
        return 0

    return end - start + 1


def range_size(topic):
    start = location_key(
        topic["start_page"],
        topic["start_line"]
    )

    end = location_key(
        topic["end_page"],
        topic["end_line"]
    )

    return end - start + 1


# ============================================================
# Text normalization
# ============================================================

def normalize(text):
    return set(
        re.findall(
            r"[a-z0-9]+",
            text.lower()
        )
    )


def text_similarity(a, b):
    words_a = normalize(a)
    words_b = normalize(b)

    if not words_a or not words_b:
        return 0.0

    return len(
        words_a & words_b
    ) / len(
        words_a | words_b
    )


# ============================================================
# Topic similarity
# ============================================================

def topic_similarity(manual, grounded):

    name_score = text_similarity(
        manual.get("topic", ""),
        grounded.get("topic", "")
    )

    evidence_score = text_similarity(
        manual.get("evidence", ""),
        grounded.get("evidence", "")
    )

    overlap = range_overlap(
        manual,
        grounded
    )

    manual_size = range_size(manual)
    grounded_size = range_size(grounded)

    smaller_size = min(
        manual_size,
        grounded_size
    )

    if smaller_size > 0:
        overlap_ratio = (
            overlap / smaller_size
        )
    else:
        overlap_ratio = 0.0

    # Weighted score:
    #
    # Topic name similarity = strongest signal
    # Evidence similarity   = supporting signal
    # Range overlap         = boundary/context signal

    score = (
        name_score * 0.60
        + evidence_score * 0.20
        + overlap_ratio * 0.20
    )

    return score


# ============================================================
# Metadata helper
# ============================================================

def propagate_metadata(final_topic, grounded_topic):
    """
    Copy metadata from the grounded source into the final topic.

    The grounded metadata is source-derived deposition metadata.
    Missing values remain missing; nothing is inferred.
    """

    if "metadata" in grounded_topic:
        final_topic["metadata"] = grounded_topic["metadata"]

    return final_topic


# ============================================================
# Load files
# ============================================================

with open(
    MANUAL_PATH,
    "r",
    encoding="utf-8"
) as f:
    manual_data = json.load(f)


with open(
    GROUNDED_PATH,
    "r",
    encoding="utf-8"
) as f:
    grounded_data = json.load(f)


manual_topics = manual_data["topics"]
grounded_topics = grounded_data["topics"]


# ============================================================
# Match manual topics to grounded topics
# ============================================================

matches = []
unmatched = []

used_grounded = set()


for manual_index, manual_topic in enumerate(
    manual_topics,
    start=1
):

    candidates = []

    for grounded_index, grounded_topic in enumerate(
        grounded_topics
    ):

        if grounded_index in used_grounded:
            continue

        overlap = range_overlap(
            manual_topic,
            grounded_topic
        )

        if overlap == 0:
            continue

        score = topic_similarity(
            manual_topic,
            grounded_topic
        )

        candidates.append(
            (
                score,
                overlap,
                grounded_index,
                grounded_topic
            )
        )

    # --------------------------------------------------------
    # Sort by similarity
    # --------------------------------------------------------

    candidates.sort(
        key=lambda item: (
            item[0],
            item[1]
        ),
        reverse=True
    )

    if not candidates:

        unmatched.append(
            {
                "manual_topic_number": manual_index,
                "topic": manual_topic["topic"],
                "reason": "No overlapping grounded topic"
            }
        )

        continue

    best_score, best_overlap, best_index, best_topic = (
        candidates[0]
    )

    # --------------------------------------------------------
    # Minimum matching requirements
    # --------------------------------------------------------

    name_score = text_similarity(
        manual_topic.get("topic", ""),
        best_topic.get("topic", "")
    )

    evidence_score = text_similarity(
        manual_topic.get("evidence", ""),
        best_topic.get("evidence", "")
    )

    if (
        name_score < 0.15
        and evidence_score < 0.20
    ):

        unmatched.append(
            {
                "manual_topic_number": manual_index,
                "topic": manual_topic["topic"],
                "reason": "Best candidate similarity too low",
                "best_candidate": best_topic["topic"],
                "score": round(
                    best_score,
                    4
                )
            }
        )

        continue

    # --------------------------------------------------------
    # Match accepted
    # --------------------------------------------------------

    used_grounded.add(
        best_index
    )

    matches.append(
        {
            "manual_index": manual_index,
            "grounded_index": best_index,
            "score": best_score,
            "overlap": best_overlap,
            "manual_topic": manual_topic,
            "grounded_topic": best_topic
        }
    )


# ============================================================
# Build final topics
# ============================================================

final_topics = []


for match in matches:

    manual_topic = match[
        "manual_topic"
    ]

    grounded_topic = match[
        "grounded_topic"
    ]

    # --------------------------------------------------------
    # Manual topic is authoritative
    # --------------------------------------------------------

    final_topic = dict(
        manual_topic
    )

    # --------------------------------------------------------
    # Add grounded evidence locations
    # --------------------------------------------------------

    final_topic[
        "evidence_locations"
    ] = [
        {
            "page": item["page"],
            "line": item["line"]
        }
        for item in grounded_topic.get(
            "evidence_locations",
            []
        )
    ]

    # --------------------------------------------------------
    # Combine source chunks
    # --------------------------------------------------------

    manual_chunks = set(
        manual_topic.get(
            "source_chunks",
            []
        )
    )

    grounded_chunks = set(
        grounded_topic.get(
            "source_chunks",
            []
        )
    )

    final_topic[
        "source_chunks"
    ] = sorted(
        manual_chunks
        | grounded_chunks
    )

    # --------------------------------------------------------
    # Propagate grounded metadata
    # --------------------------------------------------------

    propagate_metadata(
        final_topic,
        grounded_topic
    )

    # --------------------------------------------------------
    # Grounding source
    # --------------------------------------------------------

    final_topic[
        "grounding_source"
    ] = "grounded_merged_topics"

    final_topics.append(
        final_topic
    )


# ============================================================
# Restore manual chronological order
# ============================================================

final_topics.sort(
    key=lambda topic: (
        topic["start_page"],
        topic["start_line"]
    )
)


# ============================================================
# Save result
# ============================================================

output = {
    "topics": final_topics,

    "integration": {
        "manual_topics": len(
            manual_topics
        ),

        "grounded_topics": len(
            grounded_topics
        ),

        "final_topics": len(
            final_topics
        ),

        "matched_topics": len(
            matches
        ),

        "unmatched_topics": len(
            unmatched
        ),

        "unmatched_details": unmatched
    }
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
# Report
# ============================================================

print()
print("=" * 60)
print("FINAL TOPIC INTEGRATION")
print("=" * 60)

print(
    f"Manual topics: {len(manual_topics)}"
)

print(
    f"Grounded merged topics: {len(grounded_topics)}"
)

print(
    f"Matched topics: {len(matches)}"
)

print(
    f"Unmatched topics: {len(unmatched)}"
)

print(
    f"Final topics: {len(final_topics)}"
)

metadata_count = sum(
    1
    for topic in final_topics
    if "metadata" in topic
)

print(
    f"Topics with metadata: "
    f"{metadata_count}/{len(final_topics)}"
)

print()

if unmatched:

    print("UNMATCHED TOPICS:")

    for item in unmatched:

        print(
            f"  Topic {item['manual_topic_number']}: "
            f"{item['topic']}"
        )

        print(
            f"    Reason: {item['reason']}"
        )

else:

    print(
        "All manual topics successfully "
        "received grounded evidence."
    )


print()
print(
    f"Saved to {OUTPUT_PATH}"
)
