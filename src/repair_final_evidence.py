import json
from pathlib import Path
import re


INPUT_PATH = Path("data/final_grounded_topics.json")
LINES_PATH = Path("data/lines.json")
OUTPUT_PATH = Path("data/final_grounded_topics_repaired.json")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def normalize_tokens(text):
    if not text:
        return set()

    return set(
        re.findall(r"\b[a-z0-9]+\b", text.lower())
    )


def location_key(item):
    return (
        int(item["page"]),
        int(item["line"])
    )


def inside_range(location, start, end):
    return start <= location <= end


def score_line(line_text, evidence_tokens):
    line_tokens = normalize_tokens(line_text)

    if not line_tokens or not evidence_tokens:
        return 0

    return len(
        line_tokens.intersection(evidence_tokens)
    )


def extract_topic_list(data):
    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for key in [
            "topics",
            "final_topics",
            "merged_topics",
            "candidate_topics",
            "data"
        ]:
            value = data.get(key)

            if isinstance(value, list):
                return value

    raise ValueError(
        "Could not find a topic list in final_grounded_topics.json"
    )


def main():

    print()
    print("=" * 60)
    print("FINAL EVIDENCE REPAIR")
    print("=" * 60)

    raw_data = load_json(INPUT_PATH)
    topics = extract_topic_list(raw_data)

    lines = load_json(LINES_PATH)

    print(f"Topics checked: {len(topics)}")

    repaired_count = 0

    for index, topic in enumerate(topics, start=1):

        if not isinstance(topic, dict):
            raise ValueError(
                f"Topic {index} is not a JSON object."
            )

        start = (
            int(topic["start_page"]),
            int(topic["start_line"])
        )

        end = (
            int(topic["end_page"]),
            int(topic["end_line"])
        )

        evidence_text = topic.get("evidence", "")
        evidence_tokens = normalize_tokens(evidence_text)

        candidates = []

        for line in lines:

            location = location_key(line)

            if not inside_range(location, start, end):
                continue

            score = score_line(
                line.get("text", ""),
                evidence_tokens
            )

            if score > 0:
                candidates.append(
                    (
                        score,
                        location,
                        line
                    )
                )

        # Highest lexical overlap first.
        candidates.sort(
            key=lambda x: (-x[0], x[1])
        )

        selected = candidates[:5]

        # IMPORTANT:
        # After selecting the strongest evidence lines,
        # always sort the final evidence locations
        # chronologically.
        selected.sort(
            key=lambda x: x[1]
        )

        selected_locations = [
            {
                "page": item[1][0],
                "line": item[1][1]
            }
            for item in selected
        ]

        # Fallback if no lexical match exists.
        if not selected_locations:

            fallback = []

            for line in lines:

                location = location_key(line)

                if inside_range(
                    location,
                    start,
                    end
                ):
                    fallback.append(location)

                if len(fallback) == 5:
                    break

            fallback.sort()

            selected_locations = [
                {
                    "page": location[0],
                    "line": location[1]
                }
                for location in fallback
            ]

        old_locations = topic.get(
            "evidence_locations",
            []
        )

        # Check whether old evidence is valid.
        old_valid = True
        old_previous = None

        for old in old_locations:

            try:
                old_location = (
                    int(old["page"]),
                    int(old["line"])
                )
            except (KeyError, TypeError, ValueError):
                old_valid = False
                break

            if not inside_range(
                old_location,
                start,
                end
            ):
                old_valid = False
                break

            if (
                old_previous is not None
                and old_location < old_previous
            ):
                old_valid = False
                break

            old_previous = old_location

        if not old_valid:

            repaired_count += 1

            print()
            print(
                f"Topic {index}: "
                f"{topic.get('topic', '<missing topic>')}"
            )

            print(
                f"  Evidence: "
                f"{len(old_locations)} -> "
                f"{len(selected_locations)}"
            )

            print(
                f"  New evidence: "
                f"{selected_locations}"
            )

            topic["evidence_locations"] = (
                selected_locations
            )

    # Save ONLY the list of 43 topics.
    save_json(
        OUTPUT_PATH,
        topics
    )

    print()
    print(
        f"Topics repaired: {repaired_count}"
    )

    print()
    print(
        f"Saved to {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()