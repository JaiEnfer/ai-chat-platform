from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.company import Company
from app.models.lead import Lead
from app.schemas.lead import LeadCreate, LeadRead

router = APIRouter()


@router.post(
    "/leads",
    response_model=LeadRead,
    status_code=status.HTTP_201_CREATED,
)
def create_lead(
    lead_data: LeadCreate,
    db: Session = Depends(get_db),
) -> Lead:
    company: Company | None = None

    if lead_data.company_id is not None:
        company = db.get(Company, lead_data.company_id)
    elif lead_data.widget_key:
        statement = select(Company).where(Company.widget_key == lead_data.widget_key)
        company = db.scalars(statement).first()
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="company_id or widget_key is required",
        )

    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )

    lead = Lead(
        company_id=company.id,
        name=lead_data.name.strip(),
        email=lead_data.email.lower(),
        phone=lead_data.phone,
        message=lead_data.message,
    )

    db.add(lead)
    db.commit()
    db.refresh(lead)

    return lead


@router.get(
    "/companies/{company_id}/leads",
    response_model=list[LeadRead],
)
def list_company_leads(
    company_id: int,
    db: Session = Depends(get_db),
) -> list[Lead]:
    statement = select(Lead).where(Lead.company_id == company_id)
    leads = db.scalars(statement).all()

    return list(leads)
