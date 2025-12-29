"""Add device enrollment and login challenges

Revision ID: b2f1c7b2a7c1
Revises: f670358689d2
Create Date: 2025-12-28 13:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2f1c7b2a7c1'
down_revision = 'f670358689d2'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'devices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('device_label', sa.String(length=120), nullable=False),
        sa.Column('platform', sa.String(length=32), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'device_keys',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('device_id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('rp_id', sa.String(length=255), nullable=False),
        sa.Column('key_type', sa.String(length=32), nullable=False),
        sa.Column('public_key', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['device_id'], ['devices.id']),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('device_id', 'rp_id', 'tenant_id', name='uq_device_rp_tenant')
    )
    op.create_table(
        'login_challenges',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('device_id', sa.Integer(), nullable=False),
        sa.Column('rp_id', sa.String(length=255), nullable=False),
        sa.Column('nonce', sa.String(length=255), nullable=False),
        sa.Column('otp_hash', sa.String(length=128), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('denied_reason', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['device_id'], ['devices.id']),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_login_challenges_user_status', 'login_challenges', ['user_id', 'status'])


def downgrade():
    op.drop_index('ix_login_challenges_user_status', table_name='login_challenges')
    op.drop_table('login_challenges')
    op.drop_table('device_keys')
    op.drop_table('devices')
