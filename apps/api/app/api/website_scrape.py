from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.company import Company
from app.models.knowledge_item import KnowledgeItem
from app.schemas.website_scrape import WebsiteScrapeRequest, WebsiteScrapeResponse
from app.services.text_chunker import chunk_text
from app.services.website_scraper import scrape_website_text

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
        text = scrape_website_text(str(scrape_data.url))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not scrape website: {exc}",
        ) from exc

    chunks = chunk_text(text)

    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No readable website content found",
        )

    for index, chunk in enumerate(chunks, start=1):
        item = KnowledgeItem(
            company_id=company_id,
            title=f"Website Content {index}",
            content=chunk,
        )
        db.add(item)

    db.commit()

    return WebsiteScrapeResponse(
        company_id=company_id,
        source_url=str(scrape_data.url),
        chunks_created=len(chunks),
    )