"""Score snapshots for change tracking.

Revision ID: 005
Create Date: 2026-03-18
"""

from alembic import op
import sqlalchemy as sa

revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "score_snapshots",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("job_id", sa.String(36), nullable=False),
        sa.Column("site_url", sa.String(2048), nullable=False),
        sa.Column("brand", sa.String(200), nullable=False),
        sa.Column("clarity", sa.Integer, server_default="0"),
        sa.Column("audience_fit", sa.Integer, server_default="0"),
        sa.Column("conversion", sa.Integer, server_default="0"),
        sa.Column("seo", sa.Integer, server_default="0"),
        sa.Column("ux", sa.Integer, server_default="0"),
        sa.Column("overall_avg", sa.Integer, server_default="0"),
        sa.Column("snapshot_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_score_snapshots_user_site", "score_snapshots", ["user_id", "site_url", "snapshot_at"])
    op.create_index("ix_score_snapshots_job", "score_snapshots", ["job_id"])


def downgrade() -> None:
    op.drop_table("score_snapshots")
