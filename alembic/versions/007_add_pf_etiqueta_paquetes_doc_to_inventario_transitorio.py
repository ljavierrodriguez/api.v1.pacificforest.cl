"""Add numero_proforma, etiqueta, numero_paquetes, url_documento to inventario_transitorio

Revision ID: 007
Revises: 006
Create Date: 2026-08-13 03:30:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "007"
down_revision = "006"
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



def upgrade() -> None:
    bind = op.get_bind()
    if not _column_exists(bind, "inventario_transitorio", "numero_proforma"):
        op.add_column(
            "inventario_transitorio",
            sa.Column("numero_proforma", sa.String(length=100), nullable=True)
        )
    if not _column_exists(bind, "inventario_transitorio", "etiqueta"):
        op.add_column(
            "inventario_transitorio",
            sa.Column("etiqueta", sa.String(length=100), nullable=True)
        )
    if not _column_exists(bind, "inventario_transitorio", "numero_paquetes"):
        op.add_column(
            "inventario_transitorio",
            sa.Column("numero_paquetes", sa.Integer(), nullable=True)
        )
    if not _column_exists(bind, "inventario_transitorio", "url_documento"):
        op.add_column(
            "inventario_transitorio",
            sa.Column("url_documento", sa.String(length=500), nullable=True)
        )


def downgrade() -> None:
    bind = op.get_bind()
    if _column_exists(bind, "inventario_transitorio", "url_documento"):
        op.drop_column("inventario_transitorio", "url_documento")
    if _column_exists(bind, "inventario_transitorio", "numero_paquetes"):
        op.drop_column("inventario_transitorio", "numero_paquetes")
    if _column_exists(bind, "inventario_transitorio", "etiqueta"):
        op.drop_column("inventario_transitorio", "etiqueta")
    if _column_exists(bind, "inventario_transitorio", "numero_proforma"):
        op.drop_column("inventario_transitorio", "numero_proforma")
