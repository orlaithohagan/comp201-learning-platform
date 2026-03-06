import streamlit as st

from src.concept_map import (
    load_concept_map_data,
    build_graph,
    create_plotly_figure,
    get_topic_lookup,
    get_topic_options,
)


st.set_page_config(page_title="Concept Map", page_icon="🧠", layout="wide")


def render_tool_links(related_tools, selected_topic):

    st.subheader("Related Learning Tools")

    col1, col2, col3 = st.columns(3)

    with col1:
        if "flashcards" in related_tools:
            if st.button("Go to Flashcards"):
                st.session_state["selected_topic"] = selected_topic["label"]
                st.switch_page("pages/Flashcards.py")
        else:
            st.button("Flashcards", disabled=True)

    with col2:
        if "quiz" in related_tools:
            if st.button("Go to Quiz"):
                st.switch_page("pages/Quiz.py")
        else:
            st.button("Quiz", disabled=True)

    with col3:
        if "ai_tutor" in related_tools:
            if st.button("Go to AI Tutor"):
                st.switch_page("pages/AITutor.py")
        else:
            st.button("AI Tutor", disabled=True)


def main():
    st.title("🧠 Concept Map")
    st.markdown(
        """
        Explore how the main COMP201 software engineering topics connect together.
        Hover over nodes in the graph to see a short description, then select a topic
        below to view more detail.
        """
    )

    data = load_concept_map_data()
    graph = build_graph(data)
    fig = create_plotly_figure(graph)
    topic_lookup = get_topic_lookup(data)
    topic_options = get_topic_options(data)

    st.plotly_chart(fig, width = "stretch", config={"displayModeBar": False})

    st.markdown(
        """
        **Legend**

        🔵 Core Topic  
        🟢 Major Topic  
        🟠 Subtopic
        """
        )

    st.markdown("---")
    st.subheader("Select a Topic")

    # selected_label = st.selectbox(
    #     "Choose a concept to view details",
    #     options=list(topic_options.keys()),
    #     index=0
    # )
    labels = ["Select a topic..."] + list(topic_options.keys())

    selected_label = st.selectbox(
        "Choose a concept to view details",
        options=labels,
    )

    if selected_label == "Select a topic...":
        st.stop()

    selected_id = topic_options[selected_label]
    selected_topic = topic_lookup[selected_id]

    st.markdown("### Topic Details")
    st.markdown(f"**Name:** {selected_topic['label']}")
    st.markdown(f"**Category:** {selected_topic['category'].title()}")
    st.markdown(f"**Description:** {selected_topic['description']}")

    related_tools = selected_topic.get("related_tools", [])

    if related_tools:
        st.markdown("**Available Tools:** " + ", ".join(tool.replace("_", " ").title() for tool in related_tools))
    else:
        st.markdown("**Available Tools:** None yet")

    st.markdown("---")
    render_tool_links(related_tools, selected_topic)

    st.info(
        "Version 1 note: the buttons are currently placeholders. "
        "Next, you can connect them to your Flashcards, Quiz, Mini Games, and AI Tutor pages."
    )


if __name__ == "__main__":
    main()