"""Add contacto_orden_servicio table

Revision ID: 004
Revises: 003
Create Date: 2026-05-11 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def _table_exists(bind, table_name: str) -> bool:
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    bind = op.get_bind()
    if _table_exists(bind, "contacto_orden_servicio"):
        return

    if not _table_exists(bind, "contacto") or not _table_exists(bind, "orden_servicio"):
        return

    op.create_table(
        "contacto_orden_servicio",
        sa.Column("id_contacto_orden_servicio", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "id_contacto",
            sa.Integer(),
            sa.ForeignKey("contacto.id_contacto", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "id_orden_servicio",
            sa.Integer(),
            sa.ForeignKey("orden_servicio.id_orden_servicio", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
    )


def downgrade() -> None:
    bind = op.get_bind()
    if _table_exists(bind, "contacto_orden_servicio"):
        op.drop_table("contacto_orden_servicio")

