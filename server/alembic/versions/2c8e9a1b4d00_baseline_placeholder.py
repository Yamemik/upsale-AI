"""baseline placeholder revision

Revision ID: 2c8e9a1b4d00
Revises:
Create Date: 2026-04-14
"""

from typing import Sequence, Union


revision: str = "2c8e9a1b4d00"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Placeholder for missing historical revision.
    # Keeps migration graph consistent for current environments.
    pass


def downgrade() -> None:
    pass

