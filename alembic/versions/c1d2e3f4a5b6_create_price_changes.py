"""create price_changes table

Revision ID: c1d2e3f4a5b6
Revises: 9f8e7d6c5b4a
Create Date: 2026-07-25 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "c1d2e3f4a5b6"
down_revision = "9f8e7d6c5b4a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "price_changes",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("competitor_id", sa.Integer(), nullable=False),
        sa.Column("current_snapshot_id", sa.Integer(), nullable=False),
        sa.Column("previous_snapshot_id", sa.Integer(), nullable=True),
        sa.Column("old_price", sa.Numeric(18, 2), nullable=True),
        sa.Column("new_price", sa.Numeric(18, 2), nullable=False),
        sa.Column("change_amount", sa.Numeric(18, 2), nullable=True),
        sa.Column("change_percent", sa.Numeric(10, 2), nullable=True),
        sa.Column("currency", sa.String(length=10), nullable=False, server_default="IRR"),
        sa.Column("change_type", sa.String(length=20), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["competitor_id"], ["competitors.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["current_snapshot_id"], ["price_snapshots.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["previous_snapshot_id"], ["price_snapshots.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("current_snapshot_id", name="uq_price_changes_current_snapshot_id"),
    )

    op.create_index(op.f("ix_price_changes_id"), "price_changes", ["id"], unique=False)
    op.create_index(op.f("ix_price_changes_competitor_id"), "price_changes", ["competitor_id"], unique=False)
    op.create_index(op.f("ix_price_changes_current_snapshot_id"), "price_changes", ["current_snapshot_id"], unique=False)
    op.create_index(op.f("ix_price_changes_previous_snapshot_id"), "price_changes", ["previous_snapshot_id"], unique=False)
    op.create_index(op.f("ix_price_changes_detected_at"), "price_changes", ["detected_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_price_changes_detected_at"), table_name="price_changes")
    op.drop_index(op.f("ix_price_changes_previous_snapshot_id"), table_name="price_changes")
    op.drop_index(op.f("ix_price_changes_current_snapshot_id"), table_name="price_changes")
    op.drop_index(op.f("ix_price_changes_competitor_id"), table_name="price_changes")
    op.drop_index(op.f("ix_price_changes_id"), table_name="price_changes")
    op.drop_table("price_changes")
