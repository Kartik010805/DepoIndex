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

        .provenance {
            font-size: 0.92rem;
            color: #555;
            margin-bottom: 0.5rem;
        }

        .evidence-label {
            font-weight: 600;
            margin-bottom: 0.25rem;
        }

        .section-label {
            font-weight: 650;
            margin-top: 0.5rem;
            margin-bottom: 0.3rem;
        }

        .attorney-note {
            padding: 0.8rem 1rem;
            border-radius: 0.5rem;
            border: 1px solid #ddd;
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

DATA_FILE = Path("data/final_grounded_topics_repaired.json")


@st.cache_data
def load_topics():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
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
            if isinstance(data.get(key), list):
                return data[key]

    raise ValueError(
        "Could not find a topic list in the final grounded topic file."
    )


topics = load_topics()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_value(topic, *keys, default=""):
    for key in keys:
        if key in topic and topic[key] not in (None, ""):
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
        default="No supporting evidence available.",
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
    start_page = get_value(topic, "start_page", "startPage")
    start_line = get_value(topic, "start_line", "startLine")
    end_page = get_value(topic, "end_page", "endPage")
    end_line = get_value(topic, "end_line", "endLine")

    return (
        f"Page {start_page}, Line {start_line} "
        f"→ Page {end_page}, Line {end_line}"
    )


def format_evidence_locations(topic):
    locations = get_evidence_locations(topic)

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
    chunks = get_source_chunks(topic)

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
        f"{format_evidence_locations(topic)}"
    ).lower()


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
    "Search and navigate the deposition through a chronological "
    "index of discussion topics with transcript-level provenance "
    "and evidence locations."
)

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("🔎 Find a Topic")

    search = st.text_input(
        "Search the deposition",
        placeholder="ITT, PEAKS, Vervent, servicing...",
    )

    st.divider()

    st.subheader("Index Overview")

    st.metric(
        "Total Topics",
        len(topics),
    )

    st.metric(
        "Final Validation",
        "43 / 43",
    )

    st.metric(
        "Evidence Grounded",
        "43 / 43",
    )

    st.divider()

    st.subheader("How to use")

    st.write(
        "Search for a subject, select a topic, and review "
        "its exact transcript range, supporting evidence, "
        "evidence locations, and source chunks."
    )

    st.divider()

    st.subheader("Pipeline")

    st.caption("LLM-assisted topic extraction")
    st.caption("Deterministic provenance validation")
    st.caption("Manual boundary review")
    st.caption("Final 43-topic index")

    st.divider()

    st.caption("Source: Persis Yu Deposition")
    st.caption("DepoIndex prototype")


# ============================================================
# SEARCH / FILTER
# ============================================================

filtered_topics = []

for index, topic in enumerate(topics, start=1):

    if (
        not search
        or search.lower() in topic_search_text(topic)
    ):
        filtered_topics.append(
            (index, topic)
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

    topic_options = {
        f"{index}. {get_topic_name(topic)}": index
        for index, topic in filtered_topics
    }

    selected_label = st.selectbox(
        "Select a topic for detailed review",
        list(topic_options.keys()),
    )

    selected_index = topic_options[selected_label]

    selected_topic = topics[selected_index - 1]

    st.divider()

    st.subheader(
        f"Attorney View — Topic {selected_index}"
    )

    st.markdown(
        f'<div class="topic-title">'
        f"{get_topic_name(selected_topic)}"
        f"</div>",
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # Key metadata
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown(
            '<div class="section-label">'
            "Transcript Range"
            "</div>",
            unsafe_allow_html=True,
        )

        st.write(
            get_location(selected_topic)
        )

    with col2:

        st.markdown(
            '<div class="section-label">'
            "Source Chunks"
            "</div>",
            unsafe_allow_html=True,
        )

        st.write(
            format_source_chunks(selected_topic)
        )

    with col3:

        st.markdown(
            '<div class="section-label">'
            "Grounding"
            "</div>",
            unsafe_allow_html=True,
        )

        grounding_source = get_grounding_source(
            selected_topic
        )

        if grounding_source == "grounded_merged_topics":
            st.success("Validated source grounding")
        else:
            st.info(str(grounding_source))

    # --------------------------------------------------------
    # Evidence
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-label">'
        "Supporting Evidence"
        "</div>",
        unsafe_allow_html=True,
    )

    st.write(
        get_evidence(selected_topic)
    )

    # --------------------------------------------------------
    # Evidence locations
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-label">'
        "Evidence Locations"
        "</div>",
        unsafe_allow_html=True,
    )

    evidence_locations = get_evidence_locations(
        selected_topic
    )

    if evidence_locations:

        location_columns = st.columns(
            min(len(evidence_locations), 5)
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
    # Full provenance
    # --------------------------------------------------------

    with st.expander(
        "View full provenance and validation details"
    ):

        st.write(
            "**Topic range:**"
        )

        st.code(
            get_location(selected_topic)
        )

        st.write(
            "**Source chunks:**"
        )

        st.code(
            format_source_chunks(selected_topic)
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


# ============================================================
# CHRONOLOGICAL INDEX
# ============================================================

st.divider()

st.subheader(
    "📚 Chronological Topic Index"
)

st.caption(
    "Use this list to understand the order in which subjects "
    "appear throughout the deposition."
)

for index, topic in filtered_topics:

    name = get_topic_name(topic)
    location = get_location(topic)

    with st.expander(
        f"{index}. {name}"
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

            st.write(location)

        with col2:

            st.markdown(
                '<div class="section-label">'
                "Source Chunks"
                "</div>",
                unsafe_allow_html=True,
            )

            st.write(
                format_source_chunks(topic)
            )

        st.markdown(
            '<div class="section-label">'
            "Supporting Evidence"
            "</div>",
            unsafe_allow_html=True,
        )

        st.write(
            get_evidence(topic)
        )

        st.markdown(
            '<div class="section-label">'
            "Evidence Locations"
            "</div>",
            unsafe_allow_html=True,
        )

        st.write(
            format_evidence_locations(topic)
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