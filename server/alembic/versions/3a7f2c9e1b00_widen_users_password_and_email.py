"""widen users.hashed_password and email for bcrypt

Revision ID: 3a7f2c9e1b00
Revises: 2c8e9a1b4d00
Create Date: 2026-04-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "3a7f2c9e1b00"
down_revision: Union[str, Sequence[str], None] = "2c8e9a1b4d00"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "users",
        "hashed_password",
        existing_type=sa.String(length=50),
        type_=sa.String(length=255),
        existing_nullable=False,
    )
    op.alter_column(
        "users",
        "email",
        existing_type=sa.String(length=50),
        type_=sa.String(length=255),
        existing_nullable=True,
    )
    op.alter_column(
        "users",
        "login",
        existing_type=sa.String(length=50),
        type_=sa.String(length=128),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "users",
        "login",
        existing_type=sa.String(length=128),
        type_=sa.String(length=50),
        existing_nullable=False,
    )
    op.alter_column(
        "users",
        "email",
        existing_type=sa.String(length=255),
        type_=sa.String(length=50),
        existing_nullable=True,
    )
    op.alter_column(
        "users",
        "hashed_password",
        existing_type=sa.String(length=255),
        type_=sa.String(length=50),
        existing_nullable=False,
    )
