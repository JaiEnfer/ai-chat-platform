from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
import uuid

from app.db.database import Base
from app.models.mixins.timestamp import TimestampMixin


class Company(TimestampMixin, Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)

    owner_user_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    widget_key: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        default=lambda: str(uuid.uuid4()),
    )
    
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    website: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )