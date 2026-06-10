import re

from app.models.knowledge_item import KnowledgeItem
from app.services.text_chunker import normalize_paragraphs


def extract_keywords(text: str) -> set[str]:
    stop_words = {
        "what",
        "who",
        "where",
        "when",
        "why",
        "how",
        "is",
        "are",
        "the",
        "his",
        "her",
        "their",
        "about",
        "tell",
        "me",
        "and",
        "or",
        "to",
        "of",
        "in",
        "for",
        "a",
        "an",
    }

    words = re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())

    return {
        word
        for word in words
        if len(word) >= 3 and word not in stop_words
    }


def paragraph_relevance_score(question_keywords: set[str], paragraph: str) -> int:
    paragraph_keywords = extract_keywords(paragraph)

    return len(question_keywords & paragraph_keywords)


def build_document_context(
    question: str,
    knowledge_item: KnowledgeItem,
    max_paragraphs: int = 4,
) -> str:
    paragraphs = normalize_paragraphs(knowledge_item.content)

    if not paragraphs:
        return knowledge_item.content

    question_keywords = extract_keywords(question)

    if not question_keywords:
        return "\n\n".join(paragraphs[:max_paragraphs])

    scored_paragraphs = [
        (paragraph_relevance_score(question_keywords, paragraph), index, paragraph)
        for index, paragraph in enumerate(paragraphs)
    ]

    matching_paragraphs = [
        (score, index, paragraph)
        for score, index, paragraph in scored_paragraphs
        if score > 0
    ]

    if not matching_paragraphs:
        return "\n\n".join(paragraphs[:max_paragraphs])

    matching_paragraphs.sort(key=lambda item: (item[0], -item[1]), reverse=True)
    selected_indices = sorted(
        {
            index
            for _, index, _ in matching_paragraphs[:max_paragraphs]
        }
    )

    context_paragraphs: list[str] = []

    for index in selected_indices:
        start_index = max(0, index - 1)
        end_index = min(len(paragraphs), index + 2)

        for paragraph in paragraphs[start_index:end_index]:
            if paragraph not in context_paragraphs:
                context_paragraphs.append(paragraph)

            if len(context_paragraphs) >= max_paragraphs:
                break

        if len(context_paragraphs) >= max_paragraphs:
            break

    return "\n\n".join(context_paragraphs[:max_paragraphs])
