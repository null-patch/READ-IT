"""add missing message reads media presence

Revision ID: e705945d0f9d
Revises:
Create Date: 2026-10-03 03:03:09.996998

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e705945d0f9d"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create missing message reads, media, and user presence tables."""

    op.create_table(
        "user_presence",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "user_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "online",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "last_seen",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )

    op.create_table(
        "media",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "message_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "uploader_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "media_type",
            sa.Enum(
                "IMAGE",
                "VIDEO",
                "FILE",
                "AUDIO",
                name="media_type",
            ),
            nullable=False,
        ),
        sa.Column(
            "original_name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "stored_name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "mime_type",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "file_size",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "file_path",
            sa.String(length=500),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["message_id"],
            ["messages.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["uploader_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("stored_name"),
    )

    op.create_table(
        "message_reads",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "message_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "read_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["message_id"],
            ["messages.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "message_id",
            "user_id",
            name="uq_message_read",
        ),
    )


def downgrade() -> None:
    """Remove the missing message reads, media, and user presence tables."""

    op.drop_table("message_reads")
    op.drop_table("media")
    op.drop_table("user_presence")
