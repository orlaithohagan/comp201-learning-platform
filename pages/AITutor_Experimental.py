import streamlit as st
from src.services.auth_ui import require_login, logout_button
from src.ai_tutor import ask_ai_tutor

require_login()
logout_button()

st.set_page_config(page_title="AI Tutor Experimental", page_icon="🤖", layout="wide")

st.title("AI Tutor")
st.markdown(
    "This is an experimental built-in AI tutor for COMP201 topics. "
    "Your original Custom GPT tutor is still available as a fallback."
)
st.caption("⚡ Powered by OpenAI API with retrieval from COMP201 course materials")


# Initialise chat history
if "ai_tutor_messages" not in st.session_state:
    st.session_state.ai_tutor_messages = [
        {
            "role": "assistant",
            "content": (
                f"Hi! I'm your COMP201 AI tutor. "
                f"Ask me anything about software engineering concepts, and I'll do my best to explain them clearly. "
            ),
        }
    ]

def send_message(user_message: str):
    st.session_state.ai_tutor_messages.append(
        {"role": "user", "content": user_message}
    )

    with st.spinner("Thinking..."):
        answer, relevant_cards = ask_ai_tutor(user_message)

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
            st.markdown(f"🤖 {message['content']}")

            if i == len(st.session_state.ai_tutor_messages) - 1:
                st.caption("💡 Try asking: 'quiz me on this', 'give an example', or 'summarise this topic'")

            sources = message.get("sources", [])
            if sources:
                with st.expander("View course context used"):
                    for j, card in enumerate(sources, start=1):
                        st.markdown(f"**{j}. {card['topic']}**")
                        st.markdown(f"> **Q:** {card['prompt']}")
                        st.markdown(f"> **A:** {card['answer']}")
                        st.markdown("---")

        else:
            st.markdown(f"🧑 {message['content']}")


col1, col2 = st.columns([6, 1])

with col1:
    user_input = st.chat_input(f"Ask a question about COMP201 software engineering....")

with col2:
    if st.button("🗑️", help="Clear chat"):
        st.session_state.ai_tutor_messages = []
        st.rerun()

if user_input:
    send_message(user_input)
    st.rerun()