import json


INPUT_FILE = "data/manual_corrected_topics.json"
OUTPUT_FILE = "data/manual_validation_results.json"


with open(INPUT_FILE, "r", encoding="utf-8") as f:
    topics = json.load(f)["topics"]


# These are the 20 topics that were manually reviewed.
# The review checked:
# - location accuracy
# - topic relevance
# - boundary quality
# - redundancy
#
# Topic 8 was corrected after the review because its original
# boundary overlapped with Topic 9.


reviewed_topics = [
    {
        "topic_number": 1,
        "location_accuracy": "PASS",
        "topic_relevance": "PASS",
        "boundary_quality": "PASS",
        "redundancy": "PASS",
        "notes": "Clear beginning of expert-retention discussion and clear transition to exhibit/report discussion."
    },
    {
        "topic_number": 2,
        "location_accuracy": "PASS",
        "topic_relevance": "PASS",
        "boundary_quality": "PASS",
        "redundancy": "PASS",
        "notes": "Attorney background and CV discussion ends before student-loan policy research begins."
    },
    {
        "topic_number": 3,
        "location_accuracy": "PASS",
        "topic_relevance": "PASS",
        "boundary_quality": "PASS",
        "redundancy": "PASS",
        "notes": "Policy research discussion begins at a clear transition."
    },
    {
        "topic_number": 5,
        "location_accuracy": "PASS",
        "topic_relevance": "PASS",
        "boundary_quality": "PASS",
        "redundancy": "PASS",
        "notes": "Servicer initiatives form a meaningful deposition topic."
    },
    {
        "topic_number": 6,
        "location_accuracy": "PASS",
        "topic_relevance": "PASS",
        "boundary_quality": "PASS",
        "redundancy": "PASS",
        "notes": "Clear shift to whether the witness personally worked as a loan servicer."
    },
    {
        "topic_number": 7,
        "location_accuracy": "PASS",
        "topic_relevance": "PASS",
        "boundary_quality": "PASS",
        "redundancy": "PASS",
        "notes": "Portfolio-transfer experience is distinct from the subsequent detailed transfer-process discussion."
    },
    {
        "topic_number": 8,
        "location_accuracy": "PASS",
        "topic_relevance": "PASS",
        "boundary_quality": "PASS",
        "redundancy": "PASS",
        "notes": "Boundary corrected to end at 23:7 before the specific data-transfer regulation discussion."
    },
    {
        "topic_number": 9,
        "location_accuracy": "PASS",
        "topic_relevance": "PASS",
        "boundary_quality": "PASS",
        "redundancy": "PASS",
        "notes": "Specific servicing-data transfer laws begin at 23:8 and continue through the PEAKS transfer question."
    },
    {
        "topic_number": 10,
        "location_accuracy": "PASS",
        "topic_relevance": "PASS",
        "boundary_quality": "PASS",
        "redundancy": "PASS",
        "notes": "Specific PEAKS transfer and alleged regulatory violations form a distinct discussion."
    },
    {
        "topic_number": 11,
        "location_accuracy": "PASS",
        "topic_relevance": "PASS",
        "boundary_quality": "PASS",
        "redundancy": "PASS",
        "notes": "Clear transition to criminal-law work experience."
    },
    {
        "topic_number": 14,
        "location_accuracy": "PASS",
        "topic_relevance": "PASS",
        "boundary_quality": "PASS",
        "redundancy": "PASS",
        "notes": "General for-profit-college discussion ends before ITT-specific questioning."
    },
    {
        "topic_number": 15,
        "location_accuracy": "PASS",
        "topic_relevance": "PASS",
        "boundary_quality": "PASS",
        "redundancy": "PASS",
        "notes": "ITT-specific expertise, debt, and outcomes discussion begins at 27:13."
    },
    {
        "topic_number": 16,
        "location_accuracy": "PASS",
        "topic_relevance": "PASS",
        "boundary_quality": "PASS",
        "redundancy": "PASS",
        "notes": "Degree-value and earnings discussion ends before the explicit definition of outlier."
    },
    {
        "topic_number": 17,
        "location_accuracy": "PASS",
        "topic_relevance": "PASS",
        "boundary_quality": "PASS",
        "redundancy": "PASS",
        "notes": "Discussion of outliers and institutional misrepresentation begins at 34:9."
    },
    {
        "topic_number": 18,
        "location_accuracy": "PASS",
        "topic_relevance": "PASS",
        "boundary_quality": "PASS",
        "redundancy": "PASS",
        "notes": "Vervent-awareness discussion ends before questions about the source of the witness's knowledge."
    },
    {
        "topic_number": 19,
        "location_accuracy": "PASS",
        "topic_relevance": "PASS",
        "boundary_quality": "PASS",
        "redundancy": "PASS",
        "notes": "Source/evidence discussion begins at 36:3."
    },
    {
        "topic_number": 20,
        "location_accuracy": "PASS",
        "topic_relevance": "PASS",
        "boundary_quality": "PASS",
        "redundancy": "PASS",
        "notes": "Two candidate topics were merged because the transcript shows one continuous earnings hypothetical."
    },
    {
        "topic_number": 22,
        "location_accuracy": "PASS",
        "topic_relevance": "PASS",
        "boundary_quality": "PASS",
        "redundancy": "PASS",
        "notes": "PEAKS legality, enforceability, and collection-order discussion is a meaningful topic."
    },
    {
        "topic_number": 28,
        "location_accuracy": "PASS",
        "topic_relevance": "PASS",
        "boundary_quality": "PASS",
        "redundancy": "PASS",
        "notes": "Final-disclosure discussion ends at 58:7 before the specific enforceability hypothetical."
    },
    {
        "topic_number": 29,
        "location_accuracy": "PASS",
        "topic_relevance": "PASS",
        "boundary_quality": "PASS",
        "redundancy": "PASS",
        "notes": "Enforceability and cancellation hypothetical begins at 58:8."
    }
]


result = {
    "validation_method": {
        "sample_size": len(reviewed_topics),
        "criteria": [
            "location_accuracy",
            "topic_relevance",
            "boundary_quality",
            "redundancy"
        ],
        "selection": (
            "Representative entries were selected across the deposition, "
            "including manually corrected boundaries and topic transitions."
        )
    },
    "reviewed_topics": reviewed_topics
}


with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(
        result,
        f,
        indent=2,
        ensure_ascii=False
    )


print("Manual validation results created.")
print(f"Entries reviewed: {len(reviewed_topics)}")
print(f"Saved to {OUTPUT_FILE}")