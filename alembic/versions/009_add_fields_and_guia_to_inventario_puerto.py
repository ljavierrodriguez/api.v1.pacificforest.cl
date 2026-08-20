"""Add fields and guia_inventario_puerto header to inventario_puerto

Revision ID: 009
Revises: 008
Create Date: 2026-08-13 04:52:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column, select


revision = "009"
down_revision = "008"
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

    # 1. Create table guia_inventario_puerto
    if not _table_exists(bind, "guia_inventario_puerto"):
        op.create_table(
            "guia_inventario_puerto",
            sa.Column("id_guia_inventario_puerto", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("numero_guia", sa.String(length=100), nullable=True),
            sa.Column("oc", sa.String(length=100), nullable=True),
            sa.Column("origen", sa.String(length=100), nullable=True),
            sa.Column("id_orden_servicio", sa.Integer(), sa.ForeignKey("orden_servicio.id_orden_servicio"), nullable=True),
            sa.Column("id_bodega", sa.Integer(), sa.ForeignKey("bodega.id_bodega"), nullable=True),
            sa.Column("fecha_recepcion", sa.Date(), nullable=True),
            sa.Column("url_documento", sa.String(length=500), nullable=True),
            sa.Column("observaciones", sa.String(length=500), nullable=True),
            sa.Column("estado", sa.String(length=50), server_default="RECIBIDO", nullable=True),
        )
        op.create_index(
            "ix_guia_inventario_puerto_numero_guia",
            "guia_inventario_puerto",
            ["numero_guia"],
            unique=False
        )

    # 2. Add new columns to inventario_puerto
    cols_to_add = [
        ("id_guia_inventario_puerto", sa.Column("id_guia_inventario_puerto", sa.Integer(), sa.ForeignKey("guia_inventario_puerto.id_guia_inventario_puerto", ondelete="CASCADE"), nullable=True)),
        ("numero_guia", sa.Column("numero_guia", sa.String(length=100), nullable=True)),
        ("oc", sa.Column("oc", sa.String(length=100), nullable=True)),
        ("origen", sa.Column("origen", sa.String(length=100), nullable=True)),
        ("oc_compra", sa.Column("oc_compra", sa.String(length=100), nullable=True)),
        ("etiqueta", sa.Column("etiqueta", sa.String(length=100), nullable=True)),
        ("numero_paquetes", sa.Column("numero_paquetes", sa.Integer(), nullable=True)),
        ("url_documento", sa.Column("url_documento", sa.String(length=500), nullable=True)),
    ]

    for col_name, col_def in cols_to_add:
        if not _column_exists(bind, "inventario_puerto", col_name):
            op.add_column("inventario_puerto", col_def)


def downgrade() -> None:
    bind = op.get_bind()
    cols = ["url_documento", "numero_paquetes", "etiqueta", "oc_compra", "origen", "oc", "numero_guia", "id_guia_inventario_puerto"]
    for col_name in cols:
        if _column_exists(bind, "inventario_puerto", col_name):
            op.drop_column("inventario_puerto", col_name)

    if _table_exists(bind, "guia_inventario_puerto"):
        op.drop_index("ix_guia_inventario_puerto_numero_guia", table_name="guia_inventario_puerto")
        op.drop_table("guia_inventario_puerto")
