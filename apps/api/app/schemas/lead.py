from pydantic import BaseModel, EmailStr
from datetime import datetime


class LeadCreate(BaseModel):
    company_id: int
    name: str
    email: EmailStr
    phone: str | None = None
    message: str | None = None


class LeadRead(BaseModel):
    id: int
    company_id: int
    name: str
    email: str
    phone: str | None
    message: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }