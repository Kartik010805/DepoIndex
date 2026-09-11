import json

INPUT_PATH = "data/chunks.json"
OUTPUT_PATH = "data/overlap_prompt.txt"

with open(INPUT_PATH, "r", encoding="utf-8") as f:
    chunks = json.load(f)

chunk = chunks[1]

prompt = """You are analyzing a legal deposition transcript.

Identify meaningful substantive discussion topics and topic transitions.

Rules:
1. Use ONLY information contained in the transcript.
2. Do not invent facts or page/line numbers.
3. Every start and end location must exactly match a supplied transcript location.
4. Ignore routine deposition procedure and other non-substantive material.
5. Combine consecutive discussion belonging to the same substantive topic.
6. Do not create a new topic for a short digression.
7. Topics may continue across pages.
8. Pay special attention to whether a topic from the beginning of this chunk is a continuation of an earlier discussion.
9. Do not force a topic boundary merely because this chunk starts or ends.
10. Return topics chronologically.
11. Keep topic labels concise.
12. Give a short evidence explanation.

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

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(prompt)

    for line in chunk["lines"]:
        f.write(
            f"[Page {line['page']}, Line {line['line']}] "
            f"{line['text']}\n"
        )

print(f"Prepared chunk {chunk['chunk_id']}.")
print(
    f"Transcript range: "
    f"{chunk['start_page']}:{chunk['start_line']} "
    f"to {chunk['end_page']}:{chunk['end_line']}"
)
print(f"Saved to {OUTPUT_PATH}")
