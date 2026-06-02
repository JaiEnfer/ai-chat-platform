from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.company import Company
from app.models.conversation_message import ConversationMessage
from app.models.knowledge_item import KnowledgeItem
from app.models.lead import Lead
from app.schemas.analytics import CompanyAnalyticsRead

router = APIRouter()


@router.get(
    "/companies/{company_id}/analytics",
    response_model=CompanyAnalyticsRead,
)
def get_company_analytics(
    company_id: int,
    db: Session = Depends(get_db),
) -> CompanyAnalyticsRead:
    company = db.get(Company, company_id)

    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )

    total_leads = db.scalar(
        select(func.count()).select_from(Lead).where(Lead.company_id == company_id)
    )

    total_conversation_messages = db.scalar(
        select(func.count())
        .select_from(ConversationMessage)
        .where(ConversationMessage.company_id == company_id)
    )

    total_lead_requests = db.scalar(
        select(func.count())
        .select_from(ConversationMessage)
        .where(ConversationMessage.company_id == company_id)
        .where(ConversationMessage.should_collect_lead.is_(True))
    )

    total_knowledge_items = db.scalar(
        select(func.count())
        .select_from(KnowledgeItem)
        .where(KnowledgeItem.company_id == company_id)
    )

    return CompanyAnalyticsRead(
        company_id=company_id,
        total_leads=total_leads or 0,
        total_conversation_messages=total_conversation_messages or 0,
        total_lead_requests=total_lead_requests or 0,
        total_knowledge_items=total_knowledge_items or 0,
    )