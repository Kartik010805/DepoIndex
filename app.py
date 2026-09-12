import json
from pathlib import Path

import streamlit as st


# -----------------------------
# Page configuration
# -----------------------------
st.set_page_config(
    page_title="DepoIndex",
    page_icon="📑",
    layout="wide",
)


# -----------------------------
# Load topic data
# -----------------------------
DATA_FILE = Path("data/manual_corrected_topics.json")


@st.cache_data
def load_topics():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


topics = load_topics()["topics"]


# -----------------------------
# Helper functions
# -----------------------------
def get_value(topic, *keys, default=""):
    for key in keys:
        if key in topic and topic[key] not in (None, ""):
            return topic[key]
    return default


def location_text(topic):
    start_page = get_value(topic, "start_page", "startPage")
    start_line = get_value(topic, "start_line", "startLine")
    end_page = get_value(topic, "end_page", "endPage")
    end_line = get_value(topic, "end_line", "endLine")

    return f"Page {start_page}, Line {start_line} → Page {end_page}, Line {end_line}"


# -----------------------------
# Header
# -----------------------------
st.title("📑 DepoIndex")
st.subheader("AI-Powered Deposition Topic Index")

st.write(
    "Navigate the deposition through an attorney-verifiable chronological "
    "index of discussion topics."
)

st.divider()


# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.header("Index Overview")

    st.metric("Total Topics", len(topics))

    st.write(
        "Each topic includes its transcript page/line range and supporting "
        "evidence where available."
    )

    st.divider()

    st.caption("DepoIndex")
    st.caption("AI-assisted legal transcript analysis prototype")


# -----------------------------
# Search
# -----------------------------
search = st.text_input(
    "🔎 Search topics",
    placeholder="Try: ITT, PEAKS, Vervent, loan servicing...",
)


# -----------------------------
# Filter topics
# -----------------------------
filtered_topics = []

for index, topic in enumerate(topics, start=1):
    label = get_value(topic, "topic", "label", "title", default="Untitled Topic")
    evidence = get_value(
        topic,
        "supporting_evidence",
        "supportingEvidence",
        "evidence",
        default="",
    )

    searchable_text = f"{label} {evidence}".lower()

    if not search or search.lower() in searchable_text:
        filtered_topics.append((index, topic))


st.write(f"Showing **{len(filtered_topics)}** of **{len(topics)}** topics")


# -----------------------------
# Topic cards
# -----------------------------
for index, topic in filtered_topics:

    label = get_value(
        topic,
        "topic",
        "label",
        "title",
        default="Untitled Topic",
    )

    evidence = get_value(
        topic,
        "supporting_evidence",
        "supportingEvidence",
        "evidence",
        default="No supporting evidence available.",
    )

    location = location_text(topic)

    with st.container(border=True):

        st.markdown(f"### {index}. {label}")

        st.caption(f"📍 {location}")

        if evidence:
            with st.expander("View supporting evidence"):
                st.write(evidence)


# -----------------------------
# Empty result message
# -----------------------------
if not filtered_topics:
    st.warning("No topics matched your search.")
