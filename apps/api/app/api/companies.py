from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import delete, select

from app.db.session import get_db
from app.models.company import Company
from app.models.conversation_message import ConversationMessage
from app.models.knowledge_chunk import KnowledgeChunk
from app.models.knowledge_item import KnowledgeItem
from app.models.lead import Lead
from app.schemas.company import CompanyCreate, CompanyRead

router = APIRouter()


@router.post(
    "/companies",
    response_model=CompanyRead,
    status_code=status.HTTP_201_CREATED,
)
def create_company(
    company_data: CompanyCreate,
    db: Session = Depends(get_db),
) -> Company:
    company = Company(
        owner_user_id=company_data.owner_user_id.strip(),
        name=company_data.name.strip(),
        website=str(company_data.website),
    )

    db.add(company)
    db.commit()
    db.refresh(company)

    return company


@router.get(
    "/companies/{company_id}",
    response_model=CompanyRead,
)
def get_company(
    company_id: int,
    db: Session = Depends(get_db),
) -> Company:
    company = db.get(Company, company_id)

    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )

    return company

@router.get(
    "/users/{owner_user_id}/company",
    response_model=CompanyRead,
)
def get_company_by_owner(
    owner_user_id: str,
    db: Session = Depends(get_db),
) -> Company:
    statement = select(Company).where(
        Company.owner_user_id == owner_user_id,
    )

    company = db.scalars(statement).first()

    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )

    return company


@router.delete("/companies/{company_id}")
def delete_company(
    company_id: int,
    db: Session = Depends(get_db),
) -> dict[str, int | bool]:
    company = db.get(Company, company_id)

    if company is None:
        return {
            "deleted_company_id": company_id,
            "deleted_leads": 0,
            "deleted_conversations": 0,
            "deleted_knowledge_chunks": 0,
            "deleted_knowledge_items": 0,
            "already_deleted": True,
        }

    deleted_conversations = db.execute(
        delete(ConversationMessage).where(
            ConversationMessage.company_id == company_id
        )
    ).rowcount or 0
    deleted_leads = db.execute(
        delete(Lead).where(Lead.company_id == company_id)
    ).rowcount or 0
    deleted_chunks = db.execute(
        delete(KnowledgeChunk).where(KnowledgeChunk.company_id == company_id)
    ).rowcount or 0
    deleted_knowledge_items = db.execute(
        delete(KnowledgeItem).where(KnowledgeItem.company_id == company_id)
    ).rowcount or 0

    db.delete(company)
    db.commit()

    return {
        "deleted_company_id": company_id,
        "deleted_leads": deleted_leads,
        "deleted_conversations": deleted_conversations,
        "deleted_knowledge_chunks": deleted_chunks,
        "deleted_knowledge_items": deleted_knowledge_items,
        "already_deleted": False,
    }
