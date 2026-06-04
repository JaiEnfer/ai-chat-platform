import re

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.company import Company
from app.models.conversation_message import ConversationMessage
from app.models.knowledge_item import KnowledgeItem
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.retrieval_service import retrieve_relevant_chunks

router = APIRouter()

MIN_KEYWORD_LENGTH = 4


def extract_keywords(text: str) -> set[str]:
    words = re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())

    return {
        word
        for word in words
        if len(word) >= MIN_KEYWORD_LENGTH
    }


def build_chat_response(
    message: str,
    knowledge_items: list[KnowledgeItem],
) -> ChatResponse:
    if not knowledge_items:
        return ChatResponse(
            answer=(
                "I don't have enough company information yet. "
                "Please leave your contact details and the team will get back to you."
            ),
            should_collect_lead=True,
        )

    user_keywords = extract_keywords(message)

    for item in knowledge_items:
        title_keywords = extract_keywords(item.title)
        content_keywords = extract_keywords(item.content)

        knowledge_keywords = title_keywords | content_keywords

        if user_keywords & knowledge_keywords:
            lead_intent_keywords = {
                "appointment",
                "booking",
                "book",
                "contact",
                "call",
                "consultation",
                "schedule",
            }

            should_collect_lead = bool(user_keywords & lead_intent_keywords)

            return ChatResponse(
                answer=item.content,
                should_collect_lead=should_collect_lead,
            )

    return ChatResponse(
        answer=(
            "I could not find an exact answer. "
            "Please leave your name and email, and the team will contact you."
        ),
        should_collect_lead=True,
    )


@router.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(
    chat_request: ChatRequest,
    db: Session = Depends(get_db),
) -> ChatResponse:
    statement = select(Company).where(
        Company.widget_key == chat_request.widget_key,
    )

    company = db.scalars(statement).first()
    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )

    relevant_chunks = retrieve_relevant_chunks(
        db=db,
        company_id=company.id,
        query=chat_request.message,
    )

    if relevant_chunks:
        best_chunk = relevant_chunks[0]

        response = ChatResponse(
            answer=best_chunk.content,
            should_collect_lead=any(
                keyword in chat_request.message.lower()
                for keyword in [
                    "appointment",
                    "booking",
                    "book",
                    "contact",
                    "call",
                    "consultation",
                    "schedule",
                ]
            ),
        )
    else:
        statement = select(KnowledgeItem).where(
            KnowledgeItem.company_id == company.id,
        )

        knowledge_items = list(db.scalars(statement).all())

        response = build_chat_response(
            message=chat_request.message,
            knowledge_items=knowledge_items,
        )

    conversation_message = ConversationMessage(
        company_id=company.id,
        visitor_id=chat_request.visitor_id.strip(),
        user_message=chat_request.message.strip(),
        bot_answer=response.answer,
        should_collect_lead=response.should_collect_lead,
    )

    db.add(conversation_message)
    db.commit()

    return response