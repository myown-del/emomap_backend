"""add password reset tokens

Revision ID: 6b7df67fd2f1
Revises: 2aa39afa78d2
Create Date: 2026-02-25 16:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6b7df67fd2f1"
down_revision: Union[str, None] = "2aa39afa78d2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "password_reset_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=4), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("is_used", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_password_reset_tokens_user_active",
        "password_reset_tokens",
        ["user_id", "is_used", "expires_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_password_reset_tokens_user_active", table_name="password_reset_tokens")
    op.drop_table("password_reset_tokens")
