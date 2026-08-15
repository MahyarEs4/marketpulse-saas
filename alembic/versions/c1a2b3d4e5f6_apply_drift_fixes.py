"""apply drift fixes on competitors and price_changes

Revision ID: c1a2b3d4e5f6
Revises: b07fe40502b9
Create Date: 2025-XX-XX
"""
from alembic import op
import sqlalchemy as sa

revision = 'c1a2b3d4e5f6'
down_revision = 'b07fe40502b9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column('competitors', 'category')

    op.alter_column(
        'price_changes', 'old_price',
        existing_type=sa.Numeric(10, 2), type_=sa.Numeric(12, 2),
        existing_nullable=False,
    )
    op.alter_column(
        'price_changes', 'new_price',
        existing_type=sa.Numeric(10, 2), type_=sa.Numeric(12, 2),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        'price_changes', 'new_price',
        existing_type=sa.Numeric(12, 2), type_=sa.Numeric(10, 2),
        existing_nullable=False,
    )
    op.alter_column(
        'price_changes', 'old_price',
        existing_type=sa.Numeric(12, 2), type_=sa.Numeric(10, 2),
        existing_nullable=False,
    )
    op.add_column('competitors', sa.Column('category', sa.String(100), nullable=True))
