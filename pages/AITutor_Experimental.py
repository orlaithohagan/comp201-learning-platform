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
st.caption("⚡ Powered by OpenAI API with contextual prompting (topic-aware tutoring)")

if st.button("Clear Chat"):
    st.session_state.ai_tutor_messages = []
    st.rerun()

TOPICS = [
    "Requirements Engineering",
    "Software Processes",
    "System Modelling and UML",
    "Architectural Design",
    "Object-Oriented Design",
    "Petri Nets",
    "Testing",
]

topic = st.selectbox("Choose a topic", TOPICS)
st.caption("Try asking for an explanation, an example, a revision summary, or a practice question.")

# Initialise chat history
if "ai_tutor_messages" not in st.session_state:
    st.session_state.ai_tutor_messages = [
        {
            "role": "assistant",
            "content": (
                f"Hi! I'm your COMP201 AI tutor. "
                f"You are currently studying **{topic}**. "
                f"Ask me anything about this topic."
            ),
        }
    ]

def build_prompt(topic: str, user_message: str) -> str:
    return f"""
You are helping a COMP201 Software Engineering student.

Topic: {topic}

Student request:
{user_message}

Please answer clearly, accurately, and in a student-friendly way.
Use short explanations, examples, and revision-friendly wording where helpful.
""".strip()

def send_message(user_message: str):
    prompt = build_prompt(topic, user_message)

    st.session_state.ai_tutor_messages.append(
        {"role": "user", "content": user_message}
    )

    # with st.spinner("Generating response..."):
    #     answer = ask_ai_tutor(prompt)

    # st.session_state.ai_tutor_messages.append(
    #     {"role": "assistant", "content": answer}
    # )

    with st.spinner("Thinking..."):
        answer = ask_ai_tutor(prompt)

    st.session_state.ai_tutor_messages.append(
        {"role": "assistant", "content": answer}
    )

# Reset intro message if topic changes
if st.session_state.get("ai_tutor_last_topic") != topic:
    st.session_state.ai_tutor_last_topic = topic
    st.session_state.ai_tutor_messages = [
        {
            "role": "assistant",
            "content": (
                f"You're now exploring **{topic}**. "
                f"Ask me anything about this topic and I'll help explain it clearly."
            ),
        }
    ]


# Display chat history
for message in st.session_state.ai_tutor_messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            st.markdown(f"🤖 {message['content']}")
        else:
            st.markdown(f"🧑 {message['content']}")

# Chat input
user_input = st.chat_input(f"Ask a question about {topic}...")

if user_input:
    send_message(user_input)
    st.rerun()
