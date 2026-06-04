from pydantic import BaseModel, ConfigDict, HttpUrl
from datetime import datetime


class CompanyCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

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
