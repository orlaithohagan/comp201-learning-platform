import streamlit as st 
import json
from pathlib import Path

#Page Configuration 

st.set_page_config(page_title="Flashcards", page_icon=":books:", layout="centered")
st.title("Study - Flashcards")

# Load flashcards data from JSON file
DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "flashcards.json"
flashcards_data = []
if DATA_PATH.exists():
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as file:
            flashcards_data = json.load(file)
            if not isinstance(flashcards_data, list):
                st.error("Flashcards JSON must be a list of objects.")
                flashcards_data = []
    except json.JSONDecodeError:
        st.error("Failed to parse flashcards JSON — please check the file format.")
else:
    st.warning("No flashcards data found.")


def list_topics():
    topics = set(card.get('topic') for card in flashcards_data if card.get('topic'))
    return sorted(topics)
def get_flashcards_by_topic(topic):
    return [card for card in flashcards_data if card['topic'] == topic]
    
# Sidebar for topic selection
st.sidebar.header("Select Topic")
topics = list_topics()
if topics:
    selected_topic = st.sidebar.selectbox("Topics", options=topics)
else:
    st.sidebar.info("No topics available.")
    selected_topic = None

if selected_topic:
    flashcards = get_flashcards_by_topic(selected_topic)
    if flashcards:
        st.header(f"Flashcards - {selected_topic}")
        for card in flashcards:
            question = card.get('prompt', '<no question>')
            answer = card.get('answer', '<no answer>')
            with st.expander(question):
                st.write(answer)
    else:
        st.info("No flashcards available for this topic.")
else:
    st.info("Please select a topic from the sidebar.")

