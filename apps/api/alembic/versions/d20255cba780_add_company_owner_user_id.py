"""add company owner user id

Revision ID: d20255cba780
Revises: 8d9c4c6f1e2a
Create Date: 2026-06-03 19:09:54.757401

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd20255cba780'
down_revision: Union[str, None] = '8d9c4c6f1e2a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "companies",
        sa.Column("owner_user_id", sa.String(length=255), nullable=True),
    )
    op.execute(
        "UPDATE companies SET owner_user_id = 'legacy-owner' "
        "WHERE owner_user_id IS NULL"
    )
    op.alter_column("companies", "owner_user_id", nullable=False)
    op.create_index(
        op.f("ix_companies_owner_user_id"),
        "companies",
        ["owner_user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_companies_owner_user_id"), table_name="companies")
    op.drop_column("companies", "owner_user_id")
