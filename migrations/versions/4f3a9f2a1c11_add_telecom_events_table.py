"""Add telecom_events table for AIg telecom evidence

Revision ID: 4f3a9f2a1c11
Revises: e48d1e2e7251
Create Date: 2026-02-24 16:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4f3a9f2a1c11"
down_revision = "e48d1e2e7251"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "telecom_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("mobile_number", sa.String(length=20), nullable=True),
        sa.Column("iccid", sa.String(length=32), nullable=True),
        sa.Column("old_iccid", sa.String(length=32), nullable=True),
        sa.Column("new_iccid", sa.String(length=32), nullable=True),
        sa.Column("network_provider", sa.String(length=50), nullable=True),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("event_time", sa.DateTime(), nullable=False),
        sa.Column("ingested_at", sa.DateTime(), nullable=False),
        sa.Column("source_type", sa.String(length=64), nullable=False),
        sa.Column("source_ref", sa.String(length=128), nullable=True),
        sa.Column("source_independent", sa.Boolean(), nullable=False),
        sa.Column("source_confidence", sa.Float(), nullable=True),
        sa.Column("source_weight_hint", sa.Float(), nullable=True),
        sa.Column("correlation_id", sa.String(length=128), nullable=True),
        sa.Column("experiment_run_id", sa.String(length=64), nullable=True),
        sa.Column("actor_label", sa.String(length=64), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("idx_telecom_events_event_time", "telecom_events", ["event_time"])
    op.create_index("idx_telecom_events_user_time", "telecom_events", ["user_id", "event_time"])
    op.create_index("idx_telecom_events_mobile_time", "telecom_events", ["mobile_number", "event_time"])
    op.create_index("idx_telecom_events_corr", "telecom_events", ["correlation_id"])
    op.create_index("idx_telecom_events_type_source", "telecom_events", ["event_type", "source_type"])


def downgrade():
    op.drop_index("idx_telecom_events_type_source", table_name="telecom_events")
    op.drop_index("idx_telecom_events_corr", table_name="telecom_events")
    op.drop_index("idx_telecom_events_mobile_time", table_name="telecom_events")
    op.drop_index("idx_telecom_events_user_time", table_name="telecom_events")
    op.drop_index("idx_telecom_events_event_time", table_name="telecom_events")
    op.drop_table("telecom_events")
