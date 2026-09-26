import json
import re


# ============================================================
# Configuration
# ============================================================

CANDIDATE_PATH = "data/candidate_topics.json"
TRANSCRIPT_PATH = "data/lines.json"
OUTPUT_PATH = "data/grounded_candidate_topics.json"

MAX_EVIDENCE_LOCATIONS = 5


# ============================================================
# Helpers
# ============================================================

def location_key(page, line):
    return page * 1000 + line


def tokenize(text):
    """
    Convert text into normalized lowercase words.
    """
    return set(
        re.findall(
            r"[a-z0-9]+",
            text.lower()
        )
    )


def location_inside_range(location, start, end):
    """
    Check whether a transcript location is inside
    a topic's start/end range.
    """
    key = location_key(
        location["page"],
        location["line"]
    )

    return start <= key <= end


def score_line(evidence_words, line_text):
    """
    Score how much a transcript line overlaps with the
    words contained in the LLM-generated evidence explanation.
    """

    line_words = tokenize(line_text)

    if not evidence_words or not line_words:
        return 0.0

    overlap = evidence_words & line_words

    return len(overlap) / len(evidence_words)


def get_topic_lines(topic, transcript):
    """
    Return transcript lines falling inside the topic range.
    """

    start = location_key(
        topic["start_page"],
        topic["start_line"]
    )

    end = location_key(
        topic["end_page"],
        topic["end_line"]
    )

    topic_lines = []

    for line in transcript:

        location = location_key(
            line["page"],
            line["line"]
        )

        if start <= location <= end:
            topic_lines.append(line)

    return topic_lines


def select_evidence_locations(topic, transcript):
    """
    Select source transcript locations that have the strongest
    lexical overlap with the candidate's evidence explanation.
    """

    evidence_text = topic.get("evidence", "")

    evidence_words = tokenize(evidence_text)

    topic_lines = get_topic_lines(
        topic,
        transcript
    )

    if not topic_lines:
        return []


    # --------------------------------------------------------
    # Score every source line
    # --------------------------------------------------------

    scored_lines = []

    for line in topic_lines:

        score = score_line(
            evidence_words,
            line["text"]
        )

        scored_lines.append(
            (
                score,
                line
            )
        )


    # --------------------------------------------------------
    # Sort by relevance
    # --------------------------------------------------------

    scored_lines.sort(
        key=lambda item: (
            item[0],
            -location_key(
                item[1]["page"],
                item[1]["line"]
            )
        ),
        reverse=True
    )


    # --------------------------------------------------------
    # Select evidence lines
    # --------------------------------------------------------

    selected = []

    for score, line in scored_lines:

        # Ignore lines with no lexical connection
        if score <= 0:
            continue

        selected.append(
            {
                "page": line["page"],
                "line": line["line"]
            }
        )

        if len(selected) >= MAX_EVIDENCE_LOCATIONS:
            break


    # --------------------------------------------------------
    # Return chronological order
    # --------------------------------------------------------

    selected.sort(
        key=lambda location: location_key(
            location["page"],
            location["line"]
        )
    )

    return selected


# ============================================================
# Load input files
# ============================================================

with open(
    CANDIDATE_PATH,
    "r",
    encoding="utf-8"
) as f:
    candidate_data = json.load(f)


with open(
    TRANSCRIPT_PATH,
    "r",
    encoding="utf-8"
) as f:
    transcript = json.load(f)


# ============================================================
# Process candidates
# ============================================================

grounded_topics = []

total_topics = 0
topics_with_evidence = 0
topics_without_evidence = 0


for chunk in candidate_data:

    chunk_id = chunk["chunk_id"]

    for original_topic in chunk.get("topics", []):

        total_topics += 1

        # Create a copy so the original data is untouched
        topic = dict(original_topic)

        # Preserve source chunk
        topic["source_chunks"] = [chunk_id]

        # ----------------------------------------------------
        # Find deterministic source evidence
        # ----------------------------------------------------

        evidence_locations = select_evidence_locations(
            topic,
            transcript
        )

        topic["evidence_locations"] = evidence_locations

        if evidence_locations:
            topics_with_evidence += 1
        else:
            topics_without_evidence += 1

        grounded_topics.append(topic)


# ============================================================
# Save grounded candidates
# ============================================================

output = {
    "topics": grounded_topics
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
# Print summary
# ============================================================

print()
print("Evidence attachment completed.")
print("--------------------------------")
print(f"Candidate topics: {total_topics}")
print(f"Topics with evidence: {topics_with_evidence}")
print(f"Topics without evidence: {topics_without_evidence}")
print()
print(f"Saved to {OUTPUT_PATH}")