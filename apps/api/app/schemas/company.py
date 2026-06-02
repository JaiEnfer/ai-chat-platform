from pydantic import BaseModel, HttpUrl
from datetime import datetime

class CompanyCreate(BaseModel):
    name: str
    website: HttpUrl


class CompanyRead(BaseModel):
    id: int
    name: str
    website: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }