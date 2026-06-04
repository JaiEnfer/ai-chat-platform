from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.company import Company
from app.models.knowledge_chunk import KnowledgeChunk
from app.models.knowledge_item import KnowledgeItem
from app.schemas.website_scrape import WebsiteScrapeRequest, WebsiteScrapeResponse
from app.services.knowledge_ingestion import (
    delete_knowledge_item_chunks,
    ingest_knowledge_text,
)
from app.services.website_scraper import scrape_website_pages

router = APIRouter()


@router.post(
    "/companies/{company_id}/scrape-website",
    response_model=WebsiteScrapeResponse,
)
def scrape_company_website(
    company_id: int,
    scrape_data: WebsiteScrapeRequest,
    db: Session = Depends(get_db),
) -> WebsiteScrapeResponse:
    company = db.get(Company, company_id)

    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )

    try:
        scraped_pages = scrape_website_pages(str(scrape_data.url))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not scrape website: {exc}",
        ) from exc

    if not scraped_pages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No readable website content found",
        )

    existing_items = list(
        db.query(KnowledgeItem)
        .filter(
            KnowledgeItem.company_id == company_id,
            KnowledgeItem.title.like("Website:%"),
        )
        .all()
    )

    for item in existing_items:
        delete_knowledge_item_chunks(db, item.id)
        db.delete(item)

    db.execute(
        delete(KnowledgeChunk).where(
            KnowledgeChunk.company_id == company_id,
            KnowledgeChunk.source.like("website:%"),
        )
    )

    total_chunks_created = 0

    for page_url, page_title, page_text in scraped_pages:
        _, chunk_count = ingest_knowledge_text(
            db=db,
            company_id=company_id,
            title=f"Website: {page_title[:120]}",
            content=page_text,
            source_label=f"website:{page_url}",
        )
        total_chunks_created += chunk_count

    db.commit()

    return WebsiteScrapeResponse(
        company_id=company_id,
        source_url=str(scrape_data.url),
        chunks_created=total_chunks_created,
    )
