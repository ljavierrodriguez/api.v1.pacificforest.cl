"""Add comision and flete to detalle_orden_compra

Revision ID: 013
Revises: 012
Create Date: 2026-10-05 10:45:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "013"
down_revision = "012"
branch_labels = None
depends_on = None


def _table_exists(bind, table_name: str) -> bool:
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def _column_exists(bind, table_name: str, column_name: str) -> bool:
    inspector = sa.inspect(bind)
    if table_name not in inspector.get_table_names():
        return False
    columns = [c["name"] for c in inspector.get_columns(table_name)]
    return column_name in columns


def upgrade() -> None:
    bind = op.get_bind()

    if _table_exists(bind, "detalle_orden_compra"):
        if not _column_exists(bind, "detalle_orden_compra", "comision"):
            op.add_column(
                "detalle_orden_compra",
                sa.Column("comision", sa.Numeric(precision=12, scale=3), nullable=True, server_default="0"),
            )
        if not _column_exists(bind, "detalle_orden_compra", "flete"):
            op.add_column(
                "detalle_orden_compra",
                sa.Column("flete", sa.Numeric(precision=12, scale=3), nullable=True, server_default="0"),
            )


def downgrade() -> None:
    bind = op.get_bind()

    if _table_exists(bind, "detalle_orden_compra"):
        if _column_exists(bind, "detalle_orden_compra", "flete"):
            op.drop_column("detalle_orden_compra", "flete")
        if _column_exists(bind, "detalle_orden_compra", "comision"):
            op.drop_column("detalle_orden_compra", "comision")
