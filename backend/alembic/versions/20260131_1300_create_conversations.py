"""
create conversations table

Revision ID: 20260131_1300
Revises:
Create Date: 2026-01-31 13:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20260131_1300"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ENUM type with IF NOT EXISTS via raw SQL to avoid duplicates
    op.execute(
        "CREATE TYPE conversation_status AS ENUM ('active', 'archived', 'deleted')"
    )

    op.create_table(
        "conversations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM(
                "active",
                "archived",
                "deleted",
                name="conversation_status",
                create_type=False,  # ENUM already created above
            ),
            nullable=False,
            server_default=sa.text("'active'"),
        ),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index(
        "ix_conversations_owner_updated",
        "conversations",
        ["owner_id", sa.text("updated_at DESC")],
    )
    op.create_index(
        "ix_conversations_owner_status",
        "conversations",
        ["owner_id", "status"],
    )


def downgrade() -> None:
    op.drop_index("ix_conversations_owner_status", table_name="conversations")
    op.drop_index("ix_conversations_owner_updated", table_name="conversations")
    op.drop_table("conversations")

    conversation_status = postgresql.ENUM(
        "active",
        "archived",
        "deleted",
        name="conversation_status",
    )
    conversation_status.drop(op.get_bind(), checkfirst=True)
