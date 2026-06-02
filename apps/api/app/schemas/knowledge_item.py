from pydantic import BaseModel
from datetime import datetime

class KnowledgeItemCreate(BaseModel):
    company_id: int
    title: str
    content: str


class KnowledgeItemRead(BaseModel):
    id: int
    company_id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }