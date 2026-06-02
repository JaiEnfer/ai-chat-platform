from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.company import Company
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