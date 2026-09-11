import json
import os

from google import genai
from google.genai import types

INPUT_PATH = "data/overlap_prompt.txt"
OUTPUT_PATH = "data/overlap_result.json"

with open(INPUT_PATH, "r", encoding="utf-8") as f:
    prompt = f.read()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=prompt,
    config=types.GenerateContentConfig(
        temperature=0.2,
        response_mime_type="application/json",
    ),
)

result = json.loads(response.text)

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print("Overlap test completed.")
print(f"Saved to {OUTPUT_PATH}")
print(f"Topics found: {len(result.get('topics', []))}")
