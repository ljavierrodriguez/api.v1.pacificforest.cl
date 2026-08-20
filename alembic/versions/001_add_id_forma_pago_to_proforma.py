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


def _table_exists(bind, table_name: str) -> bool:
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def _column_exists(bind, table_name: str, column_name: str) -> bool:
    if not _table_exists(bind, table_name):
        return False
    inspector = sa.inspect(bind)
    return any(col["name"] == column_name for col in inspector.get_columns(table_name))


def _fk_exists(bind, table_name: str, fk_name: str) -> bool:
    if not _table_exists(bind, table_name):
        return False
    inspector = sa.inspect(bind)
    return any(fk.get("name") == fk_name for fk in inspector.get_foreign_keys(table_name))


def upgrade() -> None:
    bind = op.get_bind()
    if _table_exists(bind, "proforma") and not _column_exists(bind, "proforma", "id_forma_pago"):
        op.add_column('proforma', sa.Column('id_forma_pago', sa.Integer(), nullable=True))
        if _table_exists(bind, "forma_pago") and not _fk_exists(bind, "proforma", "fk_proforma_forma_pago"):
            op.create_foreign_key(
                'fk_proforma_forma_pago',  # constraint name
                'proforma',                # source table
                'forma_pago',             # target table
                ['id_forma_pago'],        # source columns
                ['id_forma_pago']         # target columns
            )


def downgrade() -> None:
    bind = op.get_bind()
    if _table_exists(bind, "proforma"):
        if _fk_exists(bind, "proforma", "fk_proforma_forma_pago"):
            op.drop_constraint('fk_proforma_forma_pago', 'proforma', type_='foreignkey')
        if _column_exists(bind, "proforma", "id_forma_pago"):
            op.drop_column('proforma', 'id_forma_pago')