import json
import os
import time

from google import genai
from google.genai import types

INPUT_PATH = "data/chunks.json"
OUTPUT_PATH = "data/candidate_topics.json"

MODEL = "gemini-3.5-flash-lite"
MAX_RETRIES = 3

with open(INPUT_PATH, "r", encoding="utf-8") as f:
    chunks = json.load(f)

if os.path.exists(OUTPUT_PATH):
    with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
        results = json.load(f)
else:
    results = []

completed_chunks = {
    item["chunk_id"]
    for item in results
    if item.get("topics") 
}

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def build_prompt(chunk):
    prompt = """You are analyzing a legal deposition transcript.

Identify meaningful substantive discussion topics and topic transitions.

Rules:
1. Use ONLY information contained in the supplied transcript.
2. Do not invent facts or page/line numbers.
3. Every start and end location must exactly match a supplied transcript location.
4. Ignore routine deposition procedure, introductions, objections, and other non-substantive material.
5. Do not create a separate topic for every question.
6. Combine consecutive discussion belonging to the same substantive topic.
7. A short digression should not create a new topic.
8. Topics may continue across pages.
9. Do not force a topic boundary merely because this chunk starts or ends.
10. Pay attention to whether a topic at the beginning is a continuation from an earlier discussion.
11. Return topics chronologically.
12. Keep topic labels concise.
13. Give a short evidence explanation.
14. If no meaningful substantive topic is present, return an empty topics list.

Return ONLY valid JSON:

{
  "topics": [
    {
      "topic": "Short topic name",
      "start_page": 0,
      "start_line": 0,
      "end_page": 0,
      "end_line": 0,
      "evidence": "Brief supporting explanation."
    }
  ]
}

Transcript:

"""

    for line in chunk["lines"]:
        prompt += (
            f"[Page {line['page']}, Line {line['line']}] "
            f"{line['text']}\n"
        )

    return prompt


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

            return json.loads(response.text), True

        except Exception as e:
            error_text = str(e)

            if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
                print("Gemini quota exhausted.")
                print("Stopping the pipeline so we do not waste requests.")
                return {"topics": []}, False

            print(f"Attempt {attempt}/{MAX_RETRIES} failed: {e}")

            if attempt < MAX_RETRIES:
                wait_time = 2 ** attempt
                print(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)

    return {"topics": []}, False


for chunk in chunks:
    chunk_id = chunk["chunk_id"]

    if chunk_id in completed_chunks:
        print(f"Skipping chunk {chunk_id}/{len(chunks)} - already completed.")
        continue

    print(
        f"\nProcessing chunk {chunk_id}/{len(chunks)} "
        f"({chunk['start_page']}:{chunk['start_line']} "
        f"to {chunk['end_page']}:{chunk['end_line']})"
    )

    prompt = build_prompt(chunk)
    result, success = call_gemini(prompt)

    if not success:
        print(f"Chunk {chunk_id} was not completed.")
        break

    results.append({
        "chunk_id": chunk_id,
        "start_page": chunk["start_page"],
        "start_line": chunk["start_line"],
        "end_page": chunk["end_page"],
        "end_line": chunk["end_line"],
        "topics": result.get("topics", [])
    })

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Topics found: {len(result.get('topics', []))}")

    time.sleep(1)


print("\nPipeline stopped or completed.")
print(f"Completed chunks saved: {len(results)}")
print(f"Saved to {OUTPUT_PATH}")