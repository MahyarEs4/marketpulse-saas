"""create price_snapshots table

Revision ID: 9f8e7d6c5b4a
Revises: abcd1234
Create Date: 2026-07-25 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "9f8e7d6c5b4a"
down_revision = "abcd1234"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "price_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("competitor_id", sa.Integer(), nullable=False),
        sa.Column("source_url", sa.String(length=1000), nullable=True),
        sa.Column("title", sa.String(length=500), nullable=True),
        sa.Column("currency", sa.String(length=10), nullable=False, server_default="IRR"),
        sa.Column("price", sa.Numeric(18, 2), nullable=False),
        sa.Column("old_price", sa.Numeric(18, 2), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["competitor_id"], ["competitors.id"], ondelete="CASCADE"),
    )

    op.create_index(op.f("ix_price_snapshots_id"), "price_snapshots", ["id"], unique=False)
    op.create_index(op.f("ix_price_snapshots_competitor_id"), "price_snapshots", ["competitor_id"], unique=False)
    op.create_index(op.f("ix_price_snapshots_captured_at"), "price_snapshots", ["captured_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_price_snapshots_captured_at"), table_name="price_snapshots")
    op.drop_index(op.f("ix_price_snapshots_competitor_id"), table_name="price_snapshots")
    op.drop_index(op.f("ix_price_snapshots_id"), table_name="price_snapshots")
    op.drop_table("price_snapshots")
