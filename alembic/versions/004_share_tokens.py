"""Add share tokens for public report links.

Revision ID: 004
Create Date: 2026-03-18
"""

from alembic import op
import sqlalchemy as sa

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("analysis_jobs", sa.Column("share_token", sa.String(64), unique=True, nullable=True))
    op.add_column("analysis_jobs", sa.Column("is_public", sa.Boolean(), server_default="false", nullable=False))
    op.create_index("ix_jobs_share_token", "analysis_jobs", ["share_token"])


def downgrade() -> None:
    op.drop_index("ix_jobs_share_token", "analysis_jobs")
    op.drop_column("analysis_jobs", "is_public")
    op.drop_column("analysis_jobs", "share_token")
