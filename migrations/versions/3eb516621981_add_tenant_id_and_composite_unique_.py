"""Add tenant_id and composite unique constraint to UserAccessControl

Revision ID: 3eb516621981
Revises: 041bd9a12737
Create Date: 2025-06-22 17:10:23.859650

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3eb516621981'
down_revision = '041bd9a12737'
branch_labels = None
depends_on = None


def upgrade():
    # Step 1: Add tenant_id as nullable
    with op.batch_alter_table('user_access_controls', schema=None) as batch_op:
        batch_op.add_column(sa.Column('tenant_id', sa.Integer(), nullable=True))
        batch_op.drop_constraint('user_access_controls_user_id_key', type_='unique')
        batch_op.create_foreign_key(None, 'tenants', ['tenant_id'], ['id'])

    # Step 2: Backfill tenant_id for existing rows (assuming master tenant id = 1)
    from sqlalchemy.sql import table, column
    from sqlalchemy import Integer

    user_access_controls = table(
        'user_access_controls',
        column('id', Integer),
        column('tenant_id', Integer)
    )

    op.execute(user_access_controls.update().values(tenant_id=1))

    # Step 3: Set tenant_id to NOT NULL and add composite unique constraint
    with op.batch_alter_table('user_access_controls', schema=None) as batch_op:
        batch_op.alter_column('tenant_id', existing_type=sa.Integer(), nullable=False)
        batch_op.create_unique_constraint('uq_user_per_tenant', ['user_id', 'tenant_id'])


    # ### end Alembic commands ###
