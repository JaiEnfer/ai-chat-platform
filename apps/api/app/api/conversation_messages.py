from fastapi import APIRouter, Depends
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.conversation_message import ConversationMessage
from app.schemas.conversation_message import ConversationMessageRead

router = APIRouter()


@router.get(
    "/companies/{company_id}/conversation-messages",
    response_model=list[ConversationMessageRead],
)
def list_company_conversation_messages(
    company_id: int,
    db: Session = Depends(get_db),
) -> list[ConversationMessage]:
    statement = (
        select(ConversationMessage)
        .where(ConversationMessage.company_id == company_id)
        .order_by(ConversationMessage.id.desc())
    )

    messages = db.scalars(statement).all()

    return list(messages)


@router.get(
    "/companies/{company_id}/visitors/{visitor_id}/conversation-messages",
    response_model=list[ConversationMessageRead],
)
def list_visitor_conversation_messages(
    company_id: int,
    visitor_id: str,
    db: Session = Depends(get_db),
) -> list[ConversationMessage]:
    statement = (
        select(ConversationMessage)
        .where(ConversationMessage.company_id == company_id)
        .where(ConversationMessage.visitor_id == visitor_id)
        .order_by(ConversationMessage.id.asc())
    )

    messages = db.scalars(statement).all()

    return list(messages)


@router.delete("/companies/{company_id}/conversation-messages")
def clear_company_conversation_messages(
    company_id: int,
    db: Session = Depends(get_db),
) -> dict[str, int]:
    result = db.execute(
        delete(ConversationMessage).where(
            ConversationMessage.company_id == company_id
        )
    )
    db.commit()

    return {"deleted_count": result.rowcount or 0}
