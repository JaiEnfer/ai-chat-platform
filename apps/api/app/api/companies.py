from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

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