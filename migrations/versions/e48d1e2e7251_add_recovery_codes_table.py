"""Add recovery codes table

Revision ID: e48d1e2e7251
Revises: 057e27f089c6, b2f1c7b2a7c1
Create Date: 2025-02-14 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e48d1e2e7251"
down_revision = ("057e27f089c6", "b2f1c7b2a7c1")
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "recovery_codes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("code_hash", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("used_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_recovery_code_lookup",
        "recovery_codes",
        ["user_id", "tenant_id", "code_hash"],
    )


def downgrade():
    op.drop_index("idx_recovery_code_lookup", table_name="recovery_codes")
    op.drop_table("recovery_codes")
