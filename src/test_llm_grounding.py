import json
import os

from google import genai
from google.genai import types


# ============================================================
# Configuration
# ============================================================

CHUNKS_PATH = "data/chunks.json"
OUTPUT_PATH = "data/test_grounded_result.json"

MODEL = "gemini-3.5-flash-lite"


# ============================================================
# Load chunk 1
# ============================================================

with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
    chunks = json.load(f)

chunk = chunks[0]


# ============================================================
# Gemini client
# ============================================================

api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY environment variable is not set."
    )

client = genai.Client(api_key=api_key)


# ============================================================
# Build grounded prompt
# ============================================================

prompt = """
You are analyzing a legal deposition transcript.

Identify meaningful substantive discussion topics in the
supplied transcript.

IMPORTANT:

The supplied transcript is the ONLY source.

Do not use outside knowledge.

Do not invent facts.

Do not invent page numbers.

Do not invent line numbers.

Every location returned must exactly match a location supplied
in the transcript.


TOPIC RULES:

1. Identify meaningful substantive discussion topics.

2. Ignore routine deposition procedure, introductions,
   greetings, objections, and administrative material.

3. Do not create one topic for every question.

4. Combine consecutive discussion belonging to the same
   substantive subject.

5. A short digression should not automatically create a
   separate topic.

6. Topics may continue across pages.

7. Do not create a topic boundary merely because the chunk
   starts or ends.

8. Return topics chronologically.

9. Keep topic names concise and attorney-friendly.

10. For every topic, provide evidence_locations.

11. Evidence locations must come directly from the supplied
    transcript.

12. Evidence locations must fall inside the topic's
    start/end range.

13. If there is no meaningful substantive topic, return an
    empty topics list.


GROUNDING REQUIREMENT:

Every evidence location must exactly match one of the
[Page X, Line Y] locations supplied below.


Return ONLY valid JSON in this format:

{
  "topics": [
    {
      "topic": "Short topic name",
      "start_page": 0,
      "start_line": 0,
      "end_page": 0,
      "end_line": 0,
      "evidence": "Short explanation supported by the testimony.",
      "evidence_locations": [
        {
          "page": 0,
          "line": 0
        }
      ]
    }
  ]
}


TRANSCRIPT:

"""

for line in chunk["lines"]:
    prompt += (
        f"[Page {line['page']}, Line {line['line']}] "
        f"{line['text']}\n"
    )


# ============================================================
# Call Gemini
# ============================================================

response = client.models.generate_content(
    model=MODEL,
    contents=prompt,
    config=types.GenerateContentConfig(
        temperature=0.2,
        response_mime_type="application/json",
    ),
)


# ============================================================
# Parse JSON
# ============================================================

result = json.loads(response.text)


# ============================================================
# Deterministic grounding validation
# ============================================================

supplied_locations = {
    (line["page"], line["line"])
    for line in chunk["lines"]
}


errors = []


topics = result.get("topics", [])

if not isinstance(topics, list):
    errors.append("'topics' must be a list.")
    topics = []


for index, topic in enumerate(topics, start=1):

    required_fields = [
        "topic",
        "start_page",
        "start_line",
        "end_page",
        "end_line",
        "evidence",
        "evidence_locations",
    ]

    for field in required_fields:

        if field not in topic:

            errors.append(
                f"Topic {index}: missing '{field}'."
            )

    if any(field not in topic for field in required_fields):
        continue


    # --------------------------------------------------------
    # Topic range
    # --------------------------------------------------------

    start = (
        topic["start_page"],
        topic["start_line"]
    )

    end = (
        topic["end_page"],
        topic["end_line"]
    )


    if start not in supplied_locations:

        errors.append(
            f"Topic {index}: invalid start location {start}."
        )


    if end not in supplied_locations:

        errors.append(
            f"Topic {index}: invalid end location {end}."
        )


    if start > end:

        errors.append(
            f"Topic {index}: start is after end."
        )


    # --------------------------------------------------------
    # Evidence locations
    # --------------------------------------------------------

    evidence_locations = topic["evidence_locations"]


    if not isinstance(evidence_locations, list):

        errors.append(
            f"Topic {index}: evidence_locations is not a list."
        )

        continue


    if not evidence_locations:

        errors.append(
            f"Topic {index}: no evidence locations."
        )

        continue


    for evidence in evidence_locations:

        if (
            not isinstance(evidence, dict)
            or "page" not in evidence
            or "line" not in evidence
        ):

            errors.append(
                f"Topic {index}: invalid evidence location."
            )

            continue


        location = (
            evidence["page"],
            evidence["line"]
        )


        # Must exist in supplied transcript
        if location not in supplied_locations:

            errors.append(
                f"Topic {index}: evidence location "
                f"{location} is not in supplied transcript."
            )


        # Must fall inside topic range
        if location < start or location > end:

            errors.append(
                f"Topic {index}: evidence location "
                f"{location} is outside topic range."
            )


# ============================================================
# Save result
# ============================================================

output = {
    "chunk_id": chunk["chunk_id"],
    "topics": result.get("topics", []),
    "validation": {
        "passed": len(errors) == 0,
        "errors": errors
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
# Print result
# ============================================================

if errors:

    print("\nGrounding validation FAILED.")

    for error in errors:
        print(f"- {error}")

else:

    print("\nGrounding validation PASSED.")


print(
    f"Topics returned: {len(result.get('topics', []))}"
)

print(
    f"Saved to {OUTPUT_PATH}"
)