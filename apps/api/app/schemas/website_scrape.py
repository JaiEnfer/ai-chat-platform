from pydantic import BaseModel, HttpUrl


class WebsiteScrapeRequest(BaseModel):
    url: HttpUrl


class WebsiteScrapeResponse(BaseModel):
    company_id: int
    source_url: str
    chunks_created: int