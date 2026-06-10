from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    widget_key: str
    visitor_id: str
    message: str


class ChatSource(BaseModel):
    title: str
    source_type: str
    source_label: str
    source_url: str | None = None
    snippet: str


class ChatResponse(BaseModel):
    answer: str
    should_collect_lead: bool = False
    answer_status: str = "grounded"
    sources: list[ChatSource] = Field(default_factory=list)
