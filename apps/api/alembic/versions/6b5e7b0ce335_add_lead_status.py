"""add lead status

Revision ID: 6b5e7b0ce335
Revises: 0fad1c068609
Create Date: 2026-06-03 23:10:25.352484

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6b5e7b0ce335'
down_revision: Union[str, None] = '0fad1c068609'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("leads", sa.Column("status", sa.String(length=50), nullable=True))
    op.execute("UPDATE leads SET status = 'new' WHERE status IS NULL")
    op.alter_column("leads", "status", existing_type=sa.String(length=50), nullable=False)


def downgrade() -> None:
    op.drop_column("leads", "status")
