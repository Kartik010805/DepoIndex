import json
import re
import unicodedata

from nltk.tokenize import RegexpTokenizer

from transcript_integrity import validate_transcript_lines


INPUT_PATH = "data/transcript.json"
OUTPUT_PATH = "data/lines.json"

tokenizer = RegexpTokenizer(r"\S+")


def clean_transcript_text(text):
    """
    Clean extracted transcript text while preserving meaning.
    """

    if not text:
        return ""

    text = unicodedata.normalize(
        "NFKC",
        text
    )

    text = text.strip()

    tokens = tokenizer.tokenize(text)

    return " ".join(tokens)


with open(
    INPUT_PATH,
    "r",
    encoding="utf-8"
) as f:

    pages = json.load(f)


lines = []


for page in pages:

    transcript_page = page["transcript_page"]

    # Keep actual testimony pages.
    if transcript_page < 6 or transcript_page > 87:
        continue

    current_line = None
    current_text = []

    for raw_line in page["text"].splitlines():

        raw_line = clean_transcript_text(
            raw_line
        )

        # Remove timestamp artifacts.
        raw_line = re.sub(
            r"\s+\d{2}:\d{2}$",
            "",
            raw_line
        ).strip()

        if not raw_line:
            continue

        # Remove page-header artifacts.
        if raw_line.startswith("Page "):
            continue

        # Transcript line marker.
        match = re.fullmatch(
            r"\d{1,2}",
            raw_line
        )

        if match:

            # Save previous transcript line.
            if (
                current_line is not None
                and current_text
            ):

                lines.append(
                    {
                        "page": transcript_page,
                        "line": current_line,
                        "text": " ".join(
                            current_text
                        )
                    }
                )

            current_line = int(
                raw_line
            )

            current_text = []

        else:

            # Continuation text.
            if current_line is not None:

                current_text.append(
                    raw_line
                )

    # Save final line on page.
    if (
        current_line is not None
        and current_text
    ):

        lines.append(
            {
                "page": transcript_page,
                "line": current_line,
                "text": " ".join(
                    current_text
                )
            }
        )


# =========================================================
# INTEGRITY CHECK BEFORE WRITING lines.json
# =========================================================

integrity_errors = validate_transcript_lines(
    lines,
    expected_first_page=6,
    expected_last_page=87,
)


if integrity_errors:

    print("=" * 60)
    print("TRANSCRIPT INTEGRITY VALIDATION: FAIL")
    print("=" * 60)

    for error in integrity_errors:
        print(f"- {error}")

    raise RuntimeError(
        "Transcript integrity validation failed. "
        "Existing data/lines.json was not overwritten."
    )


# =========================================================
# Write only validated transcript output
# =========================================================

with open(
    OUTPUT_PATH,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        lines,
        f,
        indent=2,
        ensure_ascii=False
    )


print(
    f"Extracted {len(lines)} numbered transcript lines."
)

print(
    "Transcript integrity validation: PASS"
)

print(
    f"Saved to {OUTPUT_PATH}"
)
