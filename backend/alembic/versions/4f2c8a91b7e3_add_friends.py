"""add friends table

Revision ID: 4f2c8a91b7e3
Revises: e705945d0f9d
Create Date: 2026-10-03
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "4f2c8a91b7e3"
down_revision: Union[str, Sequence[str], None] = "e705945d0f9d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TYPE friend_status AS ENUM (
            'PENDING',
            'ACCEPTED',
            'REJECTED'
        )
        """
    )

    friend_status = postgresql.ENUM(
        "PENDING",
        "ACCEPTED",
        "REJECTED",
        name="friend_status",
        create_type=False,
    )

    op.create_table(
        "friends",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "requester_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "addressee_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "status",
            friend_status,
            nullable=False,
            server_default="PENDING",
        ),
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
        sa.ForeignKeyConstraint(
            ["requester_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["addressee_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "requester_id",
            "addressee_id",
            name="uq_friend_request",
        ),
    )


def downgrade() -> None:
    op.drop_table("friends")

    op.execute(
        """
        DROP TYPE friend_status
        """
    )
