from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.company import Company
from app.models.knowledge_item import KnowledgeItem
from app.schemas.knowledge_item import KnowledgeItemCreate, KnowledgeItemRead

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

    item = KnowledgeItem(
        company_id=item_data.company_id,
        title=item_data.title.strip(),
        content=item_data.content.strip(),
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return item


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

    db.delete(item)
    db.commit()