"""create pricing snapshot change and alert tables

Revision ID: 20260726_01
Revises: m7n8e3f44h6b6
Create Date: 2026-07-26 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260726_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "price_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("competitor_id", sa.Integer(), nullable=False),
        sa.Column("source_url", sa.String(length=1000), nullable=True),
        sa.Column("title", sa.String(length=500), nullable=True),
        sa.Column("currency", sa.String(length=10), nullable=False, server_default="IRR"),
        sa.Column("price", sa.Numeric(18, 2), nullable=False),
        sa.Column("old_price", sa.Numeric(18, 2), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "captured_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["competitor_id"],
            ["competitors.id"],
            name="fk_price_snapshots_competitor_id_competitors",
            ondelete="CASCADE",
        ),
    )
    op.create_index(
        "ix_price_snapshots_competitor_id",
        "price_snapshots",
        ["competitor_id"],
    )
    op.create_index(
        "ix_price_snapshots_captured_at",
        "price_snapshots",
        ["captured_at"],
    )

    op.create_table(
        "price_changes",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("competitor_id", sa.Integer(), nullable=False),
        sa.Column("current_snapshot_id", sa.Integer(), nullable=False),
        sa.Column("previous_snapshot_id", sa.Integer(), nullable=True),
        sa.Column("old_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("new_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("change_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("change_percent", sa.Numeric(12, 2), nullable=True),
        sa.Column("currency", sa.String(length=20), nullable=False, server_default="IRR"),
        sa.Column("change_type", sa.String(length=20), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["competitor_id"],
            ["competitors.id"],
            name="fk_price_changes_competitor_id_competitors",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["current_snapshot_id"],
            ["price_snapshots.id"],
            name="fk_price_changes_current_snapshot_id_price_snapshots",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["previous_snapshot_id"],
            ["price_snapshots.id"],
            name="fk_price_changes_previous_snapshot_id_price_snapshots",
            ondelete="SET NULL",
        ),
        sa.UniqueConstraint(
            "current_snapshot_id",
            name="uq_price_changes_current_snapshot_id",
        ),
    )
    op.create_index(
        "ix_price_changes_competitor_id",
        "price_changes",
        ["competitor_id"],
    )
    op.create_index(
        "ix_price_changes_current_snapshot_id",
        "price_changes",
        ["current_snapshot_id"],
    )
    op.create_index(
        "ix_price_changes_previous_snapshot_id",
        "price_changes",
        ["previous_snapshot_id"],
    )
    op.create_index(
        "ix_price_changes_detected_at",
        "price_changes",
        ["detected_at"],
    )

    op.create_table(
        "alert_logs",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("price_change_id", sa.Integer(), nullable=False),
        sa.Column("channel", sa.String(length=50), nullable=False, server_default="telegram"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["price_change_id"],
            ["price_changes.id"],
            name="fk_alert_logs_price_change_id_price_changes",
            ondelete="CASCADE",
        ),
    )
    op.create_index(
        "ix_alert_logs_price_change_id",
        "alert_logs",
        ["price_change_id"],
    )
    op.create_index(
        "ix_alert_logs_status",
        "alert_logs",
        ["status"],
    )
    op.create_index(
        "ix_alert_logs_created_at",
        "alert_logs",
        ["created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_alert_logs_created_at", table_name="alert_logs")
    op.drop_index("ix_alert_logs_status", table_name="alert_logs")
    op.drop_index("ix_alert_logs_price_change_id", table_name="alert_logs")
    op.drop_table("alert_logs")

    op.drop_index("ix_price_changes_detected_at", table_name="price_changes")
    op.drop_index("ix_price_changes_previous_snapshot_id", table_name="price_changes")
    op.drop_index("ix_price_changes_current_snapshot_id", table_name="price_changes")
    op.drop_index("ix_price_changes_competitor_id", table_name="price_changes")
    op.drop_table("price_changes")

    op.drop_index("ix_price_snapshots_captured_at", table_name="price_snapshots")
    op.drop_index("ix_price_snapshots_competitor_id", table_name="price_snapshots")
    op.drop_table("price_snapshots")
