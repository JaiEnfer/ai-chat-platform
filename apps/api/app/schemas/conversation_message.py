from pydantic import BaseModel
from datetime import datetime


class ConversationMessageRead(BaseModel):
    id: int
    company_id: int
    visitor_id: str
    user_message: str
    bot_answer: str
    should_collect_lead: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }