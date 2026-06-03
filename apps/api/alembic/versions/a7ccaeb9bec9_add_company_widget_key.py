"""add company widget key

Revision ID: a7ccaeb9bec9
Revises: b88ac10ab255
Create Date: 2026-06-03 19:35:34.214783

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a7ccaeb9bec9'
down_revision: Union[str, None] = 'b88ac10ab255'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "companies",
        sa.Column("widget_key", sa.String(length=255), nullable=True),
    )
    op.execute(
        "UPDATE companies "
        "SET widget_key = 'legacy-widget-' || id::text "
        "WHERE widget_key IS NULL"
    )
    op.alter_column("companies", "widget_key", nullable=False)
    op.create_index(
        op.f("ix_companies_widget_key"),
        "companies",
        ["widget_key"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_companies_widget_key"), table_name="companies")
    op.drop_column("companies", "widget_key")
