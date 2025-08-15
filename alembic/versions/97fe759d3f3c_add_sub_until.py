"""add sub_until to users

Revision ID: 97fe759d3f3c
Revises: 3f3d917334a5
Create Date: 2025-02-15 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '97fe759d3f3c'
down_revision: Union[str, None] = '3f3d917334a5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('users', sa.Column('sub_until', sa.DateTime(), nullable=True))

def downgrade() -> None:
    op.drop_column('users', 'sub_until')
