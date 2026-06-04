from math import sqrt
import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.knowledge_chunk import KnowledgeChunk
from app.services.embedding_service import create_embedding


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return -1.0

    dot_product = sum(left_value * right_value for left_value, right_value in zip(left, right))
    left_norm = sqrt(sum(value * value for value in left))
    right_norm = sqrt(sum(value * value for value in right))

    if left_norm == 0 or right_norm == 0:
        return -1.0

    return dot_product / (left_norm * right_norm)


def keyword_overlap_score(query: str, content: str) -> int:
    query_words = {
        word
        for word in re.findall(r"\b[a-zA-Z0-9]+\b", query.lower())
        if len(word) >= 3
    }
    content_words = {
        word
        for word in re.findall(r"\b[a-zA-Z0-9]+\b", content.lower())
        if len(word) >= 3
    }

    return len(query_words & content_words)


def retrieve_relevant_chunks(
    db: Session,
    company_id: int,
    query: str,
    limit: int = 3,
    min_similarity: float = 0.2,
) -> list[KnowledgeChunk]:
    query_embedding = create_embedding(query)

    statement = select(KnowledgeChunk).where(KnowledgeChunk.company_id == company_id)
    knowledge_chunks = list(db.scalars(statement).all())

    scored_chunks: list[tuple[int, float, KnowledgeChunk]] = []

    for chunk in knowledge_chunks:
        keyword_score = keyword_overlap_score(query, chunk.content)
        semantic_score = cosine_similarity(chunk.embedding, query_embedding)

        if semantic_score >= min_similarity or keyword_score > 0:
            scored_chunks.append((keyword_score, semantic_score, chunk))

    scored_chunks.sort(
        key=lambda item: (item[0], item[1]),
        reverse=True,
    )

    return [chunk for _, _, chunk in scored_chunks[:limit]]
