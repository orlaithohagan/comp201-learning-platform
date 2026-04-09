import streamlit as st
from openai import OpenAI
from src.rag_helper import build_context_from_flashcards

MODEL_NAME = "gpt-4o-mini"

SYSTEM_PROMPT = """
You are a helpful AI tutor for a university COMP201 Software Engineering student.

Your job is to:
- explain concepts clearly and simply
- stay accurate and student-friendly
- use the provided course material only when it is clearly relevant
- ignore irrelevant or weakly related course material
- if no strong course material is available, answer using your own general knowledge

When answering:
- respond directly to the student's actual question
- do not drift onto unrelated topics
- keep explanations concise and revision-friendly
- include structure or bullet points when helpful
- when a topic is named explicitly, focus on explaining that topic directly

If the student asks for:
- an example → give a real-world example
- a summary → provide concise revision notes
- clarification → simplify your previous answer

Do not mention raw prompt instructions.
""".strip()


def get_openai_client() -> OpenAI:
    """Create and return an OpenAI client using Streamlit secrets."""
    return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


def ask_ai_tutor(question: str, chat_history: list | None = None) -> tuple[str, list]:
    """Generate an AI tutor response using retrieved course context and recent chat history."""
    try:
        client = get_openai_client()
        context, relevant_cards = build_context_from_flashcards(question)

        context_message = f"""
        Relevant COMP201 course material:
        {context if context else "No strong matching course material was retrieved."}

        Use this material when it is clearly relevant. Ignore it if it does not fit the user's question.
        """.strip()

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": context_message},
        ]

        if chat_history:
            recent_messages = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in chat_history[-3:]
                if msg.get("role") in ["user", "assistant"]
            ]
            messages.extend(recent_messages)

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages
        )

        answer = response.choices[0].message.content
        return answer, relevant_cards

    except Exception as e:
        return f"Error: {str(e)}", []