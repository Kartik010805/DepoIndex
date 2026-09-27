import json


def validate_transcript_lines(
    lines,
    expected_first_page=6,
    expected_last_page=87,
):
    """
    Validate the structural integrity of addressable transcript lines.

    Checks:
    - required fields
    - valid page/line values
    - non-empty transcript text
    - duplicate page/line locations
    - chronological ordering
    - transcript page coverage
    - line-number continuity within each page
    """

    errors = []

    if not isinstance(lines, list):
        return ["Transcript output must be a list."]

    if not lines:
        return ["Transcript output is empty."]

    required_fields = {"page", "line", "text"}

    locations = []

    # ---------------------------------------------------------
    # 1. Validate individual records
    # ---------------------------------------------------------

    for index, item in enumerate(lines, start=1):

        if not isinstance(item, dict):
            errors.append(
                f"record {index} is not an object"
            )
            continue

        missing = required_fields - set(item.keys())

        if missing:
            errors.append(
                f"record {index} missing fields: "
                f"{sorted(missing)}"
            )
            continue

        try:
            page = int(item["page"])
            line = int(item["line"])
        except (TypeError, ValueError):

            errors.append(
                f"record {index} has invalid page/line values"
            )
            continue

        text = item.get("text")

        if not isinstance(text, str):
            errors.append(
                f"record {index} text is not a string"
            )

        elif not text.strip():
            errors.append(
                f"record {index} has empty transcript text "
                f"at {page}:{line}"
            )

        if page <= 0:
            errors.append(
                f"record {index} has invalid page {page}"
            )

        if line <= 0:
            errors.append(
                f"record {index} has invalid line {line}"
            )

        locations.append((page, line))

    # ---------------------------------------------------------
    # 2. Duplicate location detection
    # ---------------------------------------------------------

    seen = set()

    for page, line in locations:

        location = (page, line)

        if location in seen:
            errors.append(
                f"duplicate transcript location {page}:{line}"
            )

        seen.add(location)

    # ---------------------------------------------------------
    # 3. Global chronological ordering
    # ---------------------------------------------------------

    for previous, current in zip(
        locations,
        locations[1:]
    ):

        if current <= previous:

            errors.append(
                "transcript locations are not strictly "
                f"chronological: "
                f"{previous[0]}:{previous[1]} -> "
                f"{current[0]}:{current[1]}"
            )

    # ---------------------------------------------------------
    # 4. Transcript page coverage
    # ---------------------------------------------------------

    pages = sorted(
        {
            page
            for page, _ in locations
        }
    )

    expected_pages = range(
        expected_first_page,
        expected_last_page + 1
    )

    missing_pages = [
        page
        for page in expected_pages
        if page not in pages
    ]

    if missing_pages:

        errors.append(
            "missing transcript pages: "
            + ", ".join(
                str(page)
                for page in missing_pages
            )
        )

    # ---------------------------------------------------------
    # 5. Line continuity within each page
    # ---------------------------------------------------------

    page_lines = {}

    for page, line in locations:

        page_lines.setdefault(
            page,
            []
        ).append(line)

    for page, line_numbers in page_lines.items():

        line_numbers = sorted(line_numbers)

        for previous, current in zip(
            line_numbers,
            line_numbers[1:]
        ):

            if current != previous + 1:

                errors.append(
                    f"line-number gap on transcript page "
                    f"{page}: {previous} -> {current}"
                )

    return errors


def validate_transcript_file(
    input_path,
    expected_first_page=6,
    expected_last_page=87,
):
    """
    Load a transcript JSON file and validate it.
    """

    with open(
        input_path,
        "r",
        encoding="utf-8"
    ) as file:

        lines = json.load(file)

    return validate_transcript_lines(
        lines,
        expected_first_page=expected_first_page,
        expected_last_page=expected_last_page,
    )


if __name__ == "__main__":

    INPUT_PATH = "data/lines.json"

    errors = validate_transcript_file(
        INPUT_PATH
    )

    print("=" * 60)
    print("TRANSCRIPT INTEGRITY VALIDATION")
    print("=" * 60)

    if errors:

        print("STATUS: FAIL")
        print(f"Errors found: {len(errors)}")

        for error in errors:
            print(f"- {error}")

        raise SystemExit(1)

    print("STATUS: PASS")
    print("Transcript structure is valid.")
