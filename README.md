# DepoIndex

## AI-Powered Deposition Topic Index

DepoIndex is an AI-assisted legal transcript analysis prototype that converts a deposition transcript into a chronological, attorney-friendly topic index.

The system combines:

- Transcript extraction and deterministic cleaning
- Addressable page/line provenance
- Overlapping transcript chunks
- LLM-assisted topic extraction using Google Gemini
- Evidence and evidence-location tracking
- Deterministic source-grounding validation
- Deterministic topic reconciliation
- Manual boundary review
- Final 43-topic index
- Streamlit-based attorney-facing navigation

The goal is to allow an attorney or reviewer to quickly determine **what topics were discussed, where they occur in the deposition, and where the underlying testimony can be verified**.

---

# 1. Problem

Long deposition transcripts are difficult to navigate manually.

A useful deposition index should allow an attorney or reviewer to quickly determine:

1. What subjects were discussed?
2. Where does each subject begin?
3. Where does each subject end?
4. What testimony supports the indexed topic?
5. Which exact transcript page/line locations support that topic?

DepoIndex addresses this by combining LLM-assisted topic segmentation with deterministic provenance validation and human review.

---

# 2. System Architecture

```text
                    Deposition PDF
                         |
                         v
                Transcript Extraction
                         |
                         v
                 Data Cleaning
          NFKC + transcript artifact removal
                         |
                         v
              Addressable Transcript
                Page + Line + Text
                         |
                         v
               Overlapping Chunking
               100 lines / 20 overlap
                         |
                         v
              Gemini Topic Extraction
                         |
                         v
                Candidate Topics
                   57 candidates
                         |
                         v
          Evidence / Provenance Attachment
                         |
                         v
          Deterministic Grounding Validation
                         |
                         v
          Deterministic Topic Reconciliation
                         |
                         v
                44 merged topics
                         |
                         v
             Manual Boundary Review
                         |
                         v
                  43 final topics
                         |
                         v
             Final Grounding Validation
                    43 / 43 PASS
                         |
                         v
              Attorney-Facing Streamlit UI
3. Data Cleaning

Transcript preprocessing is implemented in:

src/segment.py

The cleaning stage:

Normalizes Unicode using NFKC normalization.
Removes blank or unusable transcript lines.
Removes transcript-specific page artifacts.
Removes trailing timestamp artifacts.
Normalizes transcript whitespace.
Uses NLTK RegexpTokenizer for deterministic tokenization.
Preserves the original page and line identifiers.

The output remains addressable:

{
  "page": 8,
  "line": 24,
  "text": "..."
}

The final cleaned transcript contains:

2,018 addressable transcript lines

The important design decision is that cleaning does not discard provenance. Page and line information remains attached to every transcript record.

4. Overlapping Transcript Chunks

The cleaned transcript is divided into overlapping chunks.

Configuration:

Chunk size: 100 transcript lines
Overlap:    20 transcript lines
Step:       80 transcript lines

The overlap provides surrounding context when a discussion continues across an artificial chunk boundary.

This reduces the risk of incorrectly treating a chunk boundary as a topic boundary.

5. LLM-Assisted Topic Extraction

Google Gemini is used to propose meaningful discussion topics.

The implementation is in:

src/run_pipeline.py

The model is instructed to:

Use only the supplied transcript content.
Avoid invented facts.
Preserve exact page/line references.
Identify meaningful discussion subjects.
Avoid creating one topic for every question.
Combine consecutive discussion of the same subject.
Ignore routine procedural exchanges where appropriate.
Return structured JSON.
Provide supporting evidence and evidence locations.

The LLM is treated as a proposal generator rather than ground truth.

The pipeline does not simply trust the generated topic boundaries.

6. Evidence and Provenance

Each final topic contains:

Topic label
Start page
Start line
End page
End line
Supporting evidence
Evidence locations
Source chunk identifiers
Grounding source metadata

Example:

{
  "topic": "Scope of Expert Retention and Testimony",
  "start_page": 8,
  "start_line": 24,
  "end_page": 10,
  "end_line": 4,
  "evidence_locations": [
    {
      "page": 8,
      "line": 24
    },
    {
      "page": 9,
      "line": 2
    }
  ],
  "source_chunks": [1]
}

This provides a provenance chain:

Topic
  |
  +-- Topic boundaries
  |
  +-- Evidence
  |
  +-- Evidence page/line locations
  |
  +-- Source chunks
  |
  +-- Original transcript
7. Source / Semantic Grounding

DepoIndex uses source-grounded LLM extraction.

The LLM receives transcript content as its source material and is instructed not to introduce information that is absent from the supplied testimony.

Grounding is then checked deterministically.

The validator verifies that:

Evidence locations exist in the original transcript.
Evidence locations fall within the final topic boundaries.
Evidence locations remain chronologically ordered.
Evidence locations belong to the topic's source chunks.
Topic start/end locations exist.
Topic boundaries are chronologically valid.
Required provenance fields are present.

This means the LLM's output is not accepted blindly.

The project does not claim embedding-based semantic search or vector-based grounding. Grounding is implemented through source-constrained generation combined with exact transcript page/line provenance and deterministic validation.

8. Candidate Topic Processing

The initial LLM extraction produced:

57 candidate topics

Candidate topics are reconciled using deterministic processing to reduce redundant or overlapping entries.

The result was:

57 candidates
        |
        v
44 merged topics

The implementation is primarily based on deterministic topic range overlap and topic-label similarity.

9. Manual Boundary Review

Some technically valid page/line locations are not necessarily good semantic boundaries.

Manual review was therefore used to correct topic boundaries and reconcile unsuitable topic segmentation.

The manually reviewed final index contains:

43 topics

The corrections are preserved as reproducible project artifacts rather than being silently changed in the final output.

10. Final Validation

The final topic dataset is validated using:

src/validate_final_topics.py

The final validator checks:

Required topic fields
Valid transcript start locations
Valid transcript end locations
Chronological topic boundaries
Evidence-location existence
Evidence-location boundaries
Evidence-location chronological order
Source chunk existence
Evidence membership in source chunks
Grounding source metadata

Final result:

============================================================
FINAL VALIDATION: PASS
============================================================
Total topics: 43
Passed: 43
Failed: 0

Therefore the final grounded topic index passes:

43 / 43 deterministic validation checks

Validation output:

data/final_validation_repaired.json
11. Attorney-Facing Streamlit Application

The project includes a Streamlit interface:

app.py

The interface provides an attorney-facing topic index with:

Topic search
Search across topic names and supporting evidence
Chronological topic navigation
Individual topic selection
Exact transcript start/end locations
Supporting evidence
Evidence page/line locations
Source chunk information
Grounding status
Full provenance details

The workflow is:

Search
  |
  v
Select Topic
  |
  v
Review Topic
  |
  +-- Transcript Range
  |
  +-- Supporting Evidence
  |
  +-- Evidence Locations
  |
  +-- Source Chunks
  |
  +-- Grounding Status

This is designed around the practical requirement that an attorney should be able to quickly locate where a particular subject appears in a long deposition.

12. Example Topic
Topic

Scope of Expert Retention and Testimony

Transcript Range
Page 8, Line 24
        →
Page 10, Line 4
Supporting Evidence

The witness discusses being retained as an expert witness and the scope of her expected testimony.

The application also exposes the supporting page/line evidence and source chunk information.

13. Failure Analysis
Failure 1 — Chunk Boundary Errors

A topic can appear to end at a chunk boundary even when the discussion continues.

Mitigation

Overlapping chunks were introduced:

100-line chunk
20-line overlap
80-line step

This provides surrounding context to the LLM.

Failure 2 — Similar Topics

Related discussions can receive different labels or partially overlapping boundaries.

Mitigation

Deterministic topic reconciliation followed by manual review was used to reduce unnecessary duplication.

Failure 3 — Valid Location but Poor Boundary

A page/line location can technically exist in the transcript while still being a poor semantic topic boundary.

Mitigation

Manual inspection and reproducible boundary corrections were used for the final index.

Failure 4 — Evidence Outside Final Boundaries

During final integration, some evidence locations inherited from earlier candidate topics fell outside manually corrected final topic ranges.

Mitigation

Evidence locations were deterministically re-selected from the original transcript within the final topic boundaries.

The final validator then verified:

43 / 43 PASS
14. Stability Testing

The assignment requires three complete independent pipeline runs.

The complete three-run LLM experiment could not be completed because the available Gemini free-tier request quota was exhausted during processing.

Therefore:

This project does not claim three complete independent LLM runs.

This limitation is documented rather than hidden.

The pipeline does, however, persist intermediate results so completed chunks do not need to be regenerated after transient API failures or quota interruptions.

15. Reliability Measures

DepoIndex uses multiple reliability mechanisms:

Exact page/line provenance
Transcript cleaning before extraction
Overlapping transcript chunks
Structured JSON LLM output
Source-constrained prompting
Evidence-location tracking
Deterministic evidence validation
Deterministic topic-boundary validation
Deterministic candidate merging
Manual boundary review
Intermediate result persistence
Final 43/43 validation
Attorney-facing topic navigation

The central design principle is:

The LLM proposes; deterministic validation verifies.

16. Final Outputs

The final grounded topic index contains:

43 topics

Each topic includes topic information, transcript boundaries, evidence, evidence locations, and provenance information.

Primary final artifact:

data/final_grounded_topics_repaired.json

Additional validation artifacts are stored under:

data/

including:

final_validation_repaired.json
grounded_candidate_topics_repaired.json
grounded_merged_topics.json
grounding_validation_repaired.json
merged_validation.json
17. Project Structure
DepoIndex/
|
|-- app.py
|
|-- src/
|   |-- extract_text.py
|   |-- segment.py
|   |-- chunk.py
|   |-- segment_topics.py
|   |-- run_pipeline.py
|   |-- merge_topics.py
|   |-- manual_corrections.py
|   |-- validate_merged.py
|   |-- manual_validation.py
|   |-- create_validation_results.py
|   |-- create_validation_report.py
|   |-- create_topic_index.py
|   |-- attach_evidence_locations.py
|   |-- integrate_final_topics.py
|   |-- repair_final_evidence.py
|   |-- repair_topic_boundaries.py
|   |-- test_llm_grounding.py
|   |-- validate_evidence.py
|   |-- validate_grounded_candidates.py
|   `-- validate_final_topics.py
|
|-- data/
|   |-- lines.json
|   |-- chunks.json
|   |-- candidate_topics.json
|   |-- grounded_candidate_topics.json
|   |-- grounded_candidate_topics_repaired.json
|   |-- grounded_merged_topics.json
|   |-- final_grounded_topics.json
|   |-- final_grounded_topics_repaired.json
|   |-- final_validation_repaired.json
|   |-- grounding_validation_repaired.json
|   `-- merged_validation.json
|
|-- llm_usage.md
|-- README.md
|-- requirements.txt
`-- .gitignore

The original deposition PDF is intentionally excluded from Git through .gitignore.

18. Installation
git clone <REPOSITORY_URL>
cd DepoIndex
python -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements.txt

On Windows Git Bash:

source .venv/Scripts/activate
19. API Configuration

DepoIndex uses the Gemini API for LLM-based topic extraction.

The API key must be supplied through an environment variable.

The key must never be committed to the repository.

export GEMINI_API_KEY="YOUR_API_KEY"
20. Running the Pipeline

Core pipeline:

python src/extract_text.py
python src/segment.py
python src/chunk.py
python src/run_pipeline.py
python src/merge_topics.py
python src/manual_corrections.py
python src/validate_merged.py

Grounding and final validation:

python src/attach_evidence_locations.py
python src/validate_grounded_candidates.py
python src/repair_topic_boundaries.py
python src/validate_grounded_candidates.py
python src/validate_merged.py
python src/integrate_final_topics.py
python src/repair_final_evidence.py
python src/validate_final_topics.py
21. Running the Application

Start the Streamlit application:

streamlit run app.py

Then open:

http://localhost:8501

The application provides the attorney-facing deposition topic index.

22. Reproducibility

The pipeline separates:

LLM-assisted generation

from:

deterministic processing and validation

Intermediate results are persisted to disk.

This means successful completed chunks do not need to be regenerated after transient API failures or quota interruptions.

The final artifacts also preserve the relationship between:

Topic
→ Evidence
→ Page/Line
→ Source Chunk
→ Original Transcript
23. LLM Usage

AI assistance was used during development.

Gemini was used for transcript topic extraction.

The LLM implementation, prompting approach, accepted and modified suggestions, validation strategy, API failures, free-tier limitations, and human oversight are documented separately in:

llm_usage.md

The key architectural principle is that LLM output is not treated as ground truth.

24. Limitations
LLM-generated topic segmentation can vary between runs.
Three complete independent LLM runs could not be completed because of available free-tier quota.
Manual validation covers 20 entries rather than every topic.
Candidate merging relies partly on deterministic label similarity.
The prototype was evaluated on a single deposition.
Evidence grounding is based on source-constrained generation plus deterministic page/line validation rather than embedding-based semantic retrieval.
The current prototype focuses on deposition indexing rather than complete legal-document retrieval.
25. Future Improvements

Potential future improvements include:

Semantic embedding-based topic merging
Automated boundary-quality scoring
Full three-run stability testing
Search across multiple depositions
Related-topic retrieval
Direct transcript-context navigation
Cross-deposition topic comparison
Confidence scoring for topic boundaries
Vector-based semantic search
More extensive human validation
26. Submission Deliverables

The project includes:

GitHub repository
Working Streamlit application
Final 43-topic index
Structured JSON output
Deterministic validation artifacts
LLM usage documentation
Project presentation
Attorney-facing topic navigation interface
27. Git History

The repository contains multiple meaningful implementation commits.

Important implementation milestones include:

7492fd9
feat: extract deposition into addressable transcript lines
395b867
fix: clean transcript lines and preserve testimony range
fa8730d
feat: add transcript chunking and topic extraction pipeline

The final implementation also includes grounded evidence validation, final topic integration, and the attorney-facing Streamlit index.

28. Author

Kartik Gupta

DepoIndex — AI-Powered Deposition Topic Index