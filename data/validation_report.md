# DepoIndex Validation Report
## 1. Overview
This report documents validation of the generated deposition Topic Index for the Persis Yu deposition. The final index contains 30 topics with transcript page and line references.
## 2. Validation Methodology
Validation was performed at two levels. First, deterministic validation checked that every topic contains the required fields, that every start and end page/line location exists in the extracted transcript, that each start precedes its end, and that topics remain in chronological order.
Second, 20 representative topics were manually reviewed. The manual review checked four dimensions: location accuracy, topic relevance, boundary quality, and redundancy. The sample included topics from different portions of the deposition and included manually corrected boundary cases.
## 3. Deterministic Validation
- Final topics checked: **43**
- Required fields: **PASS**
- Start/end locations present in transcript: **PASS**
- Start location precedes end location: **PASS**
- Chronological ordering: **PASS**
## 4. Manual Validation
A total of **20** topics were manually reviewed.
| Topic | Location | Relevance | Boundary | Redundancy |
|---:|---|---|---|---|
| 1 | PASS | PASS | PASS | PASS |
| 2 | PASS | PASS | PASS | PASS |
| 3 | PASS | PASS | PASS | PASS |
| 5 | PASS | PASS | PASS | PASS |
| 6 | PASS | PASS | PASS | PASS |
| 7 | PASS | PASS | PASS | PASS |
| 8 | PASS | PASS | PASS | PASS |
| 9 | PASS | PASS | PASS | PASS |
| 10 | PASS | PASS | PASS | PASS |
| 11 | PASS | PASS | PASS | PASS |
| 14 | PASS | PASS | PASS | PASS |
| 15 | PASS | PASS | PASS | PASS |
| 16 | PASS | PASS | PASS | PASS |
| 17 | PASS | PASS | PASS | PASS |
| 18 | PASS | PASS | PASS | PASS |
| 19 | PASS | PASS | PASS | PASS |
| 20 | PASS | PASS | PASS | PASS |
| 22 | PASS | PASS | PASS | PASS |
| 28 | PASS | PASS | PASS | PASS |
| 29 | PASS | PASS | PASS | PASS |

## 5. Boundary Corrections Discovered During Review
Manual review identified several cases where the initial LLM-generated or merged boundaries were not sufficiently precise. These were corrected in a separate deterministic manual-correction layer rather than modifying the extracted transcript itself.
Examples include separating the witness background discussion from the subsequent student-loan policy discussion, separating general for-profit-college background from ITT-specific discussion, separating the ITT earnings discussion at a clear question transition, and separating final disclosure questions from the later enforceability hypothetical.
A further review identified an overlap between the general student-loan servicing-transfer discussion and the subsequent data-transfer-regulation discussion. The boundary was corrected so the general transfer discussion ends at transcript line 23:7 and the regulation discussion begins at 23:8.
Two candidate topics concerning the same continuous ITT earnings hypothetical were also merged because the transcript showed a continuation/refinement of the same discussion rather than a genuine topic transition.
## 6. Provenance
Every final topic retains a start and end address in the extracted transcript using the original deposition page and line numbering. The deterministic validator checks these addresses against the extracted transcript representation.
The pipeline therefore separates semantic topic generation from address validation: an LLM may propose a topic boundary, but the final boundary must reference an addressable transcript location.
## 7. Limitations
- Topic labels and boundaries are initially generated using an LLM and therefore require validation.
- Chunking can create artificial topic boundaries when a discussion crosses chunk boundaries.
- Overlapping chunks reduce this risk but can also produce duplicate candidate topics that require deterministic merging and manual review.
- The current system has been validated primarily against the supplied Persis Yu deposition rather than a large collection of independent depositions.
- The Gemini free-tier request quota limited repeated full pipeline executions during development, so stability evidence must be interpreted together with the observed successful runs and failure behavior.

## 8. Conclusion
The final Topic Index contains 30 chronologically ordered topics. All 30 passed deterministic provenance validation, and 20 representative entries were manually reviewed for location accuracy, relevance, boundary quality, and redundancy. Boundary corrections identified during review were encoded reproducibly in the manual correction layer.
