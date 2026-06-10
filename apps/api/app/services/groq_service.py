import httpx
from groq import Groq

from app.core.config import settings
from app.services.answer_service import dedupe_chunks

MAX_GROQ_CONTEXT_CHUNKS = 4
MAX_GROQ_CHARS_PER_CHUNK = 1600


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
- Read the provided document and website context carefully before answering
- Prefer the uploaded file or PDF content when it directly answers the question
- Be conversational and sound natural, like a helpful human assistant
- Summarize clearly instead of copying raw text
- If the answer depends on several parts of the document, combine them into one clear answer
- If the context does not clearly answer the question, say that you are not fully sure based on the available information
- Do not invent information
- Do not mention facts that are not present in the context
- Keep the answer to 2 to 5 sentences when possible

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
                        "content": (
                            "You are a helpful customer support assistant who answers "
                            "using uploaded business documents and website knowledge."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                temperature=0.2,
                max_tokens=260,
            )

            message_content = completion.choices[0].message.content
            return message_content.strip() if message_content else None
    except Exception:
        return None
