import re


def chunk_text(
    text: str,
    max_chars: int = 1200,
) -> list[str]:
    if not text:
        return []

    chunks: list[str] = []
    current_chunk = ""
    normalized_text = " ".join(text.replace("\n", " ").split())
    sentences = [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", normalized_text)
        if sentence.strip()
    ]

    for sentence in sentences:
        normalized_sentence = sentence if sentence.endswith((".", "!", "?")) else f"{sentence}."

        if not current_chunk:
            current_chunk = normalized_sentence
            continue

        if len(current_chunk) + 1 + len(normalized_sentence) <= max_chars:
            current_chunk = f"{current_chunk} {normalized_sentence}"
            continue

        chunks.append(current_chunk.strip())
        current_chunk = normalized_sentence

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks
