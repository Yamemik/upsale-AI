"""sales import_extras JSON column

Revision ID: 2c8e9a1b4d00
Revises: f46541cbf198
Create Date: 2026-03-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "2c8e9a1b4d00"
down_revision: Union[str, Sequence[str], None] = "f46541cbf198"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "sales",
        sa.Column("import_extras", sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("sales", "import_extras")
