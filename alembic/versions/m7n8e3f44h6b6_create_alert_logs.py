"""create alert_logs table

Revision ID: m7n8e3f44h6b6
Revises: c1d2e3f4a5b6
Create Date: 2026-07-26 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "m7n8e3f44h6b6"
down_revision = "c1d2e3f4a5b6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "alert_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "price_change_id",
            sa.Integer(),
            sa.ForeignKey("price_changes.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("channel", sa.String(length=50), nullable=False, server_default="telegram"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )

    op.create_index("ix_alert_logs_id", "alert_logs", ["id"])
    op.create_index("ix_alert_logs_price_change_id", "alert_logs", ["price_change_id"])


def downgrade() -> None:
    op.drop_index("ix_alert_logs_price_change_id", table_name="alert_logs")
    op.drop_index("ix_alert_logs_id", table_name="alert_logs")
    op.drop_table("alert_logs")
