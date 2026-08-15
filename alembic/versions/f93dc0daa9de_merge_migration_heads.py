"""merge migration heads

Revision ID: f93dc0daa9de
Revises: 20260726_01, m7n8e3f44h6b6
Create Date: 2026-07-27 00:10:48.077636

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f93dc0daa9de'
down_revision: Union[str, Sequence[str], None] = ('20260726_01', 'm7n8e3f44h6b6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
