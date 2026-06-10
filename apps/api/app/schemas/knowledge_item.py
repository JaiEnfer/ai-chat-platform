from pydantic import BaseModel, ConfigDict
from datetime import datetime


class KnowledgeItemCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    company_id: int
    title: str
    content: str


class KnowledgeHtmlCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str
    html_content: str
    source_label: str | None = None


class KnowledgeImportResponse(BaseModel):
    company_id: int
    item_id: int
    title: str
    source: str
    source_type: str
    chunks_created: int


class KnowledgeItemRead(BaseModel):
    id: int
    company_id: int
    title: str
    source_type: str
    source_label: str
    source_url: str | None
    chunk_count: int
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }
