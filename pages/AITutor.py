import streamlit as st
from src.services.auth_ui import require_login, logout_button
from src.services.navigation import render_sidebar_navigation
from src.ai_tutor import ask_ai_tutor
from src.services.theme import apply_styles

st.set_page_config(page_title="AI Tutor", layout="wide")
apply_styles("styles/tutor.css")

require_login()
render_sidebar_navigation("pages/AITutor.py")
logout_button()

WELCOME_MESSAGE = (
    "Hi! I'm your COMP201 AI tutor. "
    "Ask me anything about software engineering concepts, and I'll do my best to explain them clearly."
)

st.title("AI Tutor")
st.markdown(
    "Your AI-powered COMP201 tutor. Ask questions, review weak topics, and get personalised explanations."
)
st.caption("Powered by OpenAI API with retrieval from COMP201 course materials")

if "ai_tutor_messages" not in st.session_state:
    st.session_state.ai_tutor_messages = [
        {
            "role": "assistant",
            "content": WELCOME_MESSAGE,
        }
    ]

if "tutor_prefill" in st.session_state:
    prefill_topic = st.session_state.pop("tutor_prefill")
    user_message = f"""
    I am struggling with {prefill_topic}.
    Explain it clearly, simply, and give an example if possible.
    """.strip()

    st.session_state.ai_tutor_messages.append(
        {"role": "user", "content": user_message}
    )

    with st.spinner("Loading tutor support..."):
        answer, relevant_cards = ask_ai_tutor(
            user_message,
            st.session_state.ai_tutor_messages
        )

    st.session_state.ai_tutor_messages.append(
        {
            "role": "assistant",
            "content": answer,
            "sources": relevant_cards
        }
    )

def send_message(user_message: str):
    st.session_state.ai_tutor_messages.append(
        {"role": "user", "content": user_message}
    )

    with st.spinner("Thinking..."):
        answer, relevant_cards = ask_ai_tutor(
            user_message,
            st.session_state.ai_tutor_messages
        )

    st.session_state.ai_tutor_messages.append(
        {
            "role": "assistant",
            "content": answer,
            "sources": relevant_cards
        }
    )


for i, message in enumerate(st.session_state.ai_tutor_messages):
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            st.markdown(f"{message['content']}")

            if i == len(st.session_state.ai_tutor_messages) - 1:
                st.caption("Try asking: 'give me an example', 'summarise this', or 'explain that more simply'")

            sources = message.get("sources", [])
            if sources:
                with st.expander("View course context used"):
                    for j, card in enumerate(sources, start=1):
                        st.markdown(f"**{j}. {card['topic']}**")
                        st.markdown(f"- **Match score:** {card['score']}")
                        st.markdown(f"> **Q:** {card['prompt']}")
                        st.markdown(f"> **A:** {card['answer']}")
                        st.markdown("---")
        else:
            st.markdown(f"{message['content']}")


col1, col2 = st.columns([6, 1])

with col1:
    user_input = st.chat_input("Ask a question about COMP201 software engineering...")

with col2:
    if st.button("Clear chat", help="Clear chat"):
        st.session_state.ai_tutor_messages = [
            {
                "role": "assistant",
                "content": WELCOME_MESSAGE,
            }
        ]
        st.rerun()

if user_input:
    send_message(user_input)
    st.rerun()