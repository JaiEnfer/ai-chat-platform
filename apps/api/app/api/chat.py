import re

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.company import Company
from app.models.conversation_message import ConversationMessage
from app.models.knowledge_item import KnowledgeItem
from app.schemas.chat import ChatRequest, ChatResponse, ChatSource
from app.services.answer_service import (
    answer_support_score,
    build_extractive_answer,
    build_natural_fallback_answer,
)
from app.services.groq_service import generate_answer_with_groq
from app.services.context_builder import build_document_context
from app.services.retrieval_service import RetrievedChunk, retrieve_relevant_chunks
from app.services.source_metadata import build_source_label, build_source_snippet

router = APIRouter()

MIN_KEYWORD_LENGTH = 3
LEAD_INTENT_KEYWORDS = {
    "appointment",
    "booking",
    "book",
    "contact",
    "call",
    "consultation",
    "schedule",
    "job",
    "jobs",
    "career",
    "careers",
    "opening",
    "openings",
    "hiring",
    "vacancy",
    "vacancies",
}


def extract_keywords(text: str) -> set[str]:
    words = re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())

    return {
        word
        for word in words
        if len(word) >= MIN_KEYWORD_LENGTH
    }


def build_sources(retrieved_chunks: list[RetrievedChunk]) -> list[ChatSource]:
    unique_sources: list[ChatSource] = []
    seen_items: set[int] = set()

    for retrieved_chunk in retrieved_chunks:
        if retrieved_chunk.item.id in seen_items:
            continue

        seen_items.add(retrieved_chunk.item.id)
        unique_sources.append(
            ChatSource(
                title=retrieved_chunk.item.title,
                source_type=retrieved_chunk.item.source_type,
                source_label=build_source_label(retrieved_chunk.item),
                source_url=retrieved_chunk.item.source_url,
                snippet=build_source_snippet(retrieved_chunk.chunk.content),
            )
        )

    return unique_sources


def build_groq_context(
    question: str,
    retrieved_chunks: list[RetrievedChunk],
) -> list[str]:
    grouped_chunks: dict[int, list[RetrievedChunk]] = {}

    for retrieved_chunk in retrieved_chunks:
        grouped_chunks.setdefault(retrieved_chunk.item.id, []).append(retrieved_chunk)

    formatted_context: list[str] = []

    for item_chunks in grouped_chunks.values():
        primary_chunk = item_chunks[0]
        if primary_chunk.item.source_type == "file":
            merged_content = build_document_context(
                question=question,
                knowledge_item=primary_chunk.item,
                max_paragraphs=5,
            )
        else:
            max_chunks_for_item = 3 if primary_chunk.item.source_type == "website" else 2
            selected_chunks = item_chunks[:max_chunks_for_item]
            merged_content = "\n\n".join(chunk.chunk.content for chunk in selected_chunks)

        formatted_context.append(
            (
                f"Source title: {primary_chunk.item.title}\n"
                f"Source type: {primary_chunk.item.source_type}\n"
                f"Source label: {build_source_label(primary_chunk.item)}\n"
                f"Content:\n{merged_content}"
            )
        )

    return formatted_context


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
            answer_status="needs_more_knowledge",
        )

    user_keywords = extract_keywords(message)

    normalized_message = " ".join(message.lower().split())

    for item in knowledge_items:
        title_keywords = extract_keywords(item.title)
        content_keywords = extract_keywords(item.content)

        knowledge_keywords = title_keywords | content_keywords
        title_text = " ".join(item.title.lower().split())
        content_text = " ".join(item.content.lower().split())
        direct_phrase_match = (
            normalized_message in title_text
            or normalized_message in content_text
            or any(
                keyword in title_text or keyword in content_text
                for keyword in user_keywords
            )
        )

        if (user_keywords & knowledge_keywords) or direct_phrase_match:
            should_collect_lead = bool(user_keywords & LEAD_INTENT_KEYWORDS)

            return ChatResponse(
                answer=build_natural_fallback_answer([item.content], max_sentences=2),
                should_collect_lead=should_collect_lead,
                answer_status="fallback",
                sources=[
                    ChatSource(
                        title=item.title,
                        source_type=item.source_type,
                        source_label=build_source_label(item),
                        source_url=item.source_url,
                        snippet=build_source_snippet(item.content),
                    )
                ],
            )

    return ChatResponse(
        answer=(
            "I could not find an exact answer in the uploaded knowledge. "
            "Please leave your name and email, and the team will contact you."
        ),
        should_collect_lead=True,
        answer_status="no_match",
    )


def should_collect_lead_for_message(message: str, answer_status: str) -> bool:
    normalized_message = message.lower()

    if answer_status in {"needs_more_knowledge", "no_match"}:
        return True

    return any(
        keyword in normalized_message
        for keyword in LEAD_INTENT_KEYWORDS
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
        context_chunks = [retrieved.chunk.content for retrieved in relevant_chunks]
        formatted_context = build_groq_context(normalized_message, relevant_chunks)

        answer = generate_answer_with_groq(
            question=normalized_message,
            context_chunks=formatted_context,
        )

        if not answer or answer_support_score(answer, context_chunks) < 2:
            answer = build_extractive_answer(
                question=normalized_message,
                context_chunks=context_chunks,
            )

        response = ChatResponse(
            answer=answer,
            should_collect_lead=should_collect_lead_for_message(
                normalized_message,
                "grounded",
            ),
            answer_status="grounded",
            sources=build_sources(relevant_chunks),
        )
    else:
        knowledge_statement = select(KnowledgeItem).where(
            KnowledgeItem.company_id == company.id,
        )

        knowledge_items = list(db.scalars(knowledge_statement).all())

        response = build_chat_response(
            message=normalized_message,
            knowledge_items=knowledge_items,
        )

    response.should_collect_lead = should_collect_lead_for_message(
        normalized_message,
        response.answer_status,
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
