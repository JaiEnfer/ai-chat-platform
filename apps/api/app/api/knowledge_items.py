from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.company import Company
from app.models.knowledge_item import KnowledgeItem
from app.schemas.knowledge_item import (
    KnowledgeHtmlCreate,
    KnowledgeImportResponse,
    KnowledgeItemCreate,
    KnowledgeItemRead,
)
from app.services.document_parser import html_to_text, parse_uploaded_document
from app.services.knowledge_ingestion import (
    delete_knowledge_item_chunks,
    ingest_knowledge_text,
)

router = APIRouter()


@router.post(
    "/knowledge-items",
    response_model=KnowledgeItemRead,
    status_code=status.HTTP_201_CREATED,
)
def create_knowledge_item(
    item_data: KnowledgeItemCreate,
    db: Session = Depends(get_db),
) -> KnowledgeItem:
    company = db.get(Company, item_data.company_id)

    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )

    item, _ = ingest_knowledge_text(
        db=db,
        company_id=item_data.company_id,
        title=item_data.title,
        content=item_data.content,
        source_label=f"manual:{item_data.title}",
    )
    db.commit()
    db.refresh(item)

    return item


@router.post(
    "/companies/{company_id}/knowledge-html",
    response_model=KnowledgeImportResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_knowledge_from_html(
    company_id: int,
    item_data: KnowledgeHtmlCreate,
    db: Session = Depends(get_db),
) -> KnowledgeImportResponse:
    company = db.get(Company, company_id)

    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )

    extracted_text = html_to_text(item_data.html_content)

    if not extracted_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="HTML content did not contain readable text.",
        )

    item, chunk_count = ingest_knowledge_text(
        db=db,
        company_id=company_id,
        title=item_data.title,
        content=extracted_text,
        source_label=item_data.source_label or f"html:{item_data.title}",
    )
    db.commit()

    return KnowledgeImportResponse(
        company_id=company_id,
        title=item.title,
        source=item_data.source_label or "html",
        chunks_created=chunk_count,
    )


@router.post(
    "/companies/{company_id}/knowledge-files",
    response_model=KnowledgeImportResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_knowledge_from_file(
    company_id: int,
    title: str | None = Form(default=None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> KnowledgeImportResponse:
    company = db.get(Company, company_id)

    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )

    file_name = file.filename or "uploaded-file"
    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file was empty.",
        )

    try:
        extracted_text = parse_uploaded_document(file_name, file_bytes)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not parse uploaded file: {exc}",
        ) from exc

    if not extracted_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file did not contain readable text.",
        )

    resolved_title = (title or Path(file_name).stem or "Uploaded document").strip()
    item, chunk_count = ingest_knowledge_text(
        db=db,
        company_id=company_id,
        title=resolved_title,
        content=extracted_text,
        source_label=f"file:{file_name}",
    )
    db.commit()

    return KnowledgeImportResponse(
        company_id=company_id,
        title=item.title,
        source=file_name,
        chunks_created=chunk_count,
    )


@router.get(
    "/companies/{company_id}/knowledge-items",
    response_model=list[KnowledgeItemRead],
)
def list_company_knowledge_items(
    company_id: int,
    db: Session = Depends(get_db),
) -> list[KnowledgeItem]:
    statement = select(KnowledgeItem).where(
        KnowledgeItem.company_id == company_id,
    )

    items = db.scalars(statement).all()

    return list(items)

@router.delete(
    "/knowledge-items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_knowledge_item(
    item_id: int,
    db: Session = Depends(get_db),
) -> None:
    item = db.get(KnowledgeItem, item_id)

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge item not found",
        )

    delete_knowledge_item_chunks(db, item.id)
    db.delete(item)
    db.commit()
