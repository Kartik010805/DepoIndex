import json
import os
import time

from google import genai
from google.genai import types


# ============================================================
# Configuration
# ============================================================

INPUT_PATH = "data/chunks.json"
OUTPUT_PATH = "data/candidate_topics.json"

MODEL = "gemini-3.5-flash-lite"

MAX_RETRIES = 3


# ============================================================
# Load chunks
# ============================================================

with open(INPUT_PATH, "r", encoding="utf-8") as f:
    chunks = json.load(f)


# ============================================================
# Load previous results if they exist
# ============================================================

if os.path.exists(OUTPUT_PATH):

    with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
        results = json.load(f)

else:
    results = []


# ============================================================
# Detect already completed chunks
# ============================================================

completed_chunks = {
    item["chunk_id"]
    for item in results
    if item.get("topics") is not None
}


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

def build_prompt(chunk):

    metadata = chunk.get("metadata", {})

    witness = metadata.get("witness")
    matter = metadata.get("matter")
    deposition_date = metadata.get("deposition_date")
    examining_attorney = metadata.get("examining_attorney")
    parties = metadata.get("parties")

    metadata_block = f"""
DOCUMENT METADATA:

Witness: {witness if witness is not None else "Not available"}
Matter/Case: {matter if matter is not None else "Not available"}
Deposition Date: {deposition_date if deposition_date is not None else "Not available"}
Examining Attorney: {examining_attorney if examining_attorney is not None else "Not available"}
Parties: {json.dumps(parties, ensure_ascii=False) if parties is not None else "Not available"}

The metadata above comes from the supplied deposition source.
Do not invent or infer values for fields marked "Not available".

"""

    prompt = metadata_block + """
You are analyzing a legal deposition transcript.

Your task is to identify meaningful substantive discussion topics
inside the supplied transcript chunk.

IMPORTANT:

The supplied transcript is the ONLY source of information.

Do not use outside knowledge.

Do not invent facts.

Do not invent page numbers.

Do not invent line numbers.

Every location you return MUST exactly match a location supplied
in this transcript chunk.


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

8. Pay attention to whether the beginning of this chunk is
   continuing a topic from earlier testimony.

9. Return topics in chronological order.

10. Keep topic names concise and attorney-friendly.

11. For every topic, identify several exact transcript
    locations that support the topic.

12. Evidence locations MUST come directly from the supplied
    transcript.

13. Evidence locations must fall inside the topic's
    start/end range.

14. If there is no meaningful substantive topic, return an
    empty topics list.

15. Do not claim that something is evidence unless the
    supplied transcript supports it.


GROUNDING REQUIREMENT:

For every topic, return evidence_locations.

Each evidence location must have:

{
    "page": <page number>,
    "line": <line number>
}

These locations must exactly match one of the
[Page X, Line Y] locations supplied below.


RETURN ONLY VALID JSON.

Expected format:

{
  "topics": [
    {
      "topic": "Short attorney-friendly topic name",
      "start_page": 0,
      "start_line": 0,
      "end_page": 0,
      "end_line": 0,
      "evidence": "Short explanation of what the supplied testimony supports.",
      "evidence_locations": [
        {
          "page": 0,
          "line": 0
        }
      ]
    }
  ]
}


TRANSCRIPT CHUNK:

"""

    for line in chunk["lines"]:

        prompt += (
            f"[Page {line['page']}, Line {line['line']}] "
            f"{line['text']}\n"
        )

    return prompt


# ============================================================
# Call Gemini
# ============================================================

def call_gemini(prompt):

    for attempt in range(1, MAX_RETRIES + 1):

        try:

            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    response_mime_type="application/json",
                ),
            )

            result = json.loads(response.text)

            return result, True

        except Exception as e:

            error_text = str(e)

            # ------------------------------------------------
            # Quota error
            # ------------------------------------------------

            if (
                "429" in error_text
                or "RESOURCE_EXHAUSTED" in error_text
            ):

                print("\nGemini quota exhausted.")
                print(
                    "Stopping the pipeline so no additional "
                    "requests are wasted."
                )

                return {"topics": []}, False

            # ------------------------------------------------
            # Other errors
            # ------------------------------------------------

            print(
                f"Attempt {attempt}/{MAX_RETRIES} failed:"
            )

            print(e)

            if attempt < MAX_RETRIES:

                wait_time = 2 ** attempt

                print(
                    f"Waiting {wait_time} seconds before retry..."
                )

                time.sleep(wait_time)

    return {"topics": []}, False


# ============================================================
# Validate LLM output structure
# ============================================================

def validate_llm_result(result, chunk):

    if not isinstance(result, dict):
        return False, "Result is not a JSON object."

    topics = result.get("topics")

    if not isinstance(topics, list):
        return False, "'topics' is not a list."

    # Locations actually supplied to Gemini
    supplied_locations = {
        (line["page"], line["line"])
        for line in chunk["lines"]
    }

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

                return (
                    False,
                    f"Topic {index}: missing field '{field}'."
                )

        # ----------------------------------------------------
        # Check topic start/end locations
        # ----------------------------------------------------

        start_location = (
            topic["start_page"],
            topic["start_line"]
        )

        end_location = (
            topic["end_page"],
            topic["end_line"]
        )

        if start_location not in supplied_locations:

            return (
                False,
                f"Topic {index}: invalid start location "
                f"{start_location}."
            )

        if end_location not in supplied_locations:

            return (
                False,
                f"Topic {index}: invalid end location "
                f"{end_location}."
            )

        # ----------------------------------------------------
        # Check chronological order
        # ----------------------------------------------------

        start_key = (
            topic["start_page"],
            topic["start_line"]
        )

        end_key = (
            topic["end_page"],
            topic["end_line"]
        )

        if start_key > end_key:

            return (
                False,
                f"Topic {index}: start location is after "
                f"end location."
            )

        # ----------------------------------------------------
        # Check evidence locations
        # ----------------------------------------------------

        evidence_locations = topic["evidence_locations"]

        if not isinstance(evidence_locations, list):

            return (
                False,
                f"Topic {index}: evidence_locations "
                f"is not a list."
            )

        if len(evidence_locations) == 0:

            return (
                False,
                f"Topic {index}: no evidence locations."
            )

        for evidence in evidence_locations:

            if not isinstance(evidence, dict):

                return (
                    False,
                    f"Topic {index}: invalid evidence location."
                )

            if "page" not in evidence or "line" not in evidence:

                return (
                    False,
                    f"Topic {index}: evidence location must "
                    f"contain page and line."
                )

            location = (
                evidence["page"],
                evidence["line"]
            )

            # Must exist in supplied chunk
            if location not in supplied_locations:

                return (
                    False,
                    f"Topic {index}: evidence location "
                    f"{location} was not supplied to the LLM."
                )

            # Must be inside topic range
            if location < start_key or location > end_key:

                return (
                    False,
                    f"Topic {index}: evidence location "
                    f"{location} is outside topic range."
                )

    return True, "Valid"


# ============================================================
# Build candidate result record
# ============================================================

def build_candidate_record(chunk, topics):
    return {
        "chunk_id": chunk["chunk_id"],
        "start_page": chunk["start_page"],
        "start_line": chunk["start_line"],
        "end_page": chunk["end_page"],
        "end_line": chunk["end_line"],
        "metadata": chunk.get("metadata", {}),
        "topics": topics,
    }


# ============================================================
# Process chunks
# ============================================================

for chunk in chunks:

    chunk_id = chunk["chunk_id"]

    # --------------------------------------------------------
    # Skip completed chunks
    # --------------------------------------------------------

    if chunk_id in completed_chunks:

        print(
            f"Skipping chunk {chunk_id}/{len(chunks)} "
            f"- already completed."
        )

        continue

    print(
        f"\nProcessing chunk {chunk_id}/{len(chunks)} "
        f"({chunk['start_page']}:{chunk['start_line']} "
        f"to {chunk['end_page']}:{chunk['end_line']})"
    )

    # --------------------------------------------------------
    # Build prompt
    # --------------------------------------------------------

    prompt = build_prompt(chunk)

    # --------------------------------------------------------
    # Call Gemini
    # --------------------------------------------------------

    result, success = call_gemini(prompt)

    if not success:

        print(
            f"Chunk {chunk_id} was not completed."
        )

        break

    # --------------------------------------------------------
    # Deterministic validation of LLM output
    # --------------------------------------------------------

    valid, validation_message = validate_llm_result(
        result,
        chunk
    )

    if not valid:

        print(
            f"\nLLM output validation FAILED for "
            f"chunk {chunk_id}:"
        )

        print(validation_message)

        print(
            "Chunk was NOT saved because the LLM output "
            "did not satisfy grounding requirements."
        )

        break

    print(
        f"LLM output validation PASSED for chunk {chunk_id}."
    )

    # --------------------------------------------------------
    # Save result
    # --------------------------------------------------------

    results.append(
        build_candidate_record(
            chunk,
            result.get("topics", [])
        )
    )

    # --------------------------------------------------------
    # Incremental persistence
    # --------------------------------------------------------

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            results,
            f,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"Topics found: {len(result.get('topics', []))}"
    )

    # Small delay between requests
    time.sleep(1)


# ============================================================
# Final status
# ============================================================

print("\nPipeline stopped or completed.")

print(
    f"Completed chunks saved: {len(results)}"
)

print(
    f"Saved to {OUTPUT_PATH}"
)