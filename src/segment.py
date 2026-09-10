import json
import re

INPUT_PATH = "data/transcript.json"
OUTPUT_PATH = "data/lines.json"

with open(INPUT_PATH, "r", encoding="utf-8") as f:
    pages = json.load(f)

lines = []

for page in pages:
    transcript_page = page["transcript_page"]
    raw_lines = page["text"].splitlines()

    current_line = None
    current_text = []

    for raw in raw_lines:
        text = raw.strip()

        if not text:
            continue

        page_match = re.fullmatch(r"Page\s+\d+", text, re.IGNORECASE)
        if page_match:
            continue

        line_match = re.fullmatch(r"\d{1,2}", text)

        if line_match:
            if current_line is not None and current_text:
                lines.append({
                    "page": transcript_page,
                    "line": current_line,
                    "text": " ".join(current_text)
                })

            current_line = int(text)
            current_text = []
            continue

        if current_line is not None:
            current_text.append(text)

    if current_line is not None and current_text:
        lines.append({
            "page": transcript_page,
            "line": current_line,
            "text": " ".join(current_text)
        })

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(lines, f, indent=2, ensure_ascii=False)

print(f"Extracted {len(lines)} numbered transcript lines.")
print(f"Saved to {OUTPUT_PATH}")