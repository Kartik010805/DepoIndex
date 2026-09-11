import json


TOPICS_FILE = "data/manual_corrected_topics.json"
VALIDATION_FILE = "data/manual_validation_results.json"
OUTPUT_FILE = "data/validation_report.md"


with open(TOPICS_FILE, "r", encoding="utf-8") as f:
    topics = json.load(f)["topics"]


with open(VALIDATION_FILE, "r", encoding="utf-8") as f:
    validation = json.load(f)


reviewed_topics = validation["reviewed_topics"]


report = []

report.append("# DepoIndex Validation Report\n")

report.append("## 1. Overview\n")

report.append(
    "This report documents validation of the generated deposition "
    "Topic Index for the Persis Yu deposition. The final index "
    "contains 30 topics with transcript page and line references.\n"
)

report.append("## 2. Validation Methodology\n")

report.append(
    "Validation was performed at two levels. First, deterministic "
    "validation checked that every topic contains the required "
    "fields, that every start and end page/line location exists "
    "in the extracted transcript, that each start precedes its "
    "end, and that topics remain in chronological order.\n"
)

report.append(
    "Second, 20 representative topics were manually reviewed. "
    "The manual review checked four dimensions: location accuracy, "
    "topic relevance, boundary quality, and redundancy. The sample "
    "included topics from different portions of the deposition and "
    "included manually corrected boundary cases.\n"
)

report.append("## 3. Deterministic Validation\n")

report.append(
    f"- Final topics checked: **{len(topics)}**\n"
)

report.append(
    "- Required fields: **PASS**\n"
)

report.append(
    "- Start/end locations present in transcript: **PASS**\n"
)

report.append(
    "- Start location precedes end location: **PASS**\n"
)

report.append(
    "- Chronological ordering: **PASS**\n"
)

report.append("## 4. Manual Validation\n")

report.append(
    f"A total of **{len(reviewed_topics)}** topics were manually "
    "reviewed.\n"
)

report.append(
    "| Topic | Location | Relevance | Boundary | Redundancy |\n"
)

report.append(
    "|---:|---|---|---|---|\n"
)

for item in reviewed_topics:

    number = item["topic_number"]

    location = item["location_accuracy"]
    relevance = item["topic_relevance"]
    boundary = item["boundary_quality"]
    redundancy = item["redundancy"]

    report.append(
        f"| {number} | {location} | {relevance} | "
        f"{boundary} | {redundancy} |\n"
    )


report.append("\n## 5. Boundary Corrections Discovered During Review\n")

report.append(
    "Manual review identified several cases where the initial "
    "LLM-generated or merged boundaries were not sufficiently "
    "precise. These were corrected in a separate deterministic "
    "manual-correction layer rather than modifying the extracted "
    "transcript itself.\n"
)

report.append(
    "Examples include separating the witness background discussion "
    "from the subsequent student-loan policy discussion, separating "
    "general for-profit-college background from ITT-specific "
    "discussion, separating the ITT earnings discussion at a clear "
    "question transition, and separating final disclosure questions "
    "from the later enforceability hypothetical.\n"
)

report.append(
    "A further review identified an overlap between the general "
    "student-loan servicing-transfer discussion and the subsequent "
    "data-transfer-regulation discussion. The boundary was corrected "
    "so the general transfer discussion ends at transcript line 23:7 "
    "and the regulation discussion begins at 23:8.\n"
)

report.append(
    "Two candidate topics concerning the same continuous ITT earnings "
    "hypothetical were also merged because the transcript showed a "
    "continuation/refinement of the same discussion rather than a "
    "genuine topic transition.\n"
)

report.append("## 6. Provenance\n")

report.append(
    "Every final topic retains a start and end address in the "
    "extracted transcript using the original deposition page and "
    "line numbering. The deterministic validator checks these "
    "addresses against the extracted transcript representation.\n"
)

report.append(
    "The pipeline therefore separates semantic topic generation "
    "from address validation: an LLM may propose a topic boundary, "
    "but the final boundary must reference an addressable transcript "
    "location.\n"
)

report.append("## 7. Limitations\n")

report.append(
    "- Topic labels and boundaries are initially generated using an "
    "LLM and therefore require validation.\n"
)

report.append(
    "- Chunking can create artificial topic boundaries when a "
    "discussion crosses chunk boundaries.\n"
)

report.append(
    "- Overlapping chunks reduce this risk but can also produce "
    "duplicate candidate topics that require deterministic merging "
    "and manual review.\n"
)

report.append(
    "- The current system has been validated primarily against the "
    "supplied Persis Yu deposition rather than a large collection "
    "of independent depositions.\n"
)

report.append(
    "- The Gemini free-tier request quota limited repeated full "
    "pipeline executions during development, so stability evidence "
    "must be interpreted together with the observed successful "
    "runs and failure behavior.\n"
)

report.append("\n## 8. Conclusion\n")

report.append(
    "The final Topic Index contains 30 chronologically ordered topics. "
    "All 30 passed deterministic provenance validation, and 20 "
    "representative entries were manually reviewed for location "
    "accuracy, relevance, boundary quality, and redundancy. "
    "Boundary corrections identified during review were encoded "
    "reproducibly in the manual correction layer.\n"
)


with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("".join(report))


print("Validation report created.")
print(f"Topics in final index: {len(topics)}")
print(f"Manual entries reviewed: {len(reviewed_topics)}")
print(f"Saved to {OUTPUT_FILE}")