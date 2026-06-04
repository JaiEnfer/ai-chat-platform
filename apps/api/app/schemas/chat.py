from pydantic import BaseModel, ConfigDict


class ChatRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    widget_key: str
    visitor_id: str
    message: str



class ChatResponse(BaseModel):
    answer: str
    should_collect_lead: bool = False
