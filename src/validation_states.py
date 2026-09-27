from enum import Enum


class ValidationStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    NEEDS_HUMAN_REVIEW = "NEEDS_HUMAN_REVIEW"


VALIDATION_LEVELS = (
    "structural",
    "referential",
    "grounding",
    "semantic",
)


def determine_overall_status(levels):
    """
    Determine the overall review state from individual
    validation levels.

    Priority:

        FAIL
          ↓
        NEEDS_HUMAN_REVIEW
          ↓
        PASS

    A hard failure always takes precedence over review.
    """

    statuses = [
        levels.get(
            level,
            ValidationStatus.FAIL.value
        )
        for level in VALIDATION_LEVELS
    ]

    if ValidationStatus.FAIL.value in statuses:
        return ValidationStatus.FAIL.value

    if (
        ValidationStatus.NEEDS_HUMAN_REVIEW.value
        in statuses
    ):
        return ValidationStatus.NEEDS_HUMAN_REVIEW.value

    return ValidationStatus.PASS.value


def build_validation_state(
    structural,
    referential,
    grounding,
    semantic,
    review_reasons=None,
):
    """
    Build a normalized validation-state object.

    Each validation level must resolve to one of:

        PASS
        FAIL
        NEEDS_HUMAN_REVIEW
    """

    levels = {
        "structural": structural,
        "referential": referential,
        "grounding": grounding,
        "semantic": semantic,
    }

    invalid_statuses = {
        ValidationStatus.PASS.value,
        ValidationStatus.FAIL.value,
        ValidationStatus.NEEDS_HUMAN_REVIEW.value,
    }

    for level, status in levels.items():

        if status not in invalid_statuses:

            raise ValueError(
                f"Invalid validation status for "
                f"{level}: {status}"
            )

    if review_reasons is None:
        review_reasons = []

    overall_status = determine_overall_status(
        levels
    )

    return {
        "structural": structural,
        "referential": referential,
        "grounding": grounding,
        "semantic": semantic,
        "overall_status": overall_status,
        "review_reasons": list(review_reasons),
    }


def is_terminal_failure(validation_state):
    """
    Return True when the topic contains a hard failure.
    """

    return (
        validation_state.get("overall_status")
        == ValidationStatus.FAIL.value
    )


def needs_human_review(validation_state):
    """
    Return True when the topic requires human review.
    """

    return (
        validation_state.get("overall_status")
        == ValidationStatus.NEEDS_HUMAN_REVIEW.value
    )


def is_validated(validation_state):
    """
    Return True only when every validation level passes.
    """

    return (
        validation_state.get("overall_status")
        == ValidationStatus.PASS.value
    )
