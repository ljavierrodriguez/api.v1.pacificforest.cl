"""Add id_orden_compra and id_detalle_odc to inventario_puerto and guia_inventario_puerto

Revision ID: 010
Revises: 009
Create Date: 2026-08-13 04:58:30.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "010"
down_revision = "009"
branch_labels = None
depends_on = None


def _column_exists(bind, table_name: str, column_name: str) -> bool:
    inspector = sa.inspect(bind)
    return any(col["name"] == column_name for col in inspector.get_columns(table_name))


def upgrade() -> None:
    bind = op.get_bind()

    if not _column_exists(bind, "guia_inventario_puerto", "id_orden_compra"):
        op.add_column("guia_inventario_puerto", sa.Column("id_orden_compra", sa.Integer(), sa.ForeignKey("orden_compra.id_orden_compra"), nullable=True))

    if not _column_exists(bind, "inventario_puerto", "id_orden_compra"):
        op.add_column("inventario_puerto", sa.Column("id_orden_compra", sa.Integer(), sa.ForeignKey("orden_compra.id_orden_compra"), nullable=True))

    if not _column_exists(bind, "inventario_puerto", "id_detalle_odc"):
        op.add_column("inventario_puerto", sa.Column("id_detalle_odc", sa.Integer(), sa.ForeignKey("detalle_orden_compra.id_detalle_odc"), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()

    if _column_exists(bind, "inventario_puerto", "id_detalle_odc"):
        op.drop_column("inventario_puerto", "id_detalle_odc")

    if _column_exists(bind, "inventario_puerto", "id_orden_compra"):
        op.drop_column("inventario_puerto", "id_orden_compra")

    if _column_exists(bind, "guia_inventario_puerto", "id_orden_compra"):
        op.drop_column("guia_inventario_puerto", "id_orden_compra")
