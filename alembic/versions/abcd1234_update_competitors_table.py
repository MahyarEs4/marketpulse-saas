from alembic import op
import sqlalchemy as sa

revision = "abcd1234"
down_revision = "014f22351766"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("competitors", sa.Column("phone", sa.String(length=50), nullable=True))
    op.add_column("competitors", sa.Column("notes", sa.Text(), nullable=True))
    op.add_column("competitors", sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")))
    op.add_column("competitors", sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))


def downgrade() -> None:
    op.drop_column("competitors", "updated_at")
    op.drop_column("competitors", "is_active")
    op.drop_column("competitors", "notes")
    op.drop_column("competitors", "phone")
