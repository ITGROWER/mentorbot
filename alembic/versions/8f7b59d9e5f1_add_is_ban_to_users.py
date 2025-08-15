"""add is_ban column to users

Revision ID: 8f7b59d9e5f1
Revises: 97fe759d3f3c
Create Date: 2025-02-15 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '8f7b59d9e5f1'
down_revision: Union[str, None] = '97fe759d3f3c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('is_ban', sa.Boolean(), nullable=False, server_default=sa.text('false')))


def downgrade() -> None:
    op.drop_column('users', 'is_ban')
