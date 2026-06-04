from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.models.knowledge_chunk import KnowledgeChunk
from app.models.knowledge_item import KnowledgeItem
from app.services.embedding_service import create_embedding
from app.services.text_chunker import chunk_text


def build_chunk_source(item_id: int, source_label: str) -> str:
    return f"knowledge-item:{item_id}:{source_label[:300]}"


def ingest_knowledge_text(
    db: Session,
    company_id: int,
    title: str,
    content: str,
    source_label: str,
) -> tuple[KnowledgeItem, int]:
    cleaned_title = " ".join(title.split()).strip()
    cleaned_content = " ".join(content.split()).strip()

    if not cleaned_title or not cleaned_content:
        raise ValueError("Knowledge title and content are required.")

    item = KnowledgeItem(
        company_id=company_id,
        title=cleaned_title,
        content=cleaned_content,
    )
    db.add(item)
    db.flush()

    chunks = chunk_text(cleaned_content)
    source = build_chunk_source(item.id, source_label)

    for chunk in chunks:
        db.add(
            KnowledgeChunk(
                company_id=company_id,
                source=source,
                content=chunk,
                embedding=create_embedding(chunk),
            )
        )

    return item, len(chunks)


def delete_knowledge_item_chunks(db: Session, item_id: int) -> None:
    db.execute(
        delete(KnowledgeChunk).where(
            KnowledgeChunk.source.like(f"knowledge-item:{item_id}:%"),
        )
    )
