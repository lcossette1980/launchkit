"""Add quick_results column for early scan data.

Revision ID: 005
Create Date: 2026-03-18
"""

from alembic import op
import sqlalchemy as sa

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("analysis_jobs", sa.Column("quick_results", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("analysis_jobs", "quick_results")
