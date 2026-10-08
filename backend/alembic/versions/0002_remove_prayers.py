"""Remove the retired prayer logging feature."""

from alembic import op

revision = "0002_remove_prayers"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table("prayer_logs")


def downgrade():
    raise NotImplementedError("The prayer logging feature is no longer supported.")
