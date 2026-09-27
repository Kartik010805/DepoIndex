import json
from pathlib import Path

import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="DepoIndex | Attorney Topic Index",
    page_icon="📑",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM STYLING
# ============================================================

st.markdown(
    """
    <style>
        .main-title {
            font-size: 2.6rem;
            font-weight: 700;
            margin-bottom: 0.1rem;
        }

        .subtitle {
            font-size: 1.1rem;
            color: #666;
            margin-bottom: 1.5rem;
        }

        .topic-title {
            font-size: 1.25rem;
            font-weight: 650;
            margin-bottom: 0.35rem;
        }

        .section-label {
            font-weight: 650;
            margin-top: 0.5rem;
            margin-bottom: 0.3rem;
        }

        .review-note {
            padding: 0.8rem 1rem;
            border-radius: 0.5rem;
            border: 1px solid #e0b000;
            margin-bottom: 1rem;
        }

        .footer {
            text-align: center;
            color: #777;
            font-size: 0.85rem;
            margin-top: 2rem;
            padding-top: 1rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATA LOADING
# ============================================================

DATA_FILE = Path(
    "data/final_grounded_topics_validated.json"
)


@st.cache_data
def load_topics():

    with open(
        DATA_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        data = json.load(file)

    if isinstance(data, list):
        return data

    if isinstance(data, dict):

        for key in [
            "topics",
            "final_topics",
            "merged_topics",
            "data",
        ]:

            if isinstance(
                data.get(key),
                list,
            ):

                return data[key]

    raise ValueError(
        "Could not find a topic list in "
        "the validated topic file."
    )


topics = load_topics()


# ============================================================
# VALIDATION HELPERS
# ============================================================

def get_validation_state(topic):

    state = topic.get(
        "validation_state"
    )

    if isinstance(state, dict):

        return state

    return {
        "structural": "UNKNOWN",
        "referential": "UNKNOWN",
        "grounding": "UNKNOWN",
        "semantic": "UNKNOWN",
        "overall_status": "UNKNOWN",
        "review_reasons": [],
    }


def get_validation_status(topic):

    state = get_validation_state(
        topic
    )

    return state.get(
        "overall_status",
        "UNKNOWN",
    )


def validation_counts():

    counts = {
        "PASS": 0,
        "NEEDS_HUMAN_REVIEW": 0,
        "FAIL": 0,
        "UNKNOWN": 0,
    }

    for topic in topics:

        status = get_validation_status(
            topic
        )

        if status not in counts:
            status = "UNKNOWN"

        counts[status] += 1

    return counts


counts = validation_counts()


def status_label(status):

    if status == "PASS":
        return "PASS"

    if status == "NEEDS_HUMAN_REVIEW":
        return "NEEDS HUMAN REVIEW"

    if status == "FAIL":
        return "FAIL"

    return "UNKNOWN"


# ============================================================
# GENERAL HELPERS
# ============================================================

def get_value(
    topic,
    *keys,
    default="",
):

    for key in keys:

        if (
            key in topic
            and topic[key] not in (
                None,
                "",
            )
        ):

            return topic[key]

    return default


def get_topic_name(topic):

    return get_value(
        topic,
        "topic",
        "label",
        "title",
        default="Untitled Topic",
    )


def get_evidence(topic):

    return get_value(
        topic,
        "evidence",
        "supporting_evidence",
        "supportingEvidence",
        default=(
            "No supporting evidence available."
        ),
    )


def get_source_chunks(topic):

    return get_value(
        topic,
        "source_chunks",
        "sourceChunks",
        default=[],
    )


def get_evidence_locations(topic):

    return get_value(
        topic,
        "evidence_locations",
        "evidenceLocations",
        default=[],
    )


def get_grounding_source(topic):

    return get_value(
        topic,
        "grounding_source",
        "groundingSource",
        default="Not specified",
    )


def get_location(topic):

    start_page = get_value(
        topic,
        "start_page",
        "startPage",
    )

    start_line = get_value(
        topic,
        "start_line",
        "startLine",
    )

    end_page = get_value(
        topic,
        "end_page",
        "endPage",
    )

    end_line = get_value(
        topic,
        "end_line",
        "endLine",
    )

    return (
        f"Page {start_page}, Line {start_line} "
        f"→ Page {end_page}, Line {end_line}"
    )


def format_evidence_locations(topic):

    locations = get_evidence_locations(
        topic
    )

    if not locations:
        return "No evidence locations recorded."

    formatted = []

    for location in locations:

        page = location.get("page")
        line = location.get("line")

        formatted.append(
            f"Page {page}, Line {line}"
        )

    return " · ".join(formatted)


def format_source_chunks(topic):

    chunks = get_source_chunks(
        topic
    )

    if not chunks:
        return "None recorded"

    if isinstance(chunks, list):

        return ", ".join(
            str(chunk)
            for chunk in chunks
        )

    return str(chunks)


def topic_search_text(topic):

    return (
        f"{get_topic_name(topic)} "
        f"{get_evidence(topic)} "
        f"{format_evidence_locations(topic)} "
        f"{format_source_chunks(topic)}"
    ).lower()


# ============================================================
# VALIDATION DISPLAY
# ============================================================

def display_validation_status(topic):

    state = get_validation_state(
        topic
    )

    status = state.get(
        "overall_status",
        "UNKNOWN",
    )

    if status == "PASS":

        st.success(
            "Validation Status: PASS"
        )

    elif status == "NEEDS_HUMAN_REVIEW":

        st.warning(
            "Validation Status: NEEDS HUMAN REVIEW"
        )

        reasons = state.get(
            "review_reasons",
            [],
        )

        if reasons:

            st.markdown(
                '<div class="review-note">'
                "<strong>Human review required</strong>"
                "<br><br>"
                + "<br><br>".join(
                    str(reason)
                    for reason in reasons
                )
                + "</div>",
                unsafe_allow_html=True,
            )

    elif status == "FAIL":

        st.error(
            "Validation Status: FAIL"
        )

    else:

        st.info(
            "Validation Status: UNKNOWN"
        )


def display_validation_levels(topic):

    state = get_validation_state(
        topic
    )

    st.write(
        "**Validation levels:**"
    )

    validation_columns = st.columns(
        4
    )

    levels = [
        (
            validation_columns[0],
            "Structural",
            state.get(
                "structural",
                "UNKNOWN",
            ),
        ),
        (
            validation_columns[1],
            "Referential",
            state.get(
                "referential",
                "UNKNOWN",
            ),
        ),
        (
            validation_columns[2],
            "Grounding",
            state.get(
                "grounding",
                "UNKNOWN",
            ),
        ),
        (
            validation_columns[3],
            "Semantic",
            state.get(
                "semantic",
                "UNKNOWN",
            ),
        ),
    ]

    for column, label, value in levels:

        with column:

            if value == "PASS":

                st.success(
                    f"{label}\n\nPASS"
                )

            elif value == "NEEDS_HUMAN_REVIEW":

                st.warning(
                    f"{label}\n\n"
                    "NEEDS REVIEW"
                )

            elif value == "FAIL":

                st.error(
                    f"{label}\n\nFAIL"
                )

            else:

                st.info(
                    f"{label}\n\n{value}"
                )


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">📑 DepoIndex</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    "Attorney-Facing Deposition Topic Index"
    "</div>",
    unsafe_allow_html=True,
)

st.write(
    "Search and navigate the deposition through a "
    "chronological index of discussion topics with "
    "transcript-level provenance, evidence locations, "
    "and validation status."
)

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("🔎 Find a Topic")

    search = st.text_input(
        "Search the deposition",
        placeholder=(
            "ITT, PEAKS, Vervent, servicing..."
        ),
    )

    st.divider()

    st.subheader(
        "Index Overview"
    )

    st.metric(
        "Total Topics",
        len(topics),
    )

    st.metric(
        "Automated Validation",
        f"{counts['PASS']} / {len(topics)}",
    )

    st.metric(
        "Human Review",
        counts["NEEDS_HUMAN_REVIEW"],
    )

    st.metric(
        "Hard Failures",
        counts["FAIL"],
    )

    st.divider()

    st.subheader(
        "Validation Meaning"
    )

    st.caption(
        "PASS — all validation levels passed."
    )

    st.caption(
        "NEEDS HUMAN REVIEW — automated checks "
        "cannot establish semantic support confidently."
    )

    st.caption(
        "FAIL — one or more hard validation checks failed."
    )

    st.divider()

    st.subheader(
        "How to use"
    )

    st.write(
        "Search for a subject, select a topic, and "
        "review its exact transcript range, supporting "
        "evidence, evidence locations, source chunks, "
        "and validation state."
    )

    st.divider()

    st.subheader(
        "Pipeline"
    )

    st.caption(
        "LLM-assisted topic extraction"
    )

    st.caption(
        "Deterministic provenance validation"
    )

    st.caption(
        "Semantic evidence validation"
    )

    st.caption(
        "Human-review routing"
    )

    st.caption(
        "Final 43-topic index"
    )

    st.divider()

    st.caption(
        "Source: Persis Yu Deposition"
    )

    st.caption(
        "DepoIndex prototype"
    )


# ============================================================
# SEARCH / FILTER
# ============================================================

filtered_topics = []

for index, topic in enumerate(
    topics,
    start=1,
):

    if (
        not search
        or search.lower()
        in topic_search_text(topic)
    ):

        filtered_topics.append(
            (
                index,
                topic,
            )
        )


# ============================================================
# RESULTS SUMMARY
# ============================================================

if search:

    st.subheader(
        f"Search results for: `{search}`"
    )

else:

    st.subheader(
        "Deposition Topic Index"
    )


st.write(
    f"Showing **{len(filtered_topics)}** "
    f"of **{len(topics)}** topics"
)


# ============================================================
# ATTORNEY VIEW
# ============================================================

if filtered_topics:

    topic_options = {}

    for index, topic in filtered_topics:

        status = get_validation_status(
            topic
        )

        topic_options[
            (
                f"{index}. "
                f"{get_topic_name(topic)} "
                f"[{status_label(status)}]"
            )
        ] = index

    selected_label = st.selectbox(
        "Select a topic for detailed review",
        list(topic_options.keys()),
    )

    selected_index = topic_options[
        selected_label
    ]

    selected_topic = topics[
        selected_index - 1
    ]

    st.divider()

    st.subheader(
        f"Attorney View — Topic {selected_index}"
    )

    st.markdown(
        '<div class="topic-title">'
        f"{get_topic_name(selected_topic)}"
        "</div>",
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # VALIDATION STATUS
    # --------------------------------------------------------

    display_validation_status(
        selected_topic
    )

    display_validation_levels(
        selected_topic
    )

    # --------------------------------------------------------
    # KEY METADATA
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(
        3
    )

    with col1:

        st.markdown(
            '<div class="section-label">'
            "Transcript Range"
            "</div>",
            unsafe_allow_html=True,
        )

        st.write(
            get_location(
                selected_topic
            )
        )

    with col2:

        st.markdown(
            '<div class="section-label">'
            "Source Chunks"
            "</div>",
            unsafe_allow_html=True,
        )

        st.write(
            format_source_chunks(
                selected_topic
            )
        )

    with col3:

        st.markdown(
            '<div class="section-label">'
            "Grounding"
            "</div>",
            unsafe_allow_html=True,
        )

        grounding_source = (
            get_grounding_source(
                selected_topic
            )
        )

        st.write(
            str(grounding_source)
        )

    # --------------------------------------------------------
    # EVIDENCE
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-label">'
        "Supporting Evidence"
        "</div>",
        unsafe_allow_html=True,
    )

    st.write(
        get_evidence(
            selected_topic
        )
    )

    # --------------------------------------------------------
    # EVIDENCE LOCATIONS
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-label">'
        "Evidence Locations"
        "</div>",
        unsafe_allow_html=True,
    )

    evidence_locations = (
        get_evidence_locations(
            selected_topic
        )
    )

    if evidence_locations:

        location_columns = st.columns(
            min(
                len(evidence_locations),
                5,
            )
        )

        for column, location in zip(
            location_columns,
            evidence_locations,
        ):

            with column:

                st.info(
                    f"Page {location.get('page')}\n\n"
                    f"Line {location.get('line')}"
                )

    else:

        st.warning(
            "No evidence locations recorded."
        )

    # --------------------------------------------------------
    # FULL PROVENANCE
    # --------------------------------------------------------

    with st.expander(
        "View full provenance and validation details"
    ):

        st.write(
            "**Topic range:**"
        )

        st.code(
            get_location(
                selected_topic
            )
        )

        st.write(
            "**Source chunks:**"
        )

        st.code(
            format_source_chunks(
                selected_topic
            )
        )

        st.write(
            "**Evidence locations:**"
        )

        st.json(
            evidence_locations
        )

        st.write(
            "**Grounding source:**"
        )

        st.code(
            str(
                get_grounding_source(
                    selected_topic
                )
            )
        )

        st.write(
            "**Validation state:**"
        )

        st.json(
            get_validation_state(
                selected_topic
            )
        )

        if (
            "semantic_validation"
            in selected_topic
        ):

            st.write(
                "**Semantic validation:**"
            )

            st.json(
                selected_topic[
                    "semantic_validation"
                ]
            )

        metadata = selected_topic.get(
            "metadata"
        )

        if metadata:

            st.write(
                "**Deposition metadata:**"
            )

            st.json(
                metadata
            )


# ============================================================
# CHRONOLOGICAL INDEX
# ============================================================

st.divider()

st.subheader(
    "📚 Chronological Topic Index"
)

st.caption(
    "Use this list to understand the order in which "
    "subjects appear throughout the deposition."
)


for index, topic in filtered_topics:

    name = get_topic_name(
        topic
    )

    location = get_location(
        topic
    )

    status = get_validation_status(
        topic
    )

    with st.expander(
        f"{index}. {name} "
        f"[{status_label(status)}]"
    ):

        col1, col2 = st.columns(
            [2, 1]
        )

        with col1:

            st.markdown(
                '<div class="section-label">'
                "Transcript Range"
                "</div>",
                unsafe_allow_html=True,
            )

            st.write(
                location
            )

        with col2:

            st.markdown(
                '<div class="section-label">'
                "Source Chunks"
                "</div>",
                unsafe_allow_html=True,
            )

            st.write(
                format_source_chunks(
                    topic
                )
            )

        st.markdown(
            '<div class="section-label">'
            "Validation Status"
            "</div>",
            unsafe_allow_html=True,
        )

        st.write(
            status_label(status)
        )

        st.markdown(
            '<div class="section-label">'
            "Supporting Evidence"
            "</div>",
            unsafe_allow_html=True,
        )

        st.write(
            get_evidence(
                topic
            )
        )

        st.markdown(
            '<div class="section-label">'
            "Evidence Locations"
            "</div>",
            unsafe_allow_html=True,
        )

        st.write(
            format_evidence_locations(
                topic
            )
        )


# ============================================================
# EMPTY SEARCH RESULT
# ============================================================

if not filtered_topics:

    st.warning(
        "No topics matched your search. "
        "Try another keyword such as ITT, PEAKS, "
        "Vervent, servicing, CFPB, or loans."
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        DepoIndex · AI-assisted deposition analysis ·
        Provenance-preserving topic indexing
    </div>
    """,
    unsafe_allow_html=True,
)