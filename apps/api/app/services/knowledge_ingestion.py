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
    source_type: str,
    source_label: str,
    source_url: str | None = None,
) -> tuple[KnowledgeItem, int]:
    cleaned_title = " ".join(title.split()).strip()
    cleaned_content = "\n\n".join(
        " ".join(block.split()).strip()
        for block in content.split("\n\n")
        if block.strip()
    ).strip()
    cleaned_source_type = " ".join(source_type.split()).strip().lower()
    cleaned_source_label = " ".join(source_label.split()).strip()
    cleaned_source_url = " ".join(source_url.split()).strip() if source_url else None

    if not cleaned_title or not cleaned_content or not cleaned_source_type or not cleaned_source_label:
        raise ValueError("Knowledge title and content are required.")

    chunks = chunk_text(cleaned_content)

    item = KnowledgeItem(
        company_id=company_id,
        title=cleaned_title,
        source_type=cleaned_source_type,
        source_label=cleaned_source_label,
        source_url=cleaned_source_url,
        chunk_count=len(chunks),
        content=cleaned_content,
    )
    db.add(item)
    db.flush()

    source = build_chunk_source(item.id, cleaned_source_label)

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
