"""Add id_forma_pago to proforma table

Revision ID: 001
Revises: 
Create Date: 2025-01-06 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add id_forma_pago column to proforma table
    op.add_column('proforma', sa.Column('id_forma_pago', sa.Integer(), nullable=True))
    
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_proforma_forma_pago',  # constraint name
        'proforma',                # source table
        'forma_pago',             # target table
        ['id_forma_pago'],        # source columns
        ['id_forma_pago']         # target columns
    )


def downgrade() -> None:
    # Drop foreign key constraint first
    op.drop_constraint('fk_proforma_forma_pago', 'proforma', type_='foreignkey')
    
    # Drop the column
    op.drop_column('proforma', 'id_forma_pago')