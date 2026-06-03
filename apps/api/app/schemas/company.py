from pydantic import BaseModel, HttpUrl
from datetime import datetime


class CompanyCreate(BaseModel):
    owner_user_id: str
    name: str
    website: HttpUrl


class CompanyRead(BaseModel):
    id: int
    name: str
    website: str
    owner_user_id: str
    widget_key: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }
