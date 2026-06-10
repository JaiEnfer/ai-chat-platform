"""add knowledge item source metadata

Revision ID: c2b9f6e4a1d8
Revises: 7823267ce4a6
Create Date: 2026-06-10 20:20:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c2b9f6e4a1d8"
down_revision: Union[str, None] = "7823267ce4a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "knowledge_items",
        sa.Column("source_type", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "knowledge_items",
        sa.Column("source_label", sa.String(length=500), nullable=True),
    )
    op.add_column(
        "knowledge_items",
        sa.Column("source_url", sa.String(length=1000), nullable=True),
    )
    op.add_column(
        "knowledge_items",
        sa.Column("chunk_count", sa.Integer(), nullable=True),
    )

    op.execute(
        """
        UPDATE knowledge_items
        SET source_type = CASE
                WHEN title LIKE 'Website:%' THEN 'website'
                ELSE 'manual'
            END,
            source_label = title,
            chunk_count = (
                SELECT COUNT(*)
                FROM knowledge_chunks
                WHERE knowledge_chunks.source LIKE 'knowledge-item:' || knowledge_items.id || ':%'
            )
        """
    )

    op.alter_column("knowledge_items", "source_type", nullable=False)
    op.alter_column("knowledge_items", "source_label", nullable=False)
    op.alter_column("knowledge_items", "chunk_count", nullable=False)


def downgrade() -> None:
    op.drop_column("knowledge_items", "chunk_count")
    op.drop_column("knowledge_items", "source_url")
    op.drop_column("knowledge_items", "source_label")
    op.drop_column("knowledge_items", "source_type")
