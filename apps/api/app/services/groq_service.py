import httpx
from groq import Groq

from app.core.config import settings
from app.services.answer_service import dedupe_chunks

MAX_GROQ_CONTEXT_CHUNKS = 2
MAX_GROQ_CHARS_PER_CHUNK = 900


def generate_answer_with_groq(
    question: str,
    context_chunks: list[str],
) -> str | None:
    if not settings.groq_api_key:
        return None

    cleaned_chunks = dedupe_chunks(context_chunks)
    trimmed_chunks = [
        chunk[:MAX_GROQ_CHARS_PER_CHUNK]
        for chunk in cleaned_chunks[:MAX_GROQ_CONTEXT_CHUNKS]
    ]

    if not trimmed_chunks:
        return None

    context = "\n\n".join(trimmed_chunks)

    prompt = f"""
You are a professional customer support AI assistant.

Answer the user's question using ONLY the context below.

Rules:
- Be concise
- Be conversational
- Sound like a helpful support agent
- Answer like a real human assistant, not like copied website text
- Rewrite and summarize the information naturally
- If information is missing, politely say so
- Do not invent information
- Keep the answer to 2 to 4 sentences when possible

Context:
{context}

User question:
{question}
"""

    try:
        with httpx.Client(trust_env=False, timeout=30.0) as http_client:
            client = Groq(
                api_key=settings.groq_api_key,
                http_client=http_client,
            )

            completion = client.chat.completions.create(
                model=settings.groq_model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful customer support assistant.",
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                temperature=0.3,
                max_tokens=200,
            )

            message_content = completion.choices[0].message.content
            return message_content.strip() if message_content else None
    except Exception:
        return None
