import pymupdf
import json
import re

PDF_PATH = "data/raw/Persis_Yu_Deposition.pdf"
OUTPUT_PATH = "data/transcript.json"

doc = pymupdf.open(PDF_PATH)

pages = []

for pdf_index in range(5, 93):
    text = doc[pdf_index].get_text()

    match = re.search(r"Page\s+(\d+)\s*$", text.strip())

    if not match:
        continue

    transcript_page = int(match.group(1))

    pages.append({
        "pdf_page": pdf_index + 1,
        "transcript_page": transcript_page,
        "text": text
    })

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(pages, f, indent=2, ensure_ascii=False)

print(f"Extracted {len(pages)} transcript pages.")
print(f"Saved to {OUTPUT_PATH}")