"""Add table detalle_costo_servicio

Revision ID: 011
Revises: 010
Create Date: 2026-08-26 12:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "011"
down_revision = "010"
branch_labels = None
depends_on = None


def _table_exists(bind, table_name: str) -> bool:
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    bind = op.get_bind()

    # Drop old table if created with old schema
    if _table_exists(bind, "detalle_costo_servicio"):
        inspector = sa.inspect(bind)
        cols = [c["name"] for c in inspector.get_columns("detalle_costo_servicio")]
        if "id_guia_costo_servicio" not in cols:
            op.drop_table("detalle_costo_servicio")

    if not _table_exists(bind, "guia_costo_servicio"):
        op.create_table(
            "guia_costo_servicio",
            sa.Column("id_guia_costo_servicio", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("numero_guia", sa.String(length=100), nullable=False),
            sa.Column("fecha_despacho", sa.Date(), nullable=True),
            sa.Column("fecha_registro", sa.Date(), nullable=True),
            sa.Column("origen", sa.String(length=100), nullable=True),
            sa.Column("producto", sa.String(length=100), nullable=True),
            sa.Column("destino", sa.String(length=100), nullable=True),
            sa.Column("oc_compra_ref", sa.String(length=200), nullable=True),
            sa.Column("total_m3", sa.Numeric(precision=12, scale=4), nullable=True),
            sa.Column("total_usd", sa.Numeric(precision=12, scale=2), nullable=True),
            sa.Column("observaciones", sa.Text(), nullable=True),
            sa.Column("url_documento", sa.String(length=500), nullable=True),
        )

    if not _table_exists(bind, "detalle_costo_servicio"):
        op.create_table(
            "detalle_costo_servicio",
            sa.Column("id_detalle_costo_servicio", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column(
                "id_guia_costo_servicio",
                sa.Integer(),
                sa.ForeignKey("guia_costo_servicio.id_guia_costo_servicio", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("servicio", sa.String(length=200), nullable=False),
            sa.Column("volumen_m3", sa.Numeric(precision=12, scale=4), nullable=True),
            sa.Column("tarifa_usd_m3", sa.Numeric(precision=12, scale=4), nullable=True),
            sa.Column("total_usd", sa.Numeric(precision=12, scale=2), nullable=True),
        )

    if not _table_exists(bind, "guia_costo_producto_terminado"):
        op.create_table(
            "guia_costo_producto_terminado",
            sa.Column("id_producto_terminado", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column(
                "id_guia_costo_servicio",
                sa.Integer(),
                sa.ForeignKey("guia_costo_servicio.id_guia_costo_servicio", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("espesor", sa.Numeric(precision=8, scale=2), nullable=True),
            sa.Column("ancho", sa.Numeric(precision=8, scale=2), nullable=True),
            sa.Column("largo", sa.Numeric(precision=8, scale=2), nullable=True),
            sa.Column("piezas", sa.Integer(), nullable=True),
            sa.Column("volumen_m3", sa.Numeric(precision=12, scale=4), nullable=True),
        )

    if not _table_exists(bind, "guia_costo_detalle_proceso"):
        op.create_table(
            "guia_costo_detalle_proceso",
            sa.Column("id_detalle_proceso", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column(
                "id_guia_costo_servicio",
                sa.Integer(),
                sa.ForeignKey("guia_costo_servicio.id_guia_costo_servicio", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("origen_entrada", sa.String(length=100), nullable=True),
            sa.Column("estado_entrada", sa.String(length=100), nullable=True),
            sa.Column("planta_secado", sa.String(length=100), nullable=True),
            sa.Column("planta_cepillado", sa.String(length=100), nullable=True),
            sa.Column("oc_compra_entrada", sa.String(length=100), nullable=True),
            sa.Column("espesor_entrada", sa.Numeric(precision=8, scale=2), nullable=True),
            sa.Column("ancho_entrada", sa.Numeric(precision=8, scale=2), nullable=True),
            sa.Column("largo_entrada", sa.Numeric(precision=8, scale=2), nullable=True),
            sa.Column("piezas_entrada", sa.Integer(), nullable=True),
            sa.Column("volumen_m3_entrada", sa.Numeric(precision=12, scale=4), nullable=True),
            sa.Column("espesor_salida", sa.Numeric(precision=8, scale=2), nullable=True),
            sa.Column("ancho_salida", sa.Numeric(precision=8, scale=2), nullable=True),
            sa.Column("largo_salida", sa.Numeric(precision=8, scale=2), nullable=True),
            sa.Column("piezas_salida", sa.Integer(), nullable=True),
            sa.Column("volumen_m3_salida", sa.Numeric(precision=12, scale=4), nullable=True),
            sa.Column("proceso", sa.String(length=100), nullable=True),
        )

    if not _table_exists(bind, "guia_costo_servicio_os"):
        op.create_table(
            "guia_costo_servicio_os",
            sa.Column("id_guia_costo_servicio", sa.Integer(), sa.ForeignKey("guia_costo_servicio.id_guia_costo_servicio", ondelete="CASCADE"), primary_key=True),
            sa.Column("id_orden_servicio", sa.Integer(), sa.ForeignKey("orden_servicio.id_orden_servicio", ondelete="CASCADE"), primary_key=True),
        )

    if not _table_exists(bind, "guia_costo_servicio_oc"):
        op.create_table(
            "guia_costo_servicio_oc",
            sa.Column("id_guia_costo_servicio", sa.Integer(), sa.ForeignKey("guia_costo_servicio.id_guia_costo_servicio", ondelete="CASCADE"), primary_key=True),
            sa.Column("id_orden_compra", sa.Integer(), sa.ForeignKey("orden_compra.id_orden_compra", ondelete="CASCADE"), primary_key=True),
        )


def downgrade() -> None:
    bind = op.get_bind()

    if _table_exists(bind, "guia_costo_servicio_oc"):
        op.drop_table("guia_costo_servicio_oc")
    if _table_exists(bind, "guia_costo_servicio_os"):
        op.drop_table("guia_costo_servicio_os")
    if _table_exists(bind, "guia_costo_detalle_proceso"):
        op.drop_table("guia_costo_detalle_proceso")
    if _table_exists(bind, "guia_costo_producto_terminado"):
        op.drop_table("guia_costo_producto_terminado")
    if _table_exists(bind, "detalle_costo_servicio"):
        op.drop_table("detalle_costo_servicio")
    if _table_exists(bind, "guia_costo_servicio"):
        op.drop_table("guia_costo_servicio")
