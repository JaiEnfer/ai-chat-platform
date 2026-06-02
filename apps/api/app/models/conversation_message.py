from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base
from app.models.mixins import TimestampMixin

class ConversationMessage(TimestampMixin, Base):
    __tablename__ = "conversation_messages"

    id: Mapped[int] = mapped_column(primary_key=True)

    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id"),
        nullable=False,
        index=True,
    )

    visitor_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    user_message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    bot_answer: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    should_collect_lead: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
    )