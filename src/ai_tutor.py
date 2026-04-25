"""
AI tutor service for generating contextual responses to COMP201 questions.

Provides functions to query OpenAI with retrieval-augmented generation (RAG)
using course flashcards as context for personalised, accurate explanations.
"""

import streamlit as st
from openai import OpenAI
from src.rag_helper import build_context_from_flashcards

MODEL_NAME = "gpt-4o-mini"

SYSTEM_PROMPT = """
    You are a helpful AI tutor for a university COMP201 Software Engineering student.

    Your job is to:
    - explain software engineering concepts clearly and simply
    - stay accurate and student-friendly
    - use the provided course material when it is relevant
    - focus only on COMP201 and closely related software engineering topics
    - avoid generating harmful or inappropriate responses

    If the user asks a question unrelated to software engineering or COMP201:
    - politely explain that you are specifically for software engineering revision
    - ask them to submit a relevant module-related question

    When answering:
    - respond directly to the student's actual question
    - do not drift onto unrelated topics
    - keep explanations concise and revision-friendly
    - include structure when helpful

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

        # Reject unrelated questions early
        if not relevant_cards:
            return (
                "I am specifically designed to support COMP201 Software Engineering revision. "
                "Please ask a question related to Software Engineering concepts or course topics.",
                []
            )

        context_message = f"""
        Relevant COMP201 course material:
        {context}

        Use this material when it is clearly relevant to the user's question.
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

        messages.append({"role": "user", "content": question})

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages
        )

        answer = response.choices[0].message.content
        return answer, relevant_cards

    except Exception as e:
        return f"Error: {str(e)}", []