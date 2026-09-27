import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

sys.path.insert(0, str(SRC))

from transcript_integrity import validate_transcript_lines


def make_line(page, line, text="sample testimony"):
    return {
        "page": page,
        "line": line,
        "text": text,
    }


def test_valid_transcript():
    lines = [
        make_line(6, 22),
        make_line(6, 23),
        make_line(6, 24),
        make_line(7, 1),
        make_line(7, 2),
    ]

    errors = validate_transcript_lines(
        lines,
        expected_first_page=6,
        expected_last_page=7,
    )

    assert errors == []


def test_duplicate_location():
    lines = [
        make_line(6, 22),
        make_line(6, 22),
        make_line(6, 23),
    ]

    errors = validate_transcript_lines(
        lines,
        expected_first_page=6,
        expected_last_page=6,
    )

    assert any(
        "duplicate transcript location" in error
        for error in errors
    )


def test_out_of_order_location():
    lines = [
        make_line(6, 22),
        make_line(6, 24),
        make_line(6, 23),
    ]

    errors = validate_transcript_lines(
        lines,
        expected_first_page=6,
        expected_last_page=6,
    )

    assert any(
        "not strictly chronological" in error
        for error in errors
    )


def test_missing_page():
    lines = [
        make_line(6, 22),
        make_line(6, 23),
        make_line(8, 1),
        make_line(8, 2),
    ]

    errors = validate_transcript_lines(
        lines,
        expected_first_page=6,
        expected_last_page=8,
    )

    assert any(
        "missing transcript pages" in error
        for error in errors
    )


def test_line_gap_inside_page():
    lines = [
        make_line(6, 22),
        make_line(6, 24),
    ]

    errors = validate_transcript_lines(
        lines,
        expected_first_page=6,
        expected_last_page=6,
    )

    assert any(
        "line-number gap" in error
        for error in errors
    )


def test_empty_text():
    lines = [
        make_line(6, 22, ""),
    ]

    errors = validate_transcript_lines(
        lines,
        expected_first_page=6,
        expected_last_page=6,
    )

    assert any(
        "empty transcript text" in error
        for error in errors
    )


def test_missing_required_field():
    lines = [
        {
            "page": 6,
            "line": 22,
        }
    ]

    errors = validate_transcript_lines(
        lines,
        expected_first_page=6,
        expected_last_page=6,
    )

    assert any(
        "missing fields" in error
        for error in errors
    )
