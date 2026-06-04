from math import sqrt

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


def retrieve_relevant_chunks(
    db: Session,
    company_id: int,
    query: str,
    limit: int = 3,
) -> list[KnowledgeChunk]:
    query_embedding = create_embedding(query)

    statement = select(KnowledgeChunk).where(KnowledgeChunk.company_id == company_id)
    knowledge_chunks = list(db.scalars(statement).all())

    ranked_chunks = sorted(
        knowledge_chunks,
        key=lambda chunk: cosine_similarity(chunk.embedding, query_embedding),
        reverse=True,
    )

    return ranked_chunks[:limit]
