"""Add resumen general, stock planta and flejes_2da to guia_costo_servicio

Revision ID: 012
Revises: 011
Create Date: 2026-09-17 12:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "012"
down_revision = "011"
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

    if _table_exists(bind, "guia_costo_servicio"):
        if not _column_exists(bind, "guia_costo_servicio", "flejes_2da"):
            op.add_column("guia_costo_servicio", sa.Column("flejes_2da", sa.Numeric(precision=12, scale=4), nullable=True))

    if not _table_exists(bind, "guia_costo_resumen_general"):
        op.create_table(
            "guia_costo_resumen_general",
            sa.Column("id_resumen_general", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column(
                "id_guia_costo_servicio",
                sa.Integer(),
                sa.ForeignKey("guia_costo_servicio.id_guia_costo_servicio", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("oc_tabla", sa.String(length=100), nullable=True),
            sa.Column("movimiento", sa.String(length=100), nullable=True),
            sa.Column("volumen_m3", sa.Numeric(precision=12, scale=4), nullable=True),
            sa.Column("estado", sa.String(length=100), nullable=True),
        )

    if not _table_exists(bind, "guia_costo_stock_planta"):
        op.create_table(
            "guia_costo_stock_planta",
            sa.Column("id_stock_planta", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column(
                "id_guia_costo_servicio",
                sa.Integer(),
                sa.ForeignKey("guia_costo_servicio.id_guia_costo_servicio", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("tipo_stock", sa.String(length=20), nullable=True),
            sa.Column("espesor", sa.Numeric(precision=8, scale=2), nullable=True),
            sa.Column("ancho", sa.Numeric(precision=8, scale=2), nullable=True),
            sa.Column("largo", sa.Numeric(precision=8, scale=2), nullable=True),
            sa.Column("piezas", sa.Integer(), nullable=True),
            sa.Column("volumen_m3", sa.Numeric(precision=12, scale=4), nullable=True),
        )


def downgrade() -> None:
    bind = op.get_bind()

    if _table_exists(bind, "guia_costo_stock_planta"):
        op.drop_table("guia_costo_stock_planta")

    if _table_exists(bind, "guia_costo_resumen_general"):
        op.drop_table("guia_costo_resumen_general")

    if _column_exists(bind, "guia_costo_servicio", "flejes_2da"):
        op.drop_column("guia_costo_servicio", "flejes_2da")
