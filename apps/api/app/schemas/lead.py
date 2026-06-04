from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime


class LeadCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    widget_key: str | None = None
    name: str
    email: EmailStr
    phone: str | None = None
    message: str | None = None


class LeadRead(BaseModel):
    id: int
    status: str
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

class LeadStatusUpdate(BaseModel):
    status: str
