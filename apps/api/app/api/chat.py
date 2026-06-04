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
from app.services.answer_service import (
    build_extractive_answer,
    build_natural_fallback_answer,
)
from app.services.groq_service import generate_answer_with_groq

router = APIRouter()

MIN_KEYWORD_LENGTH = 4
LEAD_INTENT_KEYWORDS = {
    "appointment",
    "booking",
    "book",
    "contact",
    "call",
    "consultation",
    "schedule",
}


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
            should_collect_lead = bool(user_keywords & LEAD_INTENT_KEYWORDS)

            return ChatResponse(
                answer=build_natural_fallback_answer([item.content], max_sentences=2),
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
    normalized_message = chat_request.message.strip()
    normalized_visitor_id = chat_request.visitor_id.strip()

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
        query=normalized_message,
    )

    if relevant_chunks:
        context_chunks = [chunk.content for chunk in relevant_chunks]

        answer = generate_answer_with_groq(
            question=normalized_message,
            context_chunks=context_chunks,
        )

        if not answer:
            answer = build_extractive_answer(
                question=normalized_message,
                context_chunks=context_chunks,
            )

        response = ChatResponse(
            answer=answer,
            should_collect_lead=any(
                keyword in normalized_message.lower()
                for keyword in LEAD_INTENT_KEYWORDS
            ),
        )
    else:
        statement = select(KnowledgeItem).where(
            KnowledgeItem.company_id == company.id,
        )

        knowledge_items = list(db.scalars(statement).all())

        response = build_chat_response(
            message=normalized_message,
            knowledge_items=knowledge_items,
        )

    conversation_message = ConversationMessage(
        company_id=company.id,
        visitor_id=normalized_visitor_id,
        user_message=normalized_message,
        bot_answer=response.answer,
        should_collect_lead=response.should_collect_lead,
    )

    db.add(conversation_message)
    db.commit()

    return response
