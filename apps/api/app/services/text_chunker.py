import re


def normalize_paragraphs(text: str) -> list[str]:
    paragraphs = [
        " ".join(block.split()).strip()
        for block in re.split(r"\n\s*\n+", text)
    ]

    return [paragraph for paragraph in paragraphs if paragraph]


def split_long_sentence(text: str, max_chars: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]

    clauses = re.split(r"(?<=[,;:])\s+", text)
    chunks: list[str] = []
    current_chunk = ""

    for clause in clauses:
        normalized_clause = clause.strip()

        if not normalized_clause:
            continue

        if not current_chunk:
            current_chunk = normalized_clause
            continue

        if len(current_chunk) + 1 + len(normalized_clause) <= max_chars:
            current_chunk = f"{current_chunk} {normalized_clause}"
            continue

        chunks.append(current_chunk.strip())
        current_chunk = normalized_clause

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks or [text[:max_chars].strip()]


def chunk_text(
    text: str,
    max_chars: int = 1200,
    overlap_chars: int = 180,
) -> list[str]:
    if not text:
        return []

    chunks: list[str] = []
    current_chunk = ""
    paragraphs = normalize_paragraphs(text)
    sentences: list[str] = []

    for paragraph in paragraphs:
        paragraph_sentences = [
            sentence.strip()
            for sentence in re.split(r"(?<=[.!?])\s+", paragraph)
            if sentence.strip()
        ]

        for sentence in paragraph_sentences or [paragraph]:
            sentences.extend(split_long_sentence(sentence, max_chars))

    for sentence in sentences:
        normalized_sentence = sentence if sentence.endswith((".", "!", "?")) else f"{sentence}."

        if not current_chunk:
            current_chunk = normalized_sentence
            continue

        if len(current_chunk) + 1 + len(normalized_sentence) <= max_chars:
            current_chunk = f"{current_chunk} {normalized_sentence}"
            continue

        chunks.append(current_chunk.strip())
        overlap = current_chunk[-overlap_chars:].strip()
        current_chunk = (
            f"{overlap} {normalized_sentence}".strip()
            if overlap
            else normalized_sentence
        )

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks
