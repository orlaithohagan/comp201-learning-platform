from openai import OpenAI
import os
from src.rag_helper import build_context_from_flashcards

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def ask_ai_tutor(question):
    try:
        context, relevant_cards = build_context_from_flashcards(question)

        system_prompt = """
            You are a helpful AI tutor for a university COMP201 Software Engineering student.

            Your role is to:
            - explain concepts clearly and simply
            - prioritise accuracy over creativity
            - use the provided course material where relevant
            - base your answer on course material if it is available
            - expand slightly with your own knowledge if needed

            When answering:
            - start with a clear definition (if applicable)
            - then explain key points in bullet points
            - include an example if helpful
            - keep explanations concise and revision-friendly

            If the student asks for:
            - "quiz me" → generate a short quiz question
            - "example" → give a real-world example
            - "revision" → summarise key points

            Do NOT mention the course material explicitly in your answer.
            Do NOT say "based on the material above".
            """.strip()

        user_prompt = f"""
                Student question:
                {question}

                Relevant COMP201 course material:
                {context if context else "No direct course material was retrieved."}

                Please answer clearly and in a revision-friendly way.
                """.strip()

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
        )

        answer = response.choices[0].message.content
        return answer, relevant_cards

    except Exception as e:
        return f"Error: {str(e)}", []