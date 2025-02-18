"""Split full_name into first_name and last_name

Revision ID: 3763bd23be06
Revises: 6c2608b0d6a6
Create Date: 2025-02-17 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '3763bd23be06'
down_revision = '6c2608b0d6a6'
branch_labels = None
depends_on = None

def upgrade():
    # Step 1: Add new columns as nullable
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('first_name', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('last_name', sa.String(length=50), nullable=True))
    
    # Step 2: Populate new columns from full_name
    op.execute(
        """
        UPDATE users
        SET first_name = full_name,
            last_name = ''
        WHERE full_name IS NOT NULL
        """
    )
    
    # Step 3: Alter the new columns to be NOT NULL
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('first_name', nullable=False)
        batch_op.alter_column('last_name', nullable=False)
    
    # Step 4: Drop the old full_name column
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('full_name')

def downgrade():
    # Reverse the changes: add full_name, populate it, then drop first_name and last_name.
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('full_name', sa.String(length=100), nullable=True))
    
    op.execute(
        """
        UPDATE users
        SET full_name = first_name || ' ' || last_name
        """
    )
    
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('full_name', nullable=False)
        batch_op.drop_column('first_name')
        batch_op.drop_column('last_name')

