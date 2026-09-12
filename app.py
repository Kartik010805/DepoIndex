import json
from pathlib import Path

import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="DepoIndex | Deposition Topic Index",
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
            font-size: 1.15rem;
            font-weight: 650;
            margin-bottom: 0.25rem;
        }

        .provenance {
            font-size: 0.9rem;
            color: #555;
            margin-bottom: 0.6rem;
        }

        .evidence-label {
            font-weight: 600;
            margin-bottom: 0.25rem;
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

DATA_FILE = Path("data/manual_corrected_topics.json")


@st.cache_data
def load_topics():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data["topics"]


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


def location_text(topic):
    start_page = get_value(topic, "start_page", "startPage")
    start_line = get_value(topic, "start_line", "startLine")
    end_page = get_value(topic, "end_page", "endPage")
    end_line = get_value(topic, "end_line", "endLine")

    return (
        f"Page {start_page}, Line {start_line} "
        f"→ Page {end_page}, Line {end_line}"
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
    "AI-Powered Deposition Topic Index"
    "</div>",
    unsafe_allow_html=True,
)

st.write(
    "Navigate the deposition through a chronological, "
    "attorney-verifiable index of discussion topics."
)

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("🔎 Topic Navigation")

    search = st.text_input(
        "Search topics",
        placeholder="ITT, PEAKS, Vervent...",
    )

    st.divider()

    st.subheader("Index Overview")

    st.metric(
        "Total Topics",
        len(topics),
    )

    st.metric(
        "Manually Reviewed",
        "20",
    )

    st.metric(
        "Validation",
        "43 / 43",
    )

    st.divider()

    st.subheader("About")

    st.write(
        "DepoIndex uses LLM-assisted topic extraction "
        "combined with deterministic validation and "
        "manual boundary review."
    )

    st.divider()

    st.caption("Source: Persis Yu Deposition")
    st.caption("Prototype for legal transcript navigation")


# ============================================================
# SEARCH / FILTER
# ============================================================

filtered_topics = []

for index, topic in enumerate(topics, start=1):

    name = get_topic_name(topic)
    evidence = get_evidence(topic)

    searchable_text = (
        f"{name} {evidence}"
    ).lower()

    if not search or search.lower() in searchable_text:
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
    st.subheader("Deposition Topic Index")

st.write(
    f"Showing **{len(filtered_topics)}** "
    f"of **{len(topics)}** topics"
)


# ============================================================
# TOPIC LIST
# ============================================================

for index, topic in filtered_topics:

    name = get_topic_name(topic)
    evidence = get_evidence(topic)
    location = location_text(topic)
    source_chunks = get_source_chunks(topic)

    with st.container(border=True):

        st.markdown(
            f'<div class="topic-title">'
            f"{index}. {name}"
            f"</div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="provenance">'
            f"📍 <b>Transcript location:</b> {location}"
            f"</div>",
            unsafe_allow_html=True,
        )

        if source_chunks:
            if isinstance(source_chunks, list):
                chunk_text = ", ".join(
                    str(chunk)
                    for chunk in source_chunks
                )
            else:
                chunk_text = str(source_chunks)

            st.caption(
                f"Source chunk(s): {chunk_text}"
            )

        with st.expander(
            "View supporting evidence"
        ):

            st.markdown(
                '<div class="evidence-label">'
                "Supporting Evidence"
                "</div>",
                unsafe_allow_html=True,
            )

            st.write(evidence)


# ============================================================
# EMPTY SEARCH RESULT
# ============================================================

if not filtered_topics:

    st.warning(
        "No topics matched your search. "
        "Try another keyword."
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