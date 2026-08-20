"""Normalize inventario_transitorio into header (guia_inventario_transitorio) and detail tables

Revision ID: 008
Revises: 007
Create Date: 2026-08-13 03:41:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column, select


revision = "008"
down_revision = "007"
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

    # 1. Create table guia_inventario_transitorio
    if not _table_exists(bind, "guia_inventario_transitorio"):
        op.create_table(
            "guia_inventario_transitorio",
            sa.Column("id_guia_inventario_transitorio", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("numero_guia", sa.String(length=100), nullable=True),
            sa.Column("numero_proforma", sa.String(length=100), nullable=True),
            sa.Column("id_orden_compra", sa.Integer(), sa.ForeignKey("orden_compra.id_orden_compra"), nullable=True),
            sa.Column("id_bodega", sa.Integer(), sa.ForeignKey("bodega.id_bodega"), nullable=True),
            sa.Column("fecha_recepcion", sa.Date(), nullable=True),
            sa.Column("url_documento", sa.String(length=500), nullable=True),
            sa.Column("observaciones", sa.String(length=500), nullable=True),
            sa.Column("estado", sa.String(length=50), server_default="RECIBIDO", nullable=True),
        )
        op.create_index(
            "ix_guia_inventario_transitorio_numero_guia",
            "guia_inventario_transitorio",
            ["numero_guia"],
            unique=False
        )

    # 2. Add id_guia_inventario_transitorio column to inventario_transitorio
    if not _column_exists(bind, "inventario_transitorio", "id_guia_inventario_transitorio"):
        op.add_column(
            "inventario_transitorio",
            sa.Column(
                "id_guia_inventario_transitorio",
                sa.Integer(),
                sa.ForeignKey("guia_inventario_transitorio.id_guia_inventario_transitorio", ondelete="CASCADE"),
                nullable=True
            )
        )

    # 3. Data Migration: Group existing inventario_transitorio items into guia_inventario_transitorio headers
    if _table_exists(bind, "inventario_transitorio") and _column_exists(bind, "inventario_transitorio", "numero_guia"):
        inv_table = table(
            "inventario_transitorio",
            column("id_inventario_transitorio", sa.Integer),
            column("id_guia_inventario_transitorio", sa.Integer),
            column("numero_guia", sa.String),
            column("numero_proforma", sa.String),
            column("id_orden_compra", sa.Integer),
            column("id_bodega", sa.Integer),
            column("fecha_recepcion", sa.Date),
            column("url_documento", sa.String),
            column("observaciones", sa.String),
            column("estado", sa.String),
        )

        guia_table = table(
            "guia_inventario_transitorio",
            column("id_guia_inventario_transitorio", sa.Integer),
            column("numero_guia", sa.String),
            column("numero_proforma", sa.String),
            column("id_orden_compra", sa.Integer),
            column("id_bodega", sa.Integer),
            column("fecha_recepcion", sa.Date),
            column("url_documento", sa.String),
            column("observaciones", sa.String),
            column("estado", sa.String),
        )

        rows = bind.execute(select(inv_table)).fetchall()
        groups = {}
        for r in rows:
            # Group key by guide, oc, date, bodega
            key = (
                r.numero_guia,
                r.id_orden_compra,
                r.fecha_recepcion,
                r.id_bodega,
                r.numero_proforma,
                r.url_documento,
            )
            if key not in groups:
                groups[key] = []
            groups[key].append(r.id_inventario_transitorio)

        for key, item_ids in groups.items():
            num_guia, id_oc, fecha_rec, id_bodega, num_pf, url_doc = key
            res = bind.execute(
                guia_table.insert()
                .values(
                    numero_guia=num_guia,
                    numero_proforma=num_pf,
                    id_orden_compra=id_oc,
                    id_bodega=id_bodega,
                    fecha_recepcion=fecha_rec,
                    url_documento=url_doc,
                    observaciones=None,
                    estado="RECIBIDO",
                )
                .returning(guia_table.c.id_guia_inventario_transitorio)
            )
            fetched = res.fetchone()
            header_id = fetched[0] if fetched else None
            if header_id and item_ids:
                bind.execute(
                    inv_table.update()
                    .where(inv_table.c.id_inventario_transitorio.in_(item_ids))
                    .values(id_guia_inventario_transitorio=header_id)
                )



def downgrade() -> None:
    bind = op.get_bind()
    if _column_exists(bind, "inventario_transitorio", "id_guia_inventario_transitorio"):
        op.drop_column("inventario_transitorio", "id_guia_inventario_transitorio")
    if _table_exists(bind, "guia_inventario_transitorio"):
        op.drop_index("ix_guia_inventario_transitorio_numero_guia", table_name="guia_inventario_transitorio")
        op.drop_table("guia_inventario_transitorio")
