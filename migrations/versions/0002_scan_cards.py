"""Persist discovered cards and matched detail URLs."""

import sqlalchemy as sa
from alembic import op

revision = "0002_scan_cards"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "scan_cards",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("scan_run_id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("source_section", sa.String(length=200), nullable=False),
        sa.Column("source_position", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("detail_url", sa.String(length=1000), nullable=False),
        sa.Column("image_url", sa.String(length=1000), nullable=True),
        sa.Column("summary_text", sa.Text(), nullable=True),
        sa.Column("raw_date_text", sa.Text(), nullable=True),
        sa.Column("matched_ip_id", sa.Integer(), nullable=True),
        sa.Column("matched_alias", sa.String(length=200), nullable=True),
        sa.Column("match_field", sa.String(length=50), nullable=True),
        sa.Column("match_score", sa.Float(), nullable=True),
        sa.Column("match_reason", sa.String(length=200), nullable=True),
        sa.Column("detail_status", sa.String(length=30), nullable=False),
        sa.Column("detail_error", sa.Text(), nullable=True),
        sa.Column("discovered_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["scan_run_id"], ["scan_runs.id"]),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"]),
        sa.ForeignKeyConstraint(["matched_ip_id"], ["ip_titles.id"]),
    )
    op.create_index("ix_scan_cards_scan_run_id", "scan_cards", ["scan_run_id"])
    op.create_index("ix_scan_cards_source_id", "scan_cards", ["source_id"])
    op.create_index("ix_scan_cards_matched_ip_id", "scan_cards", ["matched_ip_id"])


def downgrade() -> None:
    op.drop_index("ix_scan_cards_matched_ip_id", table_name="scan_cards")
    op.drop_index("ix_scan_cards_source_id", table_name="scan_cards")
    op.drop_index("ix_scan_cards_scan_run_id", table_name="scan_cards")
    op.drop_table("scan_cards")
