# LLM Usage

## Model

DepoIndex uses the Google Gemini API for transcript topic extraction. The model used during development was gemini-3.6-flash.

## How the LLM was used

The LLM was used to identify meaningful deposition topics from overlapping transcript chunks and return structured topic information including a concise topic label, start page/line, end page/line, and supporting evidence.

The prompt instructed the model to use only the supplied transcript, avoid inventing facts or locations, preserve exact page/line references, avoid creating a topic for every individual question, combine consecutive discussion of the same subject, and recognize topics that continue across page or chunk boundaries.

## Accepted Suggestions

LLM-generated topic labels and candidate boundaries were used as the initial topic candidates. The structured JSON output was passed to deterministic post-processing and merging.

## Modified Suggestions

Some generated boundaries were manually adjusted when the cited location was valid but the semantic topic boundary was too broad or overlapped with a neighboring topic. Examples include separating professional background from policy research, separating general servicing-transfer discussion from data-transfer regulations, and correcting later adjacent topic boundaries.

The final corrections are implemented reproducibly in src/manual_corrections.py.

## Rejected / Not Relied Upon

The system does not blindly trust LLM-generated page/line references. Locations are checked against the extracted addressable transcript lines using deterministic validation. Topic boundaries are also manually reviewed.

No unsupported facts or external information were intentionally added to the Topic Index.

## Validation

LLM output was validated using:

1. Deterministic page/line validation.
2. Chronological ordering checks.
3. Manual review of 20 topic entries.
4. Review of topic relevance, boundary quality, location accuracy, and redundancy.
5. Deterministic candidate merging and manual boundary corrections.

## API / Reliability Issues

During development, transient API errors including HTTP 503 responses occurred and were handled using retries. Later, the Gemini free-tier request quota was exhausted during the complete deposition run. The pipeline was designed to save successful intermediate results so completed chunks did not need to be reprocessed.

The free-tier quota limitation prevented completion of three independent full LLM pipeline runs. This limitation is documented in the validation report rather than presenting fabricated stability results.

## Human Oversight

The LLM was used as a component of the pipeline rather than as the final authority. Transcript extraction, addressability, deterministic validation, merging, manual review, and final boundary corrections were used to improve reliability and provenance.
