import json
import re
import unicodedata

from nltk.tokenize import RegexpTokenizer


INPUT_PATH = "data/transcript.json"
OUTPUT_PATH = "data/lines.json"


# NLTK tokenizer used for safe whitespace/token normalization.
# It does not require downloading any NLTK data package.
tokenizer = RegexpTokenizer(r"\S+")


def clean_transcript_text(text):
    """
    Clean extracted transcript text while preserving its meaning.

    Cleaning includes:
    - Unicode normalization
    - removal of leading/trailing whitespace
    - normalization of repeated whitespace using NLTK
    - preservation of punctuation and transcript wording
    """

    if not text:
        return ""

    # Normalize Unicode characters produced by PDF extraction.
    text = unicodedata.normalize("NFKC", text)

    # Remove leading/trailing whitespace.
    text = text.strip()

    # Normalize whitespace using NLTK tokenization.
    tokens = tokenizer.tokenize(text)
    text = " ".join(tokens)

    return text


with open(INPUT_PATH, "r", encoding="utf-8") as f:
    pages = json.load(f)


lines = []

for page in pages:
    transcript_page = page["transcript_page"]

    # Keep only the actual testimony range.
    if transcript_page < 6 or transcript_page > 87:
        continue

    current_line = None
    current_text = []

    for raw_line in page["text"].splitlines():

        # Clean the extracted PDF line.
        raw_line = clean_transcript_text(raw_line)

        # Remove extraction timestamps at the end of a line.
        raw_line = re.sub(r"\s+\d{2}:\d{2}$", "", raw_line).strip()

        if not raw_line:
            continue

        # Ignore PDF page-header artifacts.
        if raw_line.startswith("Page "):
            continue

        # A standalone number represents a transcript line number.
        match = re.fullmatch(r"\d{1,2}", raw_line)

        if match:
            # Save the previous transcript line.
            if current_line is not None and current_text:
                lines.append({
                    "page": transcript_page,
                    "line": current_line,
                    "text": " ".join(current_text)
                })

            current_line = int(raw_line)
            current_text = []

        else:
            # Continuation text belongs to the current transcript line.
            if current_line is not None:
                current_text.append(raw_line)

    # Save the final transcript line on the page.
    if current_line is not None and current_text:
        lines.append({
            "page": transcript_page,
            "line": current_line,
            "text": " ".join(current_text)
        })


with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(
        lines,
        f,
        indent=2,
        ensure_ascii=False
    )


print(f"Extracted {len(lines)} numbered transcript lines.")
print(f"Saved to {OUTPUT_PATH}")