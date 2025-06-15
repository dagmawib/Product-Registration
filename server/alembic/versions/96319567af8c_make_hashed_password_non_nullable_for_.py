"""make_hashed_password_non_nullable_for_users

Revision ID: 96319567af8c
Revises: 322953d1ce4c
Create Date: 2025-06-14 19:23:22.928191

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '96319567af8c'
down_revision: Union[str, None] = '322953d1ce4c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
