DepoIndex
AI-Powered Deposition Topic Index
DepoIndex is an AI-assisted legal transcript analysis prototype that converts a deposition transcript into a
chronological, attorney-verifiable topic index. The system identifies meaningful discussion topics, determines topic
boundaries, and preserves exact transcript page/line provenance so every indexed topic can be traced back to the
underlying testimony.
1. Problem
Long deposition transcripts are difficult to navigate manually. A useful deposition index should allow an attorney or
reviewer to quickly determine what topics were discussed, when each topic began and ended, and exactly where the
underlying testimony can be verified. DepoIndex addresses this by combining LLM-assisted topic segmentation with
deterministic provenance validation and human review.
2. System Architecture
Deposition PDF
|
v
Transcript Extraction
|
v
Addressable Transcript
(Page + Line + Text)
|
v
Overlapping Chunks
|
v
Gemini Topic Extraction
|
v
Candidate Topics
|
v
Deterministic Topic Merging
|
v
Manual Boundary Review
|
v
Provenance Validation
|
v
Final Topic Index
3. Key Design Decisions
Preserve Page/Line Provenance
Transcript page and line information is preserved during extraction and chunking. Every topic can therefore be traced
from its Topic label to its page/line range, addressable transcript line, and original deposition.
Overlapping Chunks
The transcript is divided into overlapping chunks so topics that continue across chunk boundaries receive surrounding
context.
Chunk size: 100 transcript lines
Overlap: 20 transcript lines
Step: 80 transcript lines
LLM-Assisted Topic Segmentation
Google Gemini is used to identify meaningful discussion topics from transcript chunks. The model is instructed to use
only supplied transcript content, avoid invented facts, preserve exact page/line references, avoid creating a topic for
every question, combine consecutive discussion of the same subject, and return structured JSON.
Deterministic Post-Processing
LLM-generated candidates are processed using deterministic range overlap and label similarity logic to reduce
redundant topic entries.
Manual Boundary Correction
Manual review is used where technically valid locations are not good semantic boundaries. Corrections are
implemented reproducibly in src/manual_corrections.py.
4. Final Output
43 topics are currently present in the final Topic Index. Each topic contains a topic label, start page/line, end
page/line, supporting evidence, and source chunk information where available.
Human-readable: data/topic_index.md
Structured JSON: data/manual_corrected_topics.json
5. Example Topic
Topic:
Scope of Expert Retention and Testimony
Start: Page 8, Line 24
End: Page 10, Line 4
Supporting Evidence:
The witness discusses being retained as an expert witness
and the scope of her expected testimony.
6. Validation
Deterministic Validation
The validator checks required fields, existence of start/end page-line locations, valid ordering, and chronological
ordering of topics. Result: 43/43 final topics passed.
Manual Validation
20 topic entries were manually reviewed for location accuracy, topic relevance, boundary quality, and redundancy.
Artifacts:
data/manual_validation_results.json
data/validation_report.md
7. Failure Analysis
Failure 1 — Chunk Boundary Errors
A topic can appear to end at a chunk boundary even when the discussion continues. Overlapping chunks were
introduced to provide adjacent context.
Failure 2 — Similar Topics
Related discussions can receive different labels. Deterministic merging followed by manual review was used to
reduce unnecessary duplication.
Failure 3 — Valid Location but Poor Boundary
A location can exist in the transcript while still being a weak semantic boundary. Manual inspection of surrounding
lines and reproducible corrections address this issue.
8. Stability Testing
The assignment requires three complete independent pipeline runs. The complete three-run LLM experiment could
not be completed because the available Gemini free-tier request quota was exhausted during processing. Therefore,
this project does not claim three complete independent LLM runs. This limitation is documented in the validation
report.
9. Reliability Measures
1. Exact page/line information preserved during extraction
2. Transcript cleaning before topic extraction
3. Overlapping chunks
4. Structured JSON LLM output
5. Deterministic provenance validation
6. Deterministic candidate merging
7. Manual review of 20 entries
8. Reproducible manual boundary corrections
9. Intermediate result persistence
10. Project Structure
DepoIndex/
|-- src/
| |-- extract_text.py
| |-- segment.py
| |-- chunk.py
| |-- segment_topics.py
| |-- run_pipeline.py
| |-- merge_topics.py
| |-- manual_corrections.py
| |-- validate_merged.py
| |-- manual_validation.py
| |-- create_validation_results.py
| |-- create_validation_report.py
| `-- create_topic_index.py
|
|-- data/
| |-- lines.json
| |-- chunks.json
| |-- candidate_topics.json
| |-- manual_corrected_topics.json
| |-- manual_validation_results.json
| |-- validation_report.md
| `-- topic_index.md
|
|-- llm_usage.md
|-- README.md
|-- requirements.txt
`-- .gitignore
11. Installation
git clone <REPOSITORY_URL>
cd DepoIndex
python -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements.txt
12. API Configuration
DepoIndex uses the Gemini API for LLM-based topic extraction. The API key must be supplied through an
environment variable and must never be committed to the repository.
export GEMINI_API_KEY="YOUR_API_KEY"
13. Running the Pipeline
python src/extract_text.py
python src/segment.py
python src/chunk.py
python src/run_pipeline.py
python src/merge_topics.py
python src/manual_corrections.py
python src/validate_merged.py
python src/create_topic_index.py
python src/manual_validation.py
python src/create_validation_results.py
python src/create_validation_report.py
14. Reproducibility
The pipeline separates LLM-assisted extraction from deterministic processing. Successful intermediate results are
persisted so completed chunks do not need to be regenerated after transient API failures or quota interruptions.
15. LLM Usage
AI assistance was used during development, and Gemini was used for transcript topic extraction. Model usage,
prompting approach, accepted and modified suggestions, validation, API failures, free-tier limitations, and human
oversight are documented in llm_usage.md.
16. Git History
The repository intentionally contains multiple meaningful commits rather than a single final commit.
Meaningful earlier implementation commit:
fa8730d feat: add transcript chunking and topic extraction pipeline
Final submission commit SHA: see the final submission commit recorded below
17. Limitations
- LLM-generated topic segmentation can vary between runs.
- Three complete independent LLM runs could not be completed because of available free-tier quota.
- Manual validation covers 20 entries rather than every topic.
- Candidate merging relies partly on deterministic label similarity.
- The prototype was evaluated on a single deposition.
- The current prototype focuses on indexing rather than full legal-document retrieval.
18. Future Improvements
- Semantic embedding-based topic merging
- Automated boundary-quality scoring
- Full three-run stability testing
- Search across multiple depositions
- Related-topic retrieval
- Direct navigation from a topic to transcript context
- Cross-deposition topic comparison
- Confidence scoring for topic boundaries
19. Submission Deliverables
- GitHub repository
- Working application URL
- Final Topic Index
- Structured JSON output
- Validation report
- LLM usage documentation
- Presentation slides
20. Author
Kartik Gupta
DepoIndex — AI-Powered Deposition Topic Index