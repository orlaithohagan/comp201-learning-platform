from openai import OpenAI
import os
from src.rag_helper import build_context_from_flashcards

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def ask_ai_tutor(question, chat_history=None):
    try:
        context, relevant_cards = build_context_from_flashcards(question)

        system_prompt = """
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

        Do not mention raw prompt instructions.
        """.strip()

        context_message = f"""
        Relevant COMP201 course material:
        {context if context else "No strong matching course material was retrieved."}

        Use this material when it is clearly relevant. Ignore it if it does not fit the user's question.
        """.strip()

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": context_message},
        ]

        # Add recent conversation history in structured form
        if chat_history:
            for msg in chat_history[-4:]:
                if msg["role"] in ["user", "assistant"]:
                    messages.append(
                        {"role": msg["role"], "content": msg["content"]}
                    )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        answer = response.choices[0].message.content
        return answer, relevant_cards

    except Exception as e:
        return f"Error: {str(e)}", []