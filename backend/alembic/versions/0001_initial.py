import sqlalchemy as sa

from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "work_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True)),
        sa.Column(
            "activity",
            sa.Enum(
                "DSA",
                "PROJECT",
                "JOB_APPLICATION",
                "INTERVIEW_PREP",
                "LEARNING",
                "OTHER",
                name="activity",
            ),
            nullable=False,
        ),
        sa.Column("deep_work", sa.Boolean()),
        sa.Column("focus_score", sa.Integer()),
        sa.CheckConstraint(
            "focus_score IS NULL OR focus_score BETWEEN 1 AND 5", name="ck_focus_score"
        ),
    )
    op.create_table(
        "distractions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True)),
        sa.Column(
            "category",
            sa.Enum(
                "YOUTUBE",
                "INSTAGRAM",
                "GAMING",
                "RANDOM_BROWSING",
                "PHONE",
                "OTHER",
                name="distractioncategory",
            ),
            nullable=False,
        ),
    )
    op.create_table(
        "prayer_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column(
            "prayer",
            sa.Enum("FAJR", "DHUHR", "ASR", "MAGHRIB", "ISHA", name="prayer"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("COMPLETED", "MISSED", name="prayerstatus"),
            nullable=False,
        ),
        sa.UniqueConstraint("date", "prayer", name="uq_prayer_date_prayer"),
    )
    op.create_table(
        "sleep_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sleep_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("wake_time", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "career_outputs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("logged_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "type",
            sa.Enum(
                "DSA_PROBLEMS",
                "PROJECT_WORK",
                "APPLICATIONS",
                "INTERVIEW",
                "MOCK_INTERVIEW",
                name="careeroutputtype",
            ),
            nullable=False,
        ),
        sa.Column("count", sa.Integer(), nullable=False),
        sa.Column("note", sa.Text()),
        sa.CheckConstraint("count >= 1", name="ck_career_count"),
    )


def downgrade():
    for table in (
        "career_outputs",
        "sleep_logs",
        "prayer_logs",
        "distractions",
        "work_sessions",
    ):
        op.drop_table(table)
