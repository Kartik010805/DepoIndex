OUTPUT_FILE = "data/stability_and_failure_analysis.md"

report = """# Stability and Failure Analysis

## 1. Stability Testing

The assignment requires the complete pipeline to be executed three times and the
runs compared for topic count, topic labels, boundaries, and provenance.

During development, the Gemini free-tier request quota was reached during the
first complete extraction attempt. The extraction successfully processed
chunks 1 through 17, producing 38 candidate topics. Processing stopped at
chunk 18 after the API returned a RESOURCE_EXHAUSTED/429 quota response.

Because the quota prevented three independent complete LLM extraction runs,
three full end-to-end LLM runs are not claimed here.

The downstream deterministic stages were designed to be reproducible. Given
the same candidate-topic input, the merge, manual-correction, provenance
validation, and Topic Index generation produce deterministic results.

Observed stability evidence:

- Candidate extraction: 17 of 25 chunks completed before quota exhaustion.
- Candidate topics from completed chunks: 38.
- Deterministic merge: 38 candidates reduced to 31 merged topics.
- Manual correction: 31 merged topics reduced to 30 final topics.
- Deterministic provenance validation: 30/30 topics passed.
- Manual validation: 20/20 reviewed entries passed the selected criteria.

The main remaining stability risk is therefore the variability of the LLM
extraction stage. Overlapping chunks and deterministic post-processing reduce
the impact of this variability.

## 2. Difficult Case 1: Chunk Boundary

### Problem

A discussion about the witness's professional background continued beyond the
initial chunk boundary. The first extraction produced a topic ending at
11:7, even though the surrounding discussion continued further into the
following transcript pages.

### Expected behavior

The system should recognize that the same subject continues across a chunk
boundary rather than treating the boundary as a semantic topic boundary.

### Improvement

The pipeline uses overlapping chunks. An overlap test showed that the
additional context allowed the model to identify the broader discussion,
extending the candidate topic through 14:12.

This demonstrates why overlapping context is necessary for deposition
segmentation.

## 3. Difficult Case 2: Duplicate ITT Earnings Discussion

### Problem

Two candidate topics were generated for discussion concerning the value of
ITT degrees and post-graduation earnings. The transcript contained a
continuous hypothetical discussion that was re-asked and refined after the
reporter lost part of the conversation.

The two candidates overlapped substantially.

### Expected behavior

The system should represent the continuous discussion as one topic rather
than creating redundant entries simply because the attorney reformulated a
question.

### Improvement

Manual review determined that the discussion was substantively continuous.
The two candidates were therefore merged into one topic spanning:

37:23 -> 42:4

The merge also combines the source-chunk references.

## 4. Difficult Case 3: General Transfer Discussion vs. Regulation Discussion

### Problem

The servicing-transfer discussion and the subsequent discussion of
data-transfer laws and regulations were initially represented with overlapping
ranges.

The initial general transfer topic extended into the specific regulatory
discussion.

### Expected behavior

The boundary should occur at the actual transcript transition rather than
where the chunk ended.

### Improvement

Manual transcript review identified the transition at:

23:7 -> 23:8

The final boundaries are:

- General servicing transfers, process risks, and regulations:
  20:5 -> 23:7
- Student loan servicing data transfer laws and regulations:
  23:8 -> 24:13

This produced non-overlapping topic boundaries at the semantic transition.

## 5. Additional Boundary Cases

Other manual corrections addressed similar issues:

- General for-profit-college background was separated from the ITT-specific
  discussion at 27:12/27:13.
- The ITT degree valuation discussion was separated from the subsequent
  graduate salary-outcome discussion at 34:8/34:9.
- The Vervent-awareness discussion was separated from the evidence-source
  discussion at 36:2/36:3.
- Final borrower disclosures were separated from the later enforceability
  discussion at 58:7/58:8.

These cases demonstrate that semantic topic boundaries do not always coincide
with fixed chunk boundaries.

## 6. Operational Failure

The Gemini API also produced transient 503 responses during development.
Retrying the affected requests allowed processing to continue.

Later, the API returned a 429/RESOURCE_EXHAUSTED response because the
free-tier request limit had been reached. The pipeline was designed to stop
rather than repeatedly retry a quota error.

This behavior prevents unnecessary requests and makes the failure explicit.

## 7. Reliability Improvements

The main reliability mechanisms are:

1. Preserve original deposition page and line addresses during extraction.
2. Use overlapping transcript chunks.
3. Include exact page/line addresses in the LLM input.
4. Request structured JSON rather than unconstrained prose.
5. Use deterministic merging after LLM extraction.
6. Validate every final start/end address against the extracted transcript.
7. Manually review a representative 20-entry sample.
8. Keep transcript-specific corrections in a separate reproducible script.

## 8. Remaining Limitation

The largest unresolved limitation is the inability to perform three complete
independent LLM pipeline runs under the available free-tier API quota.

A stronger final evaluation would repeat the complete extraction stage three
times using the same transcript and prompt, then compare:

- Number of topics
- Topic labels
- Start/end locations
- Overlap and duplication rate
- Major topic coverage

The current implementation is therefore transparent about what was and was
not experimentally established.
"""

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(report)

print("Stability and failure analysis created.")
print(f"Saved to {OUTPUT_FILE}")