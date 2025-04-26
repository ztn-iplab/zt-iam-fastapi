"""Added Tenant model and IAMaaS fields

Revision ID: 770a0b6867c6
Revises: 0cb91047b66d
Create Date: 2025-04-26 13:22:30.370558
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '770a0b6867c6'
down_revision = '0cb91047b66d'
branch_labels = None
depends_on = None


def upgrade():
    # ➡️ 1. Create tenants table
    op.create_table('tenants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('api_key', sa.String(length=64), nullable=False),
        sa.Column('contact_email', sa.String(length=120), nullable=True),
        sa.Column('plan', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('api_key')
    )

    # ➡️ 2. Insert Dummy Tenant
    op.execute("""
        INSERT INTO tenants (id, name, api_key, created_at)
        VALUES (1, 'DummyTenant', 'dummyapikey123456', NOW())
    """)

    # ➡️ 3. OTP Codes
    with op.batch_alter_table('otp_codes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('tenant_id', sa.Integer(), nullable=True))
    op.execute('UPDATE otp_codes SET tenant_id = 1')
    with op.batch_alter_table('otp_codes', schema=None) as batch_op:
        batch_op.alter_column('tenant_id', nullable=False)
        batch_op.create_foreign_key('fk_otp_codes_tenant_id', 'tenants', ['tenant_id'], ['id'])

    # ➡️ 4. Real Time Logs
    with op.batch_alter_table('real_time_logs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('tenant_id', sa.Integer(), nullable=True))
    op.execute('UPDATE real_time_logs SET tenant_id = 1')
    with op.batch_alter_table('real_time_logs', schema=None) as batch_op:
        batch_op.alter_column('tenant_id', nullable=False)
        batch_op.create_foreign_key('fk_real_time_logs_tenant_id', 'tenants', ['tenant_id'], ['id'])

    # ➡️ 5. Transactions
    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('tenant_id', sa.Integer(), nullable=True))
    op.execute('UPDATE transactions SET tenant_id = 1')
    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.alter_column('tenant_id', nullable=False)
        batch_op.create_foreign_key('fk_transactions_tenant_id', 'tenants', ['tenant_id'], ['id'])

    # ➡️ 6. User Auth Logs
    with op.batch_alter_table('user_auth_logs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('tenant_id', sa.Integer(), nullable=True))
    op.execute('UPDATE user_auth_logs SET tenant_id = 1')
    with op.batch_alter_table('user_auth_logs', schema=None) as batch_op:
        batch_op.alter_column('tenant_id', nullable=False)
        batch_op.create_foreign_key('fk_user_auth_logs_tenant_id', 'tenants', ['tenant_id'], ['id'])

    # ➡️ 7. User Roles
    with op.batch_alter_table('user_roles', schema=None) as batch_op:
        batch_op.add_column(sa.Column('tenant_id', sa.Integer(), nullable=True))
    op.execute('UPDATE user_roles SET tenant_id = 1')
    with op.batch_alter_table('user_roles', schema=None) as batch_op:
        batch_op.alter_column('tenant_id', nullable=True)  # Keep nullable because roles can be global
        batch_op.create_foreign_key('fk_user_roles_tenant_id', 'tenants', ['tenant_id'], ['id'])

    # ➡️ 8. Users
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('tenant_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('is_tenant_admin', sa.Boolean(), nullable=True))
    op.execute('UPDATE users SET tenant_id = 1')
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('tenant_id', nullable=False)
        batch_op.create_foreign_key('fk_users_tenant_id', 'tenants', ['tenant_id'], ['id'])



def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint('fk_users_tenant_id', type_='foreignkey')
        batch_op.drop_column('is_tenant_admin')
        batch_op.drop_column('tenant_id')

    with op.batch_alter_table('user_roles', schema=None) as batch_op:
        batch_op.drop_constraint('fk_user_roles_tenant_id', type_='foreignkey')
        batch_op.drop_column('tenant_id')

    with op.batch_alter_table('user_auth_logs', schema=None) as batch_op:
        batch_op.drop_constraint('fk_user_auth_logs_tenant_id', type_='foreignkey')
        batch_op.drop_column('tenant_id')

    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.drop_constraint('fk_transactions_tenant_id', type_='foreignkey')
        batch_op.drop_column('tenant_id')

    with op.batch_alter_table('real_time_logs', schema=None) as batch_op:
        batch_op.drop_constraint('fk_real_time_logs_tenant_id', type_='foreignkey')
        batch_op.drop_column('tenant_id')

    with op.batch_alter_table('otp_codes', schema=None) as batch_op:
        batch_op.drop_constraint('fk_otp_codes_tenant_id', type_='foreignkey')
        batch_op.drop_column('tenant_id')

    op.drop_table('tenants')

