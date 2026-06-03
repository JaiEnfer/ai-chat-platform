def chunk_text(
    text: str,
    max_chars: int = 1200,
) -> list[str]:
    if not text:
        return []

    chunks: list[str] = []

    start = 0

    while start < len(text):
        end = start + max_chars
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start = end

    return chunks