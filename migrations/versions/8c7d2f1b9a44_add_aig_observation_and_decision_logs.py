"""Add AIg observation and decision log tables

Revision ID: 8c7d2f1b9a44
Revises: 4f3a9f2a1c11
Create Date: 2026-02-24 16:20:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "8c7d2f1b9a44"
down_revision = "4f3a9f2a1c11"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "aig_observations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("observed_at", sa.DateTime(), nullable=False),
        sa.Column("ingested_at", sa.DateTime(), nullable=False),
        sa.Column("source_family", sa.String(length=32), nullable=False),
        sa.Column("source_name", sa.String(length=64), nullable=False),
        sa.Column("signal_key", sa.String(length=64), nullable=False),
        sa.Column("evidence_value", sa.Float(), nullable=False),
        sa.Column("weight", sa.Float(), nullable=True),
        sa.Column("reliability", sa.Float(), nullable=True),
        sa.Column("session_id", sa.String(length=128), nullable=True),
        sa.Column("session_label", sa.String(length=64), nullable=True),
        sa.Column("correlation_id", sa.String(length=128), nullable=True),
        sa.Column("experiment_run_id", sa.String(length=64), nullable=True),
        sa.Column("actor_label", sa.String(length=64), nullable=True),
        sa.Column("action_name", sa.String(length=128), nullable=True),
        sa.Column("resource_type", sa.String(length=64), nullable=True),
        sa.Column("resource_id", sa.String(length=128), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_aig_obs_time", "aig_observations", ["observed_at"])
    op.create_index("idx_aig_obs_user_time", "aig_observations", ["user_id", "observed_at"])
    op.create_index("idx_aig_obs_corr", "aig_observations", ["correlation_id"])
    op.create_index("idx_aig_obs_run", "aig_observations", ["experiment_run_id"])
    op.create_index("idx_aig_obs_family_key", "aig_observations", ["source_family", "signal_key"])

    op.create_table(
        "aig_decision_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("decision_time", sa.DateTime(), nullable=False),
        sa.Column("ingested_at", sa.DateTime(), nullable=False),
        sa.Column("action_name", sa.String(length=128), nullable=False),
        sa.Column("action_class", sa.String(length=64), nullable=True),
        sa.Column("resource_type", sa.String(length=64), nullable=True),
        sa.Column("resource_id", sa.String(length=128), nullable=True),
        sa.Column("session_id", sa.String(length=128), nullable=True),
        sa.Column("correlation_id", sa.String(length=128), nullable=True),
        sa.Column("experiment_run_id", sa.String(length=64), nullable=True),
        sa.Column("actor_label", sa.String(length=64), nullable=True),
        sa.Column("c_obs", sa.Float(), nullable=True),
        sa.Column("c_decay", sa.Float(), nullable=True),
        sa.Column("c_value", sa.Float(), nullable=True),
        sa.Column("threshold", sa.Float(), nullable=True),
        sa.Column("alpha", sa.Float(), nullable=True),
        sa.Column("decay_lambda", sa.Float(), nullable=True),
        sa.Column("delta_t_seconds", sa.Float(), nullable=True),
        sa.Column("decision", sa.String(length=32), nullable=False),
        sa.Column("reason", sa.String(length=128), nullable=True),
        sa.Column("step_up_required", sa.Boolean(), nullable=False),
        sa.Column("observation_count", sa.Integer(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_aig_decision_time", "aig_decision_logs", ["decision_time"])
    op.create_index("idx_aig_decision_user_time", "aig_decision_logs", ["user_id", "decision_time"])
    op.create_index("idx_aig_decision_corr", "aig_decision_logs", ["correlation_id"])
    op.create_index("idx_aig_decision_run", "aig_decision_logs", ["experiment_run_id"])
    op.create_index("idx_aig_decision_action", "aig_decision_logs", ["action_name", "decision"])


def downgrade():
    op.drop_index("idx_aig_decision_action", table_name="aig_decision_logs")
    op.drop_index("idx_aig_decision_run", table_name="aig_decision_logs")
    op.drop_index("idx_aig_decision_corr", table_name="aig_decision_logs")
    op.drop_index("idx_aig_decision_user_time", table_name="aig_decision_logs")
    op.drop_index("idx_aig_decision_time", table_name="aig_decision_logs")
    op.drop_table("aig_decision_logs")

    op.drop_index("idx_aig_obs_family_key", table_name="aig_observations")
    op.drop_index("idx_aig_obs_run", table_name="aig_observations")
    op.drop_index("idx_aig_obs_corr", table_name="aig_observations")
    op.drop_index("idx_aig_obs_user_time", table_name="aig_observations")
    op.drop_index("idx_aig_obs_time", table_name="aig_observations")
    op.drop_table("aig_observations")
