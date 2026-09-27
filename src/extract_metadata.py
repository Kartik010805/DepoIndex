import json
import re
from pathlib import Path

import pymupdf


PDF_PATH = Path("data/raw/Persis_Yu_Deposition.pdf")
OUTPUT_PATH = Path("data/metadata.json")


def extract_metadata(pdf_path=PDF_PATH):
    doc = pymupdf.open(pdf_path)

    front_matter = "\n".join(
        doc[index].get_text()
        for index in range(min(5, len(doc)))
    )

    witness_match = re.search(
        r"DEPOSITION OF ([A-Z][A-Z .'-]+)",
        front_matter,
        re.IGNORECASE,
    )

    examination_match = re.search(
        r"By\s+(Mr\.\s+[A-Za-z .'-]+?)(?:\s+\d+)?\s*$",
        front_matter,
        re.IGNORECASE | re.MULTILINE,
    )

    witness = witness_match.group(1).strip().title() if witness_match else None

    examining_attorney = (
        re.sub(r"\s+\d+\s*$", "", examination_match.group(1)).strip()
        if examination_match
        else None
    )

    return {
        "witness": witness,
        "matter": None,
        "deposition_date": None,
        "examining_attorney": examining_attorney,
        "parties": None,
        "administrative_information": "redacted",
    }


def main():
    metadata = extract_metadata()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print("Extracted deposition metadata:")
    print(json.dumps(metadata, indent=2, ensure_ascii=False))
    print(f"Saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
