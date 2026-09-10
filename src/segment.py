import json
import re

INPUT_PATH = "data/transcript.json"
OUTPUT_PATH = "data/lines.json"

with open(INPUT_PATH, "r", encoding="utf-8") as f:
    pages = json.load(f)

lines = []

for page in pages:
    transcript_page = page["transcript_page"]

    if transcript_page < 6 or transcript_page > 87:
        continue

    current_line = None
    current_text = []

    for raw_line in page["text"].splitlines():
        raw_line = raw_line.strip()
        raw_line = re.sub(r"\s+\d{2}:\d{2}$", "", raw_line)

        if not raw_line:
            continue

        if raw_line.startswith("Page "):
            continue

        match = re.fullmatch(r"\d{1,2}", raw_line)

        if match:
            if current_line is not None and current_text:
                lines.append({
                    "page": transcript_page,
                    "line": current_line,
                    "text": " ".join(current_text)
                })

            current_line = int(raw_line)
            current_text = []
        else:
            if current_line is not None:
                current_text.append(raw_line)

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