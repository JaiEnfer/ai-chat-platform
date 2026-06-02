from pydantic import BaseModel


class ChatRequest(BaseModel):
    company_id: int
    visitor_id: str
    message: str



class ChatResponse(BaseModel):
    answer: str
    should_collect_lead: bool = False