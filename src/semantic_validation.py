import re
import string


STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "but",
    "if",
    "then",
    "than",
    "that",
    "this",
    "these",
    "those",
    "with",
    "from",
    "into",
    "about",
    "for",
    "of",
    "to",
    "in",
    "on",
    "at",
    "by",
    "as",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "it",
    "its",
    "they",
    "them",
    "their",
    "he",
    "she",
    "his",
    "her",
    "you",
    "your",
    "we",
    "our",
    "i",
    "me",
    "my",
    "do",
    "does",
    "did",
    "have",
    "has",
    "had",
    "will",
    "would",
    "could",
    "should",
    "can",
    "may",
    "might",
    "not",
    "no",
    "yes",
    "also",
    "very",
    "just",
    "what",
    "when",
    "where",
    "who",
    "why",
    "how",
}


def normalize_text(text):
    """
    Normalize text for deterministic evidence analysis.
    """

    if not isinstance(text, str):
        return ""

    text = text.lower()

    text = text.translate(
        str.maketrans(
            "",
            "",
            string.punctuation
        )
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text


def tokenize(text):
    """
    Return meaningful normalized tokens.
    """

    normalized = normalize_text(text)

    tokens = re.findall(
        r"\b[a-z0-9]+\b",
        normalized
    )

    return {
        token
        for token in tokens
        if token not in STOPWORDS
        and len(token) > 2
    }


def lexical_support(
    topic_text,
    evidence_text
):
    """
    Calculate deterministic lexical support.

    This is only a supporting signal. It is NOT treated
    as proof of semantic entailment.
    """

    topic_tokens = tokenize(
        topic_text
    )

    evidence_tokens = tokenize(
        evidence_text
    )

    if not topic_tokens:
        return 0.0

    overlap = (
        topic_tokens
        & evidence_tokens
    )

    return (
        len(overlap)
        / len(topic_tokens)
    )


def evidence_coverage(
    topic_text,
    evidence_texts,
):
    """
    Calculate the proportion of evidence snippets
    that provide meaningful lexical support.
    """

    if not evidence_texts:

        return {
            "score": 0.0,
            "supported_items": 0,
            "total_items": 0,
        }

    supported = 0

    for evidence_text in evidence_texts:

        score = lexical_support(
            topic_text,
            evidence_text
        )

        if score >= 0.20:
            supported += 1

    total = len(evidence_texts)

    return {
        "score": supported / total,
        "supported_items": supported,
        "total_items": total,
    }


def classify_semantic_support(
    topic_text,
    evidence_texts,
    minimum_topic_support=0.20,
    minimum_coverage=0.50,
):
    """
    Classify evidence support.

    PASS:
        Evidence has sufficient deterministic lexical
        support.

    NEEDS_HUMAN_REVIEW:
        Evidence exists but deterministic lexical
        analysis is insufficient to establish semantic
        support automatically.

    FAIL:
        No evidence was supplied.

    Important:
        Weak lexical overlap does NOT mean the evidence
        is semantically wrong. It means automated
        validation cannot establish support confidently.
    """

    if not evidence_texts:

        return {
            "status": "FAIL",
            "reason": (
                "No evidence text supplied. "
                "Semantic support cannot be evaluated."
            ),
            "topic_support": 0.0,
            "coverage": 0.0,
        }

    topic_support_scores = [
        lexical_support(
            topic_text,
            evidence_text
        )
        for evidence_text in evidence_texts
    ]

    topic_support = max(
        topic_support_scores
    )

    coverage_result = evidence_coverage(
        topic_text,
        evidence_texts
    )

    coverage = coverage_result["score"]

    # Strong deterministic support.
    if (
        topic_support >= minimum_topic_support
        and coverage >= minimum_coverage
    ):

        return {
            "status": "PASS",
            "reason": (
                "Evidence provides sufficient "
                "deterministic lexical support for "
                "the topic."
            ),
            "topic_support": topic_support,
            "coverage": coverage,
        }

    # Evidence exists, but lexical analysis alone
    # cannot establish semantic correctness.
    return {
        "status": "NEEDS_HUMAN_REVIEW",
        "reason": (
            "Evidence locations exist, but deterministic "
            "lexical support is insufficient to establish "
            "semantic grounding automatically. "
            "Human review is required."
        ),
        "topic_support": topic_support,
        "coverage": coverage,
    }
