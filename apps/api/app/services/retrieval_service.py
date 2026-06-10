from dataclasses import dataclass
from math import sqrt
import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.knowledge_chunk import KnowledgeChunk
from app.models.knowledge_item import KnowledgeItem
from app.services.embedding_service import create_embedding
from app.services.source_metadata import parse_knowledge_item_id


@dataclass
class RetrievedChunk:
    chunk: KnowledgeChunk
    item: KnowledgeItem
    keyword_score: int
    semantic_score: float
    combined_score: float


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
    limit: int = 8,
    min_similarity: float = 0.2,
) -> list[RetrievedChunk]:
    query_embedding = create_embedding(query)

    chunk_statement = select(KnowledgeChunk).where(KnowledgeChunk.company_id == company_id)
    knowledge_chunks = list(db.scalars(chunk_statement).all())
    item_statement = select(KnowledgeItem).where(KnowledgeItem.company_id == company_id)
    knowledge_items = {
        item.id: item
        for item in db.scalars(item_statement).all()
    }

    scored_chunks: list[RetrievedChunk] = []

    for chunk in knowledge_chunks:
        item_id = parse_knowledge_item_id(chunk.source)

        if item_id is None:
            continue

        knowledge_item = knowledge_items.get(item_id)

        if knowledge_item is None:
            continue

        keyword_score = keyword_overlap_score(query, chunk.content)
        semantic_score = cosine_similarity(chunk.embedding, query_embedding)
        combined_score = (keyword_score * 0.35) + (semantic_score * 0.65)

        if semantic_score >= min_similarity or keyword_score > 0:
            scored_chunks.append(
                RetrievedChunk(
                    chunk=chunk,
                    item=knowledge_item,
                    keyword_score=keyword_score,
                    semantic_score=semantic_score,
                    combined_score=combined_score,
                )
            )

    scored_chunks.sort(
        key=lambda item: (item.combined_score, item.keyword_score, item.semantic_score),
        reverse=True,
    )

    return scored_chunks[:limit]
