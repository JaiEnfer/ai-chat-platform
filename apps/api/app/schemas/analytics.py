from pydantic import BaseModel


class CompanyAnalyticsRead(BaseModel):
    company_id: int
    total_leads: int
    total_conversation_messages: int
    total_lead_requests: int
    total_knowledge_items: int